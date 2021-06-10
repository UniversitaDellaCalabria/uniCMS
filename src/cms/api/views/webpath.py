from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import filters, generics
from rest_framework.permissions import IsAdminUser
from rest_framework.schemas.openapi import AutoSchema

from cms.contexts import settings as contexts_settings
from cms.contexts.forms import WebPathForm, WebPathCloneForm
from cms.contexts.models import EditorialBoardEditors, EditorialBoardLockUser, WebPath, WebSite
from cms.contexts.serializers import WebPathSerializer, WebPathSelectOptionsSerializer
from cms.contexts.utils import clone, is_publisher

from rest_framework.response import Response
from rest_framework.views import APIView

from . generics import UniCMSCachedRetrieveUpdateDestroyAPIView, UniCMSListCreateAPIView, UniCMSListSelectOptionsAPIView
from . logs import ObjectLogEntriesList
from .. exceptions import LoggedPermissionDenied, LoggedValidationException
from .. pagination import UniCmsApiPagination
from .. serializers import UniCMSFormSerializer


CMS_CONTEXT_PERMISSIONS = getattr(settings, 'CMS_CONTEXT_PERMISSIONS',
                                  contexts_settings.CMS_CONTEXT_PERMISSIONS)


class WebpathList(UniCMSListCreateAPIView):
    """
    """
    name = "Webpaths"
    description = "Get user editorial boards websites webpath list"
    serializer_class = WebPathSerializer
    search_fields = ['name','fullpath']

    def get_queryset(self):
        """
        """
        site_id = self.kwargs.get('site_id')
        if site_id:
            site = get_object_or_404(WebSite, pk=site_id, is_active=True)
            if not site.is_managed_by(self.request.user):
                raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                             resource=site)
            return WebPath.objects.filter(site=site)
        return WebPath.objects.none() # pragma: no cover

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            # get parent
            parent = serializer.validated_data.get('parent')
            # check permissions on parent
            permission = EditorialBoardEditors.get_permission(webpath=parent,
                                                              user=request.user)
            publisher_perms = is_publisher(permission)
            parent_locks_ok = EditorialBoardLockUser.check_for_locks(parent,
                                                                     request.user)
            if not publisher_perms or not parent_locks_ok:
                raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                             resource=request.method)
            try:
                webpath = serializer.save()
            except Exception as e:
                raise LoggedValidationException(classname=self.__class__.__name__,
                                                resource=request.method,
                                                detail=e)
            # add permission to webpath
            if not publisher_perms['allow_descendant']:
                EditorialBoardEditors.objects.create(user=request.user,
                                                     webpath=webpath,
                                                     permission=permission,
                                                     is_active=True)
            url = reverse('unicms_api:editorial-board-site-webpath',
                          kwargs={'site_id': webpath.site.pk,
                                  'pk': webpath.pk})
            return HttpResponseRedirect(url)


