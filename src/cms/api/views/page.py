from django.http import Http404
from django.shortcuts import get_object_or_404

from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.schemas.openapi import AutoSchema
from rest_framework.views import APIView

from cms.contexts.models import WebPath, WebSite

from cms.pages.forms import PageForm
from cms.pages.models import Page
from cms.pages.serializers import PageSerializer
from cms.pages.utils import copy_page_as_draft

from . generics import UniCMSCachedRetrieveUpdateDestroyAPIView, UniCMSListCreateAPIView, check_locks
from .. exceptions import LoggedPermissionDenied
from .. serializers import UniCMSFormSerializer


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
        site_id = self.kwargs.get('site_id')
        webpath_id = self.kwargs.get('webpath_id')
        if site_id and webpath_id:
            site = get_object_or_404(WebSite, pk=site_id, is_active=True)
            if not site.is_managed_by(self.request.user):
                raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                             resource=site)
            webpath = get_object_or_404(WebPath,
                                        pk=webpath_id,
                                        site=site)
            return Page.objects.filter(webpath=webpath)
        return Page.objects.none() # pragma: no cover

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            # get webpath
            webpath = serializer.validated_data.get('webpath')
            perms = webpath.is_editable_by(user=request.user)
            if not perms:
                raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                             resource=request.method)
            return super().post(request, *args, **kwargs)


class EditorWebpathPageView(UniCMSCachedRetrieveUpdateDestroyAPIView):
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
        pages = Page.objects\
                    .select_related('webpath')\
                    .filter(pk=pk,
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
            if new_webpath and new_webpath != item.webpath:
                # check permissions and locks on webpath
                webpath_perms = new_webpath.is_editable_by(obj=item,
                                                           user=request.user)
                if not webpath_perms:
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

            new_webpath = serializer.validated_data.get('webpath')
            # check permissions on webpath
            if new_webpath != item.webpath:
                webpath_perms = new_webpath.is_editable_by(obj=item,
                                                           user=request.user)
                if not webpath_perms:
                    raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                                 resource=request.method)
            return super().put(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        item = self.get_queryset().first()
        if not item: raise Http404
        # check permissions on page
        if item.state == 'published':
            has_permission = item.is_publicable_by(request.user)
        else:
            has_permission = item.is_editable_by(request.user)
        if not has_permission:
            raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                         resource=request.method)
        return super().delete(request, *args, **kwargs)


class PageChangeStateSchema(AutoSchema):
    def get_operation_id(self, path, method):# pragma: no cover
        return 'updatePageStatus'


class PageChangeStateView(APIView):
    """
    """
    description = ""
    permission_classes = [IsAdminUser]
    serializer_class = PageSerializer
    schema = PageChangeStateSchema()

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
            check_locks(item, request.user)
            item.is_active = not item.is_active
            item.save()
            result = self.serializer_class(item)
            return Response(result.data)
        raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                     resource=request.method)


class PageChangePublicationStatusSchema(AutoSchema):
    def get_operation_id(self, path, method):# pragma: no cover
        return 'updatePagePublicationStatus'


class PageChangePublicationStatusView(APIView):
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
            check_locks(item, request.user)
            item.toggleState()
            result = self.serializer_class(item)
            return Response(result.data)
        raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                     resource=request.method)


# Abstract API classes for every related object of Page

class PageRelatedObjectList(UniCMSListCreateAPIView):

    def get_data(self):
        """
        """
        site_id = self.kwargs.get('site_id')
        webpath_id = self.kwargs.get('webpath_id')
        if site_id and webpath_id:
            site = get_object_or_404(WebSite, pk=site_id, is_active=True)
            if not site.is_managed_by(self.request.user):
                raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                             resource=site)
            pk = self.kwargs['page_id']
            self.page = get_object_or_404(Page,
                                          pk=pk,
                                          webpath__pk=webpath_id,
                                          webpath__site__pk=site_id)
        else:
            self.page = None # pragma: no cover

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


class PageRelatedObject(UniCMSCachedRetrieveUpdateDestroyAPIView):

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


class PageFormView(APIView):

    def get(self, *args, **kwargs):
        form = PageForm(site_id=kwargs.get('site_id'),
                        webpath_id=kwargs.get('webpath_id'))
        form_fields = UniCMSFormSerializer.serialize(form)
        return Response(form_fields)


class PageGenericFormView(APIView):

    def get(self, *args, **kwargs):
        form = PageForm(site_id=kwargs.get('site_id'))
        form_fields = UniCMSFormSerializer.serialize(form)
        return Response(form_fields)


class PageCopyAsDraftSchema(AutoSchema):
    def get_operation_id(self, path, method):# pragma: no cover
        return 'copyPageAsDraftSchema'


class PageCopyAsDraftView(APIView):
    """
    """
    description = ""
    permission_classes = [IsAdminUser]
    serializer_class = PageSerializer
    schema = PageCopyAsDraftSchema()

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
            new_page = copy_page_as_draft(item)
            result = self.serializer_class(new_page)
            return Response(result.data)
        raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                     resource=request.method)
