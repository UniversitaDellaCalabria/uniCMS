from django.http import Http404
from django.shortcuts import get_object_or_404

from rest_framework import generics
from rest_framework.permissions import IsAdminUser

from cms.contexts.models import EditorialBoardEditors, WebPath, WebSite
from cms.contexts.utils import is_publisher

from cms.publications.models import PublicationContext
from cms.publications.serializers import PublicationContextSerializer

from . generics import UniCMSListCreateAPIView
from .. exceptions import LoggedPermissionDenied


class EditorWebpathPublicationContextList(UniCMSListCreateAPIView):
    """
    """
    description = ""
    search_fields = ['publication__title']
    serializer_class = PublicationContextSerializer

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
        items = PublicationContext.objects.filter(webpath=webpath)
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
            publisher_perms = is_publisher(permission)
            if not publisher_perms:
                raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                             resource=request.method)
            return super().post(request, *args, **kwargs)


class EditorWebpathPublicationContextView(generics.RetrieveUpdateDestroyAPIView):
    """
    """
    description = ""
    permission_classes = [IsAdminUser]
    serializer_class = PublicationContextSerializer

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
        contexts = PublicationContext.objects.filter(pk=pk,
                                                     webpath__pk=webpath_id,
                                                     webpath__site__pk=site_id)
        return contexts

    def patch(self, request, *args, **kwargs):
        item = self.get_queryset().first()
        if not item: raise Http404
        serializer = self.get_serializer(instance=item,
                                         data=request.data,
                                         partial=True)
        if serializer.is_valid(raise_exception=True):
            webpath = item.webpath
            permission = EditorialBoardEditors.get_permission(webpath=webpath,
                                                              user=request.user)
            publisher_perms = is_publisher(permission)
            if not publisher_perms:
                raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                             resource=request.method)
            return super().patch(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        item = self.get_queryset().first()
        if not item: raise Http404
        serializer = self.get_serializer(instance=item,
                                         data=request.data)
        if serializer.is_valid(raise_exception=True):
            webpath = item.webpath
            permission = EditorialBoardEditors.get_permission(webpath=webpath,
                                                              user=request.user)
            publisher_perms = is_publisher(permission)
            if not publisher_perms:
                raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                             resource=request.method)
            return super().put(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        item = self.get_queryset().first()
        if not item: raise Http404
        webpath = item.webpath
        permission = EditorialBoardEditors.get_permission(webpath=webpath,
                                                          user=request.user)
        publisher_perms = is_publisher(permission)
        if not publisher_perms:
            raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                         resource=request.method)
        return super().delete(request, *args, **kwargs)