class WebpathView(UniCMSCachedRetrieveUpdateDestroyAPIView):
    """
    Editor user get website webpath permissions
    """
    name = "Webpath"
    description = "Get user\'s editorial boards websites single webpath"
    permission_classes = [IsAdminUser]
    serializer_class = WebPathSerializer

    def get_queryset(self):
        """
        """
        site_id = self.kwargs['site_id']
        pk = self.kwargs['pk']
        site = get_object_or_404(WebSite, pk=site_id, is_active=True)
        if not site.is_managed_by(self.request.user):
            raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                         resource=site)
        return WebPath.objects.filter(pk=pk, site=site)

    def patch(self, request, *args, **kwargs):
        item = self.get_queryset().first()
        if not item: raise Http404

        serializer = self.get_serializer(instance=item,
                                         data=request.data,
                                         partial=True)
        if serializer.is_valid(raise_exception=True):
            has_permission = item.is_publicable_by(user=request.user,
                                                   parent=True)
            if not has_permission:
                raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                             resource=request.method)
            # if parent in request data, check permission on parent
            parent = serializer.validated_data.get('parent')
            if parent and parent != item.parent:
                # check permissions on parent
                has_permission = parent.is_publicable_by(user=request.user,
                                                         parent=True)
                if not has_permission:
                    raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                                 resource=request.method)
            try:
                return super().patch(request, *args, **kwargs)
            except Exception as e:
                raise LoggedValidationException(classname=self.__class__.__name__,
                                                resource=request.method,
                                                detail=e)

    def put(self, request, *args, **kwargs):
        item = self.get_queryset().first()
        if not item: raise Http404

        serializer = self.get_serializer(instance=item,
                                         data=request.data)
        if serializer.is_valid(raise_exception=True):
            has_permission = item.is_publicable_by(user=request.user,
                                                   parent=True)
            if not has_permission:
                raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                             resource=request.method)

            parent = serializer.validated_data.get('parent')
            # check permissions on parent if different from actual
            if parent != item.parent:
                has_permission = parent.is_publicable_by(user=request.user,
                                                         parent=True)
                if not has_permission:
                    raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                                 resource=request.method)
            try:
                return super().put(request, *args, **kwargs)
            except Exception as e:
                raise LoggedValidationException(classname=self.__class__.__name__,
                                                resource=request.method,
                                                detail=e)

    def delete(self, request, *args, **kwargs):
        item = self.get_queryset().first()
        if not item: raise Http404
        has_permission = item.is_publicable_by(user=request.user,
                                               parent=True)
        if not has_permission:
            raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                         resource=request.method)
        return super().delete(request, *args, **kwargs)


class WebpathFormView(APIView):
    def get(self, *args, **kwargs):
        form = WebPathForm(site_id=kwargs.get('site_id'))
        form_fields = UniCMSFormSerializer.serialize(form)
        return Response(form_fields)


class EditorialBoardWebpathOptionListSchema(AutoSchema):
    def get_operation_id(self, path, method):# pragma: no cover
        return 'listWebPathSelectOptions'


class WebpathOptionList(UniCMSListSelectOptionsAPIView):
    """
    """
    description = ""
    search_fields = ['name','path']
    serializer_class = WebPathSelectOptionsSerializer
    queryset = WebPath.objects.all()
    schema = EditorialBoardWebpathOptionListSchema()

    def get_queryset(self):
        """
        """
        site_id = self.kwargs.get('site_id')
        if site_id:
            site = get_object_or_404(WebSite, pk=site_id, is_active=True)
            if not site.is_managed_by(self.request.user):
                raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                             resource=site)
            return WebPath.objects.filter(site=site)
        return WebPath.objects.none()# pragma: no cover


class EditorialBoardWebpathAllOptionListSchema(AutoSchema):
    def get_operation_id(self, path, method):# pragma: no cover
        return 'listWebPathAllSelectOptions'


class WebpathAllOptionList(UniCMSListSelectOptionsAPIView):
    """
    """
    description = ""
    search_fields = ['name','path']
    serializer_class = WebPathSelectOptionsSerializer
    queryset = WebPath.objects.all()
    schema = EditorialBoardWebpathAllOptionListSchema()


class WebpathOptionView(generics.RetrieveAPIView):
    """
    """
    description = ""
    permission_classes = [IsAdminUser]
    serializer_class = WebPathSelectOptionsSerializer

    def get_queryset(self):
        """
        """
        site_id = self.kwargs['site_id']
        pk = self.kwargs['pk']
        site = get_object_or_404(WebSite, pk=site_id, is_active=True)
        if not site.is_managed_by(self.request.user):
            raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                         resource=site)
        return WebPath.objects.filter(pk=pk, site=site)


class WebpathLogsSchema(AutoSchema):
    def get_operation_id(self, path, method):# pragma: no cover
        return 'listWebPathLogs'


class WebpathLogsView(ObjectLogEntriesList):

    schema = WebpathLogsSchema()

    def get_queryset(self, **kwargs):
        """
        """
        site_id = self.kwargs['site_id']
        object_id = self.kwargs['pk']
        site = get_object_or_404(WebSite, pk=site_id, is_active=True)
        if not site.is_managed_by(self.request.user):
            raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                         resource=site)
        item = get_object_or_404(WebPath.objects.select_related('site'),
                                 pk=object_id,
                                 site=site)
        content_type_id = ContentType.objects.get_for_model(item).pk
        return super().get_queryset(object_id, content_type_id)


