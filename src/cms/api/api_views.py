import logging

# from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from cms.api.serializers import PublicationSerializer, settings

from cms.contexts.decorators import detect_language
from cms.contexts.models import EditorialBoardEditors, WebPath, WebSite
from cms.contexts import settings as contexts_settings

from cms.pages.models import Page

from cms.publications.models import Publication, PublicationContext
from cms.publications.paginators import Paginator
from cms.publications.utils import publication_context_base_filter


CMS_CONTEXT_PERMISSIONS = getattr(settings, 'CMS_CONTEXT_PERMISSIONS',
                                  contexts_settings.CMS_CONTEXT_PERMISSIONS)

logger = logging.getLogger(__name__)


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


@method_decorator(staff_member_required, name='dispatch')
class EditorWebsites(APIView):
    """
    Editor user available active websites
    """
    description = "Get user editorial boards websites"

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
        return Response(websites)


@method_decorator(staff_member_required, name='dispatch')
class EditorWebsiteWebpaths(APIView):
    """
    """
    description = "Get user editorial boards websites webpath list"

    def get(self, request, site_id):
        site = get_object_or_404(WebSite,
                                 pk=site_id,
                                 is_active=True)
        context_permissions = dict(CMS_CONTEXT_PERMISSIONS)
        webpaths = {}

        webpaths_list = WebPath.objects.filter(site=site)
        for webpath in webpaths_list:
            permission = EditorialBoardEditors.get_permission(user=request.user,
                                                              webpath=webpath)
            serialized_webpath = webpath.serialize()
            webpaths[webpath.pk] = serialized_webpath
            webpaths[webpath.pk]["permission_id"] = permission
            webpaths[webpath.pk]["permission_label"] = context_permissions[str(permission)]

        return Response(webpaths)


@method_decorator(staff_member_required, name='dispatch')
class EditorWebsiteWebpath(APIView):
    """
    Editor user get website webpath permissions
    """
    description = "Get user\'s editorial boards websites single webpath"

    def get(self, request, site_id, webpath_id):
        webpath = get_object_or_404(WebPath,
                                    pk=webpath_id,
                                    site__pk=site_id,
                                    site__is_active=True)
        context_permissions = dict(CMS_CONTEXT_PERMISSIONS)
        result = webpath.serialize()

        permission = EditorialBoardEditors.get_permission(webpath, request.user)
        result["permission_id"] = permission
        result["permission_label"] = context_permissions[str(permission)]
        return Response(result)

    def patch(self, request, site_id, webpath_id):
        site = get_object_or_404(WebSite,
                                 pk=site_id,
                                 is_active=True)
        webpath = get_object_or_404(WebPath,
                                    pk=webpath_id,
                                    site=site)
        permission = EditorialBoardEditors.get_permission(webpath=webpath,
                                                          user=request.user)
        publisher_perms = [6,7,8]
        # if user isn't a publisher
        # or can manage only created by him objects and he is not the webpath creator
        if permission not in publisher_perms or (permission == 6 and webpath.created_by != request.user):
            error_msg = _("You don't have permissions")
            return Response(error_msg, status=status.HTTP_403_FORBIDDEN)

        parent_pk = request.data.get('parent', None)
        parent = webpath.parent
        if parent_pk:
            parent = WebPath.objects.filter(pk=parent_pk,
                                            is_active=True,
                                            site=site).first()
            if not parent:
                error_msg = _("Parent not found")
                return Response(error_msg, status=status.HTTP_404_NOT_FOUND)

            permission = EditorialBoardEditors.get_permission(webpath=parent,
                                                              user=request.user)
            if permission not in publisher_perms:
                error_msg = _("You don't have permissions")
                return Response(error_msg, status=status.HTTP_403_FORBIDDEN)

        name = request.data.get('name', webpath.name)

        alias = webpath.alias
        if 'alias' in request.data:
            alias_pk = request.data.get('alias', None)
            if alias_pk:
                alias = WebPath.objects.filter(pk=alias_pk,
                                               is_active=True).first()
                if not alias:
                    error_msg = _("Alias not found")
                    return Response(error_msg, status=status.HTTP_404_NOT_FOUND)
            else:
                alias = None

        alias_url = webpath.alias_url
        if 'alias_url' in request.data:
            alias_url = request.data.get('alias_url', '')

        is_active = webpath.is_active
        if 'is_active' in request.data:
            is_active = request.data.get('is_active', False)

        path = request.data.get('path', webpath.path)
        modified_by = request.user

        webpath.parent = parent
        webpath.name = name
        webpath.alias = alias
        webpath.alias_url = alias_url
        webpath.path = path
        webpath.is_active = is_active
        webpath.modified_by = modified_by
        webpath.save()

        url = reverse('unicms_api:editorial-board-site-webpath-edit',
                      kwargs={'site_id': site_id,
                              'webpath_id': webpath_id})
        return HttpResponseRedirect(url)


