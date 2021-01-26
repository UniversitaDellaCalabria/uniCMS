from django.http import Http404
from django.shortcuts import get_object_or_404

from rest_framework import generics
from rest_framework.permissions import IsAdminUser
from rest_framework.schemas.openapi import AutoSchema

from cms.contexts.models import EditorialBoardEditors, WebPath, WebSite
from cms.contexts.utils import is_editor

from cms.pages.models import Page, PAGE_STATES
from cms.pages.serializers import PageSerializer

from . generics import UniCMSListCreateAPIView
from .. exceptions import LoggedPermissionDenied


class EditorWebpathPageList(UniCMSListCreateAPIView):
    """
    """
    name = "Pages"
    description = ""
    search_fields = ['name', 'title', 'description']
    serializer_class = PageSerializer

    def get_queryset(self):
        """
        """
        site_id = self.kwargs['site_id']
        webpath_id = self.kwargs['webpath_id']
        site = get_object_or_404(WebSite, pk=site_id, is_active=True)
        if not site.is_managed_by(self.request.user):
            raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                         resource=site)
        webpath = get_object_or_404(WebPath,
                                    pk=webpath_id,
                                    site=site)
        items = Page.objects.filter(webpath=webpath)
        self.webpath = webpath
        return items

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            # get webpath
            webpath = serializer.validated_data.get('webpath')
            # check permissions on webpath
            permission = EditorialBoardEditors.get_permission(webpath=webpath,
                                                              user=request.user)
            publisher_perms = is_editor(permission)
            if not publisher_perms:
                raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                             resource=request.method)
            return super().post(request, *args, **kwargs)


class EditorWebpathPageView(generics.RetrieveUpdateDestroyAPIView):
    """
    """
    description = ""
    permission_classes = [IsAdminUser]
    serializer_class = PageSerializer

    def get_queryset(self):
        """
        """
        site_id = self.kwargs['site_id']
        site = get_object_or_404(WebSite, pk=site_id, is_active=True)
        if not site.is_managed_by(self.request.user):
            raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                         resource=site)
        webpath_id = self.kwargs['webpath_id']
        pk = self.kwargs['pk']
        pages = Page.objects.filter(pk=pk,
                                    webpath__pk=webpath_id,
                                    webpath__site__pk=site_id)
        return pages

    def patch(self, request, *args, **kwargs):
        item = self.get_queryset().first()
        if not item: raise Http404
        serializer = self.get_serializer(instance=item,
                                         data=request.data,
                                         partial=True)
        if serializer.is_valid(raise_exception=True):
            # if user hasn't permission to edit page
            has_permission = item.is_editable_by(request.user)
            if not has_permission:
                raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                             resource=request.method)

            # if parent in request data, check permission on parent
            new_webpath = serializer.validated_data.get('webpath')
            if new_webpath:
                # check permissions on webpath
                permission = EditorialBoardEditors.get_permission(webpath=new_webpath,
                                                                  user=request.user)
                editor_perms = is_editor(permission)
                if not editor_perms:
                    raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                                 resource=request.method)
            return super().patch(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        item = self.get_queryset().first()
        if not item: raise Http404

        serializer = self.get_serializer(instance=item,
                                         data=request.data)
        if serializer.is_valid(raise_exception=True):
            # if user hasn't permission to edit page
            has_permission = item.is_editable_by(request.user)
            if not has_permission:
                raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                             resource=request.method)

            webpath = serializer.validated_data.get('webpath')
            # check permissions on webpath
            permission = EditorialBoardEditors.get_permission(webpath=webpath,
                                                              user=request.user)
            editor_perms = is_editor(permission)
            if not editor_perms:
                raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                             resource=request.method)
            return super().put(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        item = self.get_queryset().first()
        if not item: raise Http404
        # check permissions on page
        has_permission = item.is_publicable_by(request.user)
        if not has_permission:
            raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                         resource=request.method)
        return super().delete(request, *args, **kwargs)


class PageChangeStatusSchema(AutoSchema):
    def get_operation_id(self, path, method):
        return 'updatePageStatus'