class EditorialBoardWebpathAllListSchema(AutoSchema):
    def get_operation_id(self, path, method):# pragma: no cover
        return 'listWebPathAll'


class WebpathAllList(generics.ListAPIView):
    """
    """
    description = ""
    serializer_class = WebPathSerializer
    queryset = WebPath.objects.all()
    schema = EditorialBoardWebpathAllListSchema()
    permission_classes = [IsAdminUser]
    filter_backends = [filters.SearchFilter,
                       DjangoFilterBackend,
                       filters.OrderingFilter]
    filterset_fields = ['is_active', 'created', 'modified', 'created_by']
    pagination_class = UniCmsApiPagination


class WebpathCloneFormView(APIView):
    def get(self, *args, **kwargs):
        form = WebPathCloneForm()
        form_fields = UniCMSFormSerializer.serialize(form)
        return Response(form_fields)


class WebpathCloneSchema(AutoSchema):
    def get_operation_id(self, path, method):# pragma: no cover
        return 'cloneWebPath'

    def get_operation(self, path, method): # pragma: no cover
        op = super().get_operation(path, method)
        op['parameters'].append(
            {
                "name": "parent",
                "in": "form",
                "required": True,
                "description": "Destination webpath",
                'schema': {'type': 'integer'}
            }
        )
        op['parameters'].append(
            {
                "name": "exclude_pages",
                "in": "form",
                "required": False,
                "description": "If true exclude webpath pages from cloning",
                'schema': {'type': 'boolean'}
            }
        )
        op['parameters'].append(
            {
                "name": "exclude_news",
                "in": "form",
                "required": False,
                "description": "If true exclude webpath news from cloning",
                'schema': {'type': 'boolean'}
            }
        )
        op['parameters'].append(
            {
                "name": "only_childs",
                "in": "form",
                "required": False,
                "description": "If true only webpath childs are cloned",
                'schema': {'type': 'boolean'}
            }
        )
        return op


class WebpathCloneView(APIView):

    schema = WebpathCloneSchema()
    description = ""
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        """
        """
        site_id = self.kwargs['site_id']
        pk = self.kwargs['pk']
        site = get_object_or_404(WebSite, pk=site_id, is_active=True)
        return WebPath.objects.filter(pk=pk, site=site)

    def post(self, request, *args, **kwargs):
        item = self.get_queryset().first()
        if not item: raise Http404

        # get POST data
        parent_id = request.data.get('parent', None)
        exclude_pages = request.data.get('exclude_pages', 0)
        exclude_news = request.data.get('exclude_news', 0)
        only_childs = request.data.get('only_childs', 0)

        if not parent_id:
            raise Http404

        # check permissions on parent
        parent = get_object_or_404(WebPath, pk=parent_id)
        has_permission = parent.is_publicable_by(user=request.user,
                                                 parent=True)
        if not has_permission:
            raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                         resource=request.method)

        # exclue relations
        excluded_childrens = ['editorialboardeditors',
                              'linked_page',
                              'navigationbaritem']
        if exclude_pages:
            excluded_childrens.append('page')
        if exclude_news:
            excluded_childrens.append('publicationcontext')

        # set new parent
        custom_values = {'parent': parent}

        # set values to all childs
        recursive_values = {'created_by': request.user,
                            'modified_by': None,
                            'site': parent.site,
                            'date_start': timezone.localtime(),
                            'date_end': timezone.localtime() + timezone.timedelta(days=30),
                            'in_evidence_start': None,
                            'in_evidence_end': None}

        # clone full tree or get only childs (useful to clone a root in another root!)
        to_apply = WebPath.objects.filter(parent=item) if only_childs else [item]
        for element in to_apply:
            try:
                clone(element,
                      excluded_fields=['created', 'modified'],
                      excluded_childrens=excluded_childrens,
                      custom_values=custom_values,
                      recursive_custom_values=recursive_values)
            except Exception as e: # pragma: no cover
                raise LoggedValidationException(classname=self.__class__.__name__,
                                                resource=request.method,
                                                detail=e)
        return Response(_("Cloning done with success!"))
