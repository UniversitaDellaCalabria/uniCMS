from django.conf import settings
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse

from rest_framework import generics
from rest_framework.permissions import IsAdminUser
from rest_framework.schemas.openapi import AutoSchema

from cms.contexts import settings as contexts_settings
from cms.contexts.forms import WebPathForm
from cms.contexts.models import EditorialBoardEditors, EditorialBoardLockUser, WebPath, WebSite
from cms.contexts.serializers import WebPathSerializer, WebPathSelectOptionsSerializer
from cms.contexts.utils import is_publisher

from rest_framework.response import Response
from rest_framework.views import APIView

from . generics import UniCMSCachedRetrieveUpdateDestroyAPIView, UniCMSListCreateAPIView, UniCMSListSelectOptionsAPIView
from .. exceptions import LoggedPermissionDenied
from .. serializers import UniCMSFormSerializer


CMS_CONTEXT_PERMISSIONS = getattr(settings, 'CMS_CONTEXT_PERMISSIONS',
                                  contexts_settings.CMS_CONTEXT_PERMISSIONS)


class EditorWebsiteWebpathList(UniCMSListCreateAPIView):
    """
    """
    name = "Webpaths"
    description = "Get user editorial boards websites webpath list"
    serializer_class = WebPathSerializer
    search_fields = ['name']

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
            webpath = serializer.save()
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


class EditorWebsiteWebpathView(UniCMSCachedRetrieveUpdateDestroyAPIView):
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
            return super().patch(request, *args, **kwargs)

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
            return super().put(request, *args, **kwargs)

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
