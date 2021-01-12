import logging
import os

# from django.contrib.auth.decorators import login_required
# from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _

from rest_framework import generics, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (BasePermission,
                                        IsAdminUser,
                                        SAFE_METHODS)
from rest_framework.response import Response
from rest_framework.views import APIView

from cms.api.serializers import PublicationSerializer, settings

from cms.contexts.decorators import detect_language
from cms.contexts.models import EditorialBoardEditors, WebPath, WebSite
from cms.contexts.serializers import WebPathSerializer
from cms.contexts import settings as contexts_settings

from cms.medias.models import Media
from cms.medias.serializers import MediaSerializer

from cms.publications.models import Publication, PublicationContext
from cms.publications.paginators import Paginator
from cms.publications.utils import publication_context_base_filter

from . utils import check_user_permission_on_object


CMS_CONTEXT_PERMISSIONS = getattr(settings, 'CMS_CONTEXT_PERMISSIONS',
                                  contexts_settings.CMS_CONTEXT_PERMISSIONS)

logger = logging.getLogger(__name__)


class UniCmsApiPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 250


# TODO - better get with filters
class PublicationDetail(generics.RetrieveAPIView):
    name = 'publication-detail'
    description = 'News'
    queryset = Publication.objects.filter(is_active=True,
                                          state='published')
    serializer_class = PublicationSerializer
    lookup_field = 'slug'

    def get_queryset(self):
        self.request.user
        for pub in super(PublicationDetail, self).get_queryset():
            if pub.is_publicable:
                return pub


@method_decorator(detect_language, name='dispatch')
class ApiPublicationsByContext(APIView):
    """
    """
    description = 'ApiPublicationsByContext'
    # authentication_classes = [authentication.TokenAuthentication]
    # permission_classes = [permissions.IsAdminUser]

    def get(self, request, webpath_id, category_name=None):
        query_params = publication_context_base_filter()
        query_params.update({'webpath__pk': webpath_id,
                             'publication__state': 'published'})

        category_name = category_name or request.GET.get('category_name')
        if category_name:
            query_params['publication__category__name__iexact'] = category_name
        pubcontx = PublicationContext.objects.filter(**query_params)
        paginator = Paginator(queryset=pubcontx, request=request)

        try:
            page_num = int(request.GET.get('page_number', 1))
        except Exception as e: # pragma: no cover
            logger.error(f'API {self.__class__.__name__} paginator number: {e}')
            raise ValidationError('Wrong page_number value')

        paged = paginator.get_page(page_num)
        result = paged.serialize()
        return Response(result)


@method_decorator(detect_language, name='dispatch')
class ApiContext(APIView): # pragma: no cover
    """
    """
    description = 'Get publications in Context (WebPath)'

    def get(self, request):
        webpaths = WebPath.objects.filter(is_active=True)
        pubs = ({i.pk: f'{i.site.domain}{i.get_full_path()}'}
                for i in webpaths if i.is_publicable)
        return Response(pubs)


# @method_decorator(staff_member_required, name='dispatch')
class EditorWebsiteList(APIView, UniCmsApiPagination):
    """
    Editor user available active websites
    """
    description = "Get user editorial boards websites"
    permission_classes = [IsAdminUser]

    def get(self, request):
        permissions = EditorialBoardEditors.objects.filter(user=request.user,
                                                           is_active=True)
        websites = []
        for permission in permissions:
            webpath = permission.webpath
            # can access to all active websites
            if not webpath:
                websites = []
                sites = WebSite.objects.filter(is_active=True)
                for site in sites:
                    websites.append(site.serialize())
                break
            # can access to active webpath' websites
            permissions = permissions.filter(webpath__is_active=True,
                                             webpath__site__is_active=True)
            site = permission.webpath.site
            serialized_site = site.serialize()
            if serialized_site not in websites:
                websites.append(serialized_site)
        results = self.paginate_queryset(websites, request, view=self)
        return self.get_paginated_response(results)