@method_decorator(staff_member_required, name='dispatch')
class EditorWebsiteWebpathNew(APIView):
    """
    Editor user get website webpath permissions
    """
    description = ""

    def post(self, request, site_id):
        parent_pk = request.data['parent']
        name = request.data['name']
        alias_pk = request.data.get('alias', None)
        alias_url = request.data.get('alias_url','')
        path = request.data['path']
        created_by = request.user
        is_active = True

        site = get_object_or_404(WebSite,
                                 pk=site_id,
                                 is_active=True)
        parent = WebPath.objects.filter(pk=parent_pk,
                                        is_active=True,
                                        site=site).first()
        if not parent:
            error_msg = _("Parent not found")
            return Response(error_msg, status=status.HTTP_404_NOT_FOUND)

        permission = EditorialBoardEditors.get_permission(webpath=parent,
                                                          user=request.user)
        publisher_perms = [6,7,8]
        if permission not in publisher_perms:
            error_msg = _("You don't have permissions")
            return Response(error_msg, status=status.HTTP_403_FORBIDDEN)

        alias = None
        if alias_pk:
            alias = WebPath.objects.filter(pk=alias_pk,
                                           is_active=True).first()
            if not alias:
                error_msg = _("Alias not found")
                return Response(error_msg, status=status.HTTP_404_NOT_FOUND)

        webpath = WebPath.objects.create(site=site,
                                         name=name,
                                         parent=parent,
                                         alias=alias,
                                         alias_url=alias_url,
                                         path=path,
                                         is_active=is_active,
                                         created_by=created_by,
                                         modified_by=created_by)
        if permission != 8:
            EditorialBoardEditors.objects.create(user=request.user,
                                                 webpath=webpath,
                                                 permission=str(permission),
                                                 is_active=True)
        url = reverse('unicms_api:editorial-board-site-webpath-edit',
                      kwargs={'site_id': site_id,
                              'webpath_id': webpath.pk})
        return HttpResponseRedirect(url)


@method_decorator(staff_member_required, name='dispatch')
class EditorWebsiteWebpathDelete(APIView):
    """
    """
    description = ""

    def get(self, request, site_id, webpath_id):
        webpath = get_object_or_404(WebPath,
                                    pk=webpath_id,
                                    site__pk=site_id,
                                    site__is_active=True,
                                    is_active=True)
        context_permissions = dict(CMS_CONTEXT_PERMISSIONS)
        result = {}
        result['site_name'] = webpath.site.name
        result['site_domain'] = webpath.site.domain
        result['name'] = webpath.name
        result['parent'] = webpath.parent.__str__()
        result['fullpath'] = webpath.fullpath
        permission = EditorialBoardEditors.get_permission(webpath, request.user)
        result['permission'] = permission
        result['verbose'] = context_permissions[str(permission)]
        return Response(result)

    def delete(self, request, site_id, webpath_id):
        site = get_object_or_404(WebSite,
                                 pk=site_id,
                                 is_active=True)
        webpath = get_object_or_404(WebPath,
                                    pk=webpath_id,
                                    is_active=True,
                                    site=site)
        permission = EditorialBoardEditors.get_permission(webpath=webpath,
                                                          user=request.user)
        publisher_perms = [6,7,8]
        if permission not in publisher_perms:
            error_msg = _("You don't have permissions")
            return Response(error_msg, status=status.HTTP_403_FORBIDDEN)

        webpath.delete()

        return Response(_("Webpath deleted successfully"))


@method_decorator(staff_member_required, name='dispatch')
class EditorWebsitePages(APIView):
    """
    """
    description = ""

    def get(self, request, site_id):
        result = {}
        site = get_object_or_404(WebSite,
                                 pk=site_id,
                                 is_active=True)
        result['site_name'] = site.name
        result['site_domain'] = site.domain
        result['pages'] = {}

        lang = getattr(request, 'LANGUAGE_CODE', '')
        pages = {}

        pages_list = Page.objects.filter(webpath__site=site)
        for page in pages_list:
            page.translate_as(lang)
            pages[page.pk] = {"name": page.name,
                              "title": page.title,
                              "webpath": page.webpath.__str__(),
                              "base_template": page.base_template.__str__(),
                              "description": page.description,
                              "date_start": page.date_start,
                              "date_end": page.date_end,
                              "state": page.state,
                              "type": page.type,
                              "tags": [i.slug for i in page.tags.all()],
                              "is_active": page.is_active}
        result['pages'] = pages
        return Response(result)


@method_decorator(staff_member_required, name='dispatch')
class EditorWebsitePage(APIView):
    """
    Editor user get website webpath permissions
    """
    description = "Get user\'s editorial boards websites single webpath"

    def get(self, request, site_id, page_id):
        page = get_object_or_404(Page,
                                 pk=page_id,
                                 webpath__site__pk=site_id,
                                 webpath__site__is_active=True)
        result = {}
        result['site_name'] = page.webpath.site.name
        result['site_domain'] = page.webpath.site.domain
        result['name'] = page.name
        result['title'] = page.title
        result['webpath'] = page.webpath.__str__()
        result['base_template'] = page.base_template.__str__()
        result['description'] = page.description
        result['date_start'] = page.date_start
        result['date_end'] = page.date_end
        result['state'] = page.state
        result['type'] = page.type
        result['tags'] = [i.slug for i in page.tags.all()]
        result['is_active'] = page.is_active
        return Response(result)