class PageChangeStateView(generics.RetrieveAPIView):
    """
    """
    description = ""
    permission_classes = [IsAdminUser]
    serializer_class = PageSerializer
    schema = PageChangeStatusSchema()

    def get_queryset(self):
        """
        """
        site_id = self.kwargs['site_id']
        site = get_object_or_404(WebSite, pk=site_id, is_active=True)
        if not site.is_managed_by(self.request.user):
            raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                         resource=site)
        webpath_id = self.kwargs['webpath_id']
        pk = self.kwargs['pk']
        pages = Page.objects.filter(pk=pk,
                                    webpath__pk=webpath_id,
                                    webpath__site__pk=site_id)
        return pages

    def get(self, request, *args, **kwargs):
        item = self.get_queryset().first()
        if not item: raise Http404
        has_permission = item.is_publicable_by(request.user)
        if has_permission:
            item.is_active = not item.is_active
            item.save()
            return super().get(request, *args, **kwargs)
        raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                     resource=request.method)


class PageChangePublicationStatusSchema(AutoSchema):
    def get_operation_id(self, path, method):
        return 'updatePagePublicationStatus'


class PageChangePublicationStatusView(generics.RetrieveAPIView):
    """
    """
    description = ""
    permission_classes = [IsAdminUser]
    serializer_class = PageSerializer
    schema = PageChangePublicationStatusSchema()

    def get_queryset(self):
        """
        """
        site_id = self.kwargs['site_id']
        site = get_object_or_404(WebSite, pk=site_id, is_active=True)
        if not site.is_managed_by(self.request.user):
            raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                         resource=site)
        webpath_id = self.kwargs['webpath_id']
        pk = self.kwargs['pk']
        pages = Page.objects.filter(pk=pk,
                                    webpath__pk=webpath_id,
                                    webpath__site__pk=site_id)
        return pages

    def get(self, request, *args, **kwargs):
        item = self.get_queryset().first()
        if not item: raise Http404
        has_permission = item.is_publicable_by(request.user)
        if has_permission:
            if item.state == PAGE_STATES[0][0]:
                item.state = PAGE_STATES[1][0]
            else: item.state = PAGE_STATES[0][0]
            item.save()
            return super().get(request, *args, **kwargs)
        raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                     resource=request.method)


# Abstract API classes for every related object of Page

class PageRelatedObjectList(UniCMSListCreateAPIView):

    def get_data(self):
        """
        """
        site_id = self.kwargs['site_id']
        site = get_object_or_404(WebSite, pk=site_id, is_active=True)
        if not site.is_managed_by(self.request.user):
            raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                         resource=site)
        webpath_id = self.kwargs['webpath_id']
        pk = self.kwargs['page_id']
        self.page = get_object_or_404(Page,
                                      pk=pk,
                                      webpath__pk=webpath_id,
                                      webpath__site__pk=site_id)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            # get page
            page = serializer.validated_data.get('page')
            # check permissions on page
            has_permission = page.is_editable_by(request.user)
            if not has_permission:
                raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                             resource=request.method)
            return super().post(request, *args, **kwargs)

    class Meta:
        abstract = True


class PageRelatedObject(generics.RetrieveUpdateDestroyAPIView):

    permission_classes = [IsAdminUser]

    def get_data(self):
        site_id = self.kwargs['site_id']
        site = get_object_or_404(WebSite, pk=site_id, is_active=True)
        if not site.is_managed_by(self.request.user):
            raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                         resource=site)
        webpath_id = self.kwargs['webpath_id']
        page_id = self.kwargs['page_id']
        self.pk = self.kwargs['pk']
        self.page = get_object_or_404(Page,
                                      pk=page_id,
                                      webpath__pk=webpath_id,
                                      webpath__site__pk=site_id)

    def patch(self, request, *args, **kwargs):
        item = self.get_queryset().first()
        if not item: raise Http404
        serializer = self.get_serializer(instance=item,
                                         data=request.data,
                                         partial=True)
        if serializer.is_valid(raise_exception=True):
            page = item.page
            # check permissions on page
            has_permission = page.is_editable_by(request.user)
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
            page = item.page
            # check permissions on page
            has_permission = page.is_editable_by(request.user)
            if not has_permission:
                raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                             resource=request.method)
            return super().put(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        item = self.get_queryset().first()
        if not item: raise Http404
        page = item.page
        # check permissions on page
        has_permission = page.is_editable_by(request.user)
        if not has_permission:
            raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                         resource=request.method)
        return super().delete(request, *args, **kwargs)

    class Meta:
        abstract = True