# @method_decorator(staff_member_required, name='dispatch')
class EditorWebsiteWebpathList(generics.ListCreateAPIView):
    """
    """
    description = "Get user editorial boards websites webpath list"
    pagination_class = UniCmsApiPagination
    permission_classes = [IsAdminUser]
    serializer_class = WebPathSerializer

    def get_queryset(self):
        """
        """
        site_id = self.kwargs['site_id']
        site = get_object_or_404(WebSite, pk=site_id, is_active=True)
        webpaths = WebPath.objects.filter(site=site)
        return webpaths

    def get(self, request, *args, **kwargs):
        webpaths_list = self.get_queryset()
        context_permissions = dict(CMS_CONTEXT_PERMISSIONS)
        webpaths = []

        for webpath in webpaths_list:
            permission = EditorialBoardEditors.get_permission(user=request.user,
                                                              webpath=webpath)
            serialized_webpath = WebPathSerializer(webpath).data
            serialized_webpath["permission_id"] = permission
            permission_label = context_permissions[permission] if permission else ''
            serialized_webpath["permission_label"] = permission_label
            webpaths.append(serialized_webpath)
        results = self.paginate_queryset(webpaths)
        return self.get_paginated_response(results)

    def post(self, request, *args, **kwargs):
        # site in url kwargs
        site_id = kwargs['site_id']
        site = get_object_or_404(WebSite,
                                 pk=site_id,
                                 is_active=True)

        # site in request.data
        site_pk = request.data.get('site', None)
        if not site_pk or int(site_pk) != site_id:
            error_msg = _("Site must be {}").format(site)
            return Response(error_msg, status=status.HTTP_404_NOT_FOUND)

        # parent in request data
        parent_pk = request.data.get('parent',None)
        if not parent_pk:
            error_msg = _("Parent empty")
            return Response(error_msg, status=status.HTTP_404_NOT_FOUND)

        # get active parent
        parent = WebPath.objects.filter(pk=int(parent_pk),
                                        site=site).first()
        if not parent:
            error_msg = _("Parent not found")
            return Response(error_msg, status=status.HTTP_404_NOT_FOUND)

        # check permissions on parent
        permission = EditorialBoardEditors.get_permission(webpath=parent,
                                                          user=request.user)
        publisher_perms = [6,7,8]
        if permission not in publisher_perms or (permission == 6 and parent.created_by != request.user):
            error_msg = _("You don't have permissions")
            return Response(error_msg, status=status.HTTP_403_FORBIDDEN)

        serializer = WebPathSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            webpath = serializer.save()
            webpath.created_by = request.user
            webpath.modified_by = request.user
            webpath.save()
            # add permission to webpath
            if permission != 8:
                EditorialBoardEditors.objects.create(user=request.user,
                                                     webpath=webpath,
                                                     permission=permission,
                                                     is_active=True)
            url = reverse('unicms_api:editorial-board-site-webpath-view',
                          kwargs={'site_id': site_id,
                                  'pk': webpath.pk})
            return HttpResponseRedirect(url)


