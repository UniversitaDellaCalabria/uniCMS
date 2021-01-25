from django.http import Http404
from django.shortcuts import get_object_or_404

from rest_framework import filters, generics
from rest_framework.permissions import IsAdminUser

from cms.contexts.models import EditorialBoardEditors, WebPath, WebSite
from cms.contexts.utils import is_editor, is_publisher

from cms.pages.models import Page, PAGE_STATES
from cms.pages.serializers import PageSerializer, PageWebpathSerializer

from .. exceptions import LoggedPermissionDenied
from .. pagination import UniCmsApiPagination


class EditorWebpathPageList(generics.ListCreateAPIView):
    """
    """
    name = "Pages"
    description = ""
    filter_backends = [filters.SearchFilter]
    search_fields = ['in_evidence_start','publication__title']
    pagination_class = UniCmsApiPagination
    permission_classes = [IsAdminUser]
    serializer_class = PageWebpathSerializer

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
        pages = Page.objects.filter(webpath=webpath)
        self.webpath = webpath
        is_active = self.request.GET.get('is_active')
        if is_active:
            pages = pages.filter(is_active=is_active)
        return pages

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


class PageChangeStateView(generics.RetrieveAPIView):
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


class PageChangePublicationStatusView(generics.RetrieveAPIView):
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

class PageRelatedObjectList(generics.ListCreateAPIView):

    filter_backends = [filters.SearchFilter]
    pagination_class = UniCmsApiPagination
    permission_classes = [IsAdminUser]

    class Meta:
        abstract = True

    def get_queryset(self):
        """
        """
        site_id = self.kwargs['site_id']
        site = get_object_or_404(WebSite, pk=site_id, is_active=True)
        if not site.is_managed_by(self.request.user):
            raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                         resource=site)
        webpath_id = self.kwargs['webpath_id']
        page_id = self.kwargs['page_id']
        self.page = Page.objects.filter(pk=pk,
                                        webpath__pk=webpath_id,
                                        webpath__site__pk=site_id).first()

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


class PageRelatedObject(generics.RetrieveUpdateDestroyAPIView):

    filter_backends = [filters.SearchFilter]
    permission_classes = [IsAdminUser]

    class Meta:
        abstract = True

    def get_queryset(self):
        site_id = self.kwargs['site_id']
        site = get_object_or_404(WebSite, pk=site_id, is_active=True)
        if not site.is_managed_by(self.request.user):
            raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                         resource=site)
        webpath_id = self.kwargs['webpath_id']
        page_id = self.kwargs['page_id']
        self.pk = self.kwargs['pk']
        self.page = Page.objects.filter(pk=page_id,
                                        webpath__pk=webpath_id,
                                        webpath__site__pk=site_id).first()

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