# @method_decorator(staff_member_required, name='dispatch')
class EditorWebsiteWebpathView(generics.RetrieveUpdateDestroyAPIView):
    """
    Editor user get website webpath permissions
    """
    description = "Get user\'s editorial boards websites single webpath"
    permission_classes = [IsAdminUser]
    serializer_class = WebPathSerializer

    def get_queryset(self):
        """
        """
        site_id = self.kwargs['site_id']
        pk = self.kwargs['pk']
        site = get_object_or_404(WebSite, pk=site_id, is_active=True)
        webpath = get_object_or_404(WebPath, pk=pk, site=site)
        return webpath

    def get(self, request, *args, **kwargs):
        context_permissions = dict(CMS_CONTEXT_PERMISSIONS)
        webpath = self.get_queryset()
        result = WebPathSerializer(webpath).data
        permission = EditorialBoardEditors.get_permission(webpath, request.user)
        result["permission_id"] = permission
        webpath_permission = context_permissions[permission] if permission else None
        result["permission_label"] = webpath_permission
        return Response(result)

    def patch(self, request, *args, **kwargs):
        error_msg = _("Method not allowed. Use put instead")
        return Response(error_msg, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def put(self, request, *args, **kwargs):
        dict(CMS_CONTEXT_PERMISSIONS)
        site_id = kwargs['site_id']
        webpath = self.get_queryset()
        permission = EditorialBoardEditors.get_permission(webpath=webpath,
                                                          user=request.user)
        publisher_perms = [6,7,8]
        # if user isn't a publisher
        # or can manage only created by him objects and he is not the webpath creator
        if permission not in publisher_perms or (permission == 6 and webpath.created_by != request.user):
            error_msg = _("You don't have permissions on webpath {}").format(webpath)
            return Response(error_msg, status=status.HTTP_403_FORBIDDEN)

        # site in request.data
        site_pk = request.data['site']
        if site_pk != site_id:
            error_msg = _("Site must be {}").format(webpath.site)
            return Response(error_msg, status=status.HTTP_404_NOT_FOUND)

        # parent in request data
        parent_pk = request.data.get('parent',None)
        if not parent_pk:
            error_msg = _("Parent empty")
            return Response(error_msg, status=status.HTTP_404_NOT_FOUND)

        # get active parent
        parent = WebPath.objects.filter(pk=parent_pk,
                                        site=webpath.site).first()
        if not parent:
            error_msg = _("Parent not found")
            return Response(error_msg, status=status.HTTP_404_NOT_FOUND)

        # check permissions on parent
        parent_permission = EditorialBoardEditors.get_permission(webpath=parent,
                                                                 user=request.user)
        if parent_permission not in publisher_perms or (parent_permission == 6 and parent.created_by != request.user):
            error_msg = _("You don't have permissions on webpath {}").format(parent)
            return Response(error_msg, status=status.HTTP_403_FORBIDDEN)

        serializer = WebPathSerializer(instance=webpath,
                                       data=request.data)
        if serializer.is_valid(raise_exception=True):
            webpath = serializer.save()
            webpath.modified_by = request.user
            webpath.save()
            url = reverse('unicms_api:editorial-board-site-webpath-view',
                          kwargs={'site_id': site_id,
                                  'pk': webpath.pk})
            return HttpResponseRedirect(url)

    def delete(self, request, site_id, pk):
        site = get_object_or_404(WebSite,
                                 pk=site_id,
                                 is_active=True)
        webpath = get_object_or_404(WebPath,
                                    pk=pk,
                                    site=site)
        permission = EditorialBoardEditors.get_permission(webpath=webpath,
                                                          user=request.user)
        publisher_perms = [6,7,8]
        if permission not in publisher_perms or (permission == 6 and webpath.created_by != request.user):
            error_msg = _("You don't have permissions on webpath {}").format(webpath)
            return Response(error_msg, status=status.HTTP_403_FORBIDDEN)

        webpath.delete()
        return Response(_("Webpath deleted successfully"))


class UserCanAddMediaOrAdminReadonly(BasePermission):
    """
    """

    def has_permission(self, request, view):
        user = request.user
        if user.is_superuser and user.is_staff: return True
        if not user.is_staff: return False
        if request.method in SAFE_METHODS: return True
        return user.has_perm('cmsmedias.add_media')


class MediaList(generics.ListCreateAPIView):
    """
    """
    description = ""
    pagination_class = UniCmsApiPagination
    permission_classes = [UserCanAddMediaOrAdminReadonly]
    serializer_class = MediaSerializer
    queryset = Media.objects.filter(is_active=True)


class MediaView(generics.RetrieveUpdateDestroyAPIView):
    """
    """
    description = ""
    permission_classes = [IsAdminUser]
    serializer_class = MediaSerializer

    def get_queryset(self):
        """
        """
        media_id = self.kwargs['pk']
        media = Media.objects.filter(pk=media_id)
        return media

    def patch(self, request, *args, **kwargs):
        permission = check_user_permission_on_object(request.user,
                                                     self.get_queryset().first(),
                                                     'cmsmedias.change_media')
        if not permission:
            error_msg = _("You don't have permissions")
            return Response(error_msg, status=status.HTTP_403_FORBIDDEN)
        return super().patch(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        permission = check_user_permission_on_object(request.user,
                                                     self.get_queryset().first(),
                                                     'cmsmedias.change_media')
        if not permission:
            error_msg = _("You don't have permissions")
            return Response(error_msg, status=status.HTTP_403_FORBIDDEN)
        return super().put(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        permission = check_user_permission_on_object(request.user,
                                                     self.get_queryset().first(),
                                                     'cmsmedias.delete_media')
        if not permission:
            error_msg = _("You don't have permissions")
            return Response(error_msg, status=status.HTTP_403_FORBIDDEN)
        media = self.get_queryset().first()
        os.remove(media.file.path)
        return super().delete(request, *args, **kwargs)


# @method_decorator(staff_member_required, name='dispatch')
# class EditorWebsitePages(APIView):
    # """
    # """
    # description = ""

    # def get(self, request, site_id):
        # result = {}
        # site = get_object_or_404(WebSite,
        # pk=site_id,
        # is_active=True)
        # result['site_name'] = site.name
        # result['site_domain'] = site.domain
        # result['pages'] = {}

        # lang = getattr(request, 'LANGUAGE_CODE', '')
        # pages = {}

        # pages_list = Page.objects.filter(webpath__site=site)
        # for page in pages_list:
        # page.translate_as(lang)
        # pages[page.pk] = {"name": page.name,
        # "title": page.title,
        # "webpath": page.webpath.__str__(),
        # "base_template": page.base_template.__str__(),
        # "description": page.description,
        # "date_start": page.date_start,
        # "date_end": page.date_end,
        # "state": page.state,
        # "type": page.type,
        # "tags": [i.slug for i in page.tags.all()],
        # "is_active": page.is_active}
        # result['pages'] = pages
        # return Response(result)


# @method_decorator(staff_member_required, name='dispatch')
# class EditorWebsitePage(APIView):
    # """
    # Editor user get website webpath permissions
    # """
    # description = "Get user\'s editorial boards websites single webpath"

    # def get(self, request, site_id, page_id):
        # page = get_object_or_404(Page,
        # pk=page_id,
        # webpath__site__pk=site_id,
        # webpath__site__is_active=True)
        # result = {}
        # result['site_name'] = page.webpath.site.name
        # result['site_domain'] = page.webpath.site.domain
        # result['name'] = page.name
        # result['title'] = page.title
        # result['webpath'] = page.webpath.__str__()
        # result['base_template'] = page.base_template.__str__()
        # result['description'] = page.description
        # result['date_start'] = page.date_start
        # result['date_end'] = page.date_end
        # result['state'] = page.state
        # result['type'] = page.type
        # result['tags'] = [i.slug for i in page.tags.all()]
        # result['is_active'] = page.is_active
        # return Response(result)
