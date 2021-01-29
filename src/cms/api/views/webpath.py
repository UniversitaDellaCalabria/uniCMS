from django.conf import settings
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse

from rest_framework import generics
from rest_framework.permissions import IsAdminUser

from cms.contexts import settings as contexts_settings
from cms.contexts.models import EditorialBoardEditors, WebPath, WebSite
from cms.contexts.serializers import WebPathSerializer
from cms.contexts.utils import is_publisher

from . generics import UniCMSListCreateAPIView
from .. exceptions import LoggedPermissionDenied


CMS_CONTEXT_PERMISSIONS = getattr(settings, 'CMS_CONTEXT_PERMISSIONS',
                                  contexts_settings.CMS_CONTEXT_PERMISSIONS)


class EditorWebsiteWebpathList(UniCMSListCreateAPIView):
    """
    """
    name = "Webpaths"
    description = "Get user editorial boards websites webpath list"
    serializer_class = WebPathSerializer

    def get_queryset(self):
        """
        """
        site_id = self.kwargs['site_id']
        site = get_object_or_404(WebSite, pk=site_id, is_active=True)
        if not site.is_managed_by(self.request.user):
            raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                         resource=site)
        return WebPath.objects.filter(site=site)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            # get parent
            parent = serializer.validated_data.get('parent')
            # check permissions on parent
            permission = EditorialBoardEditors.get_permission(webpath=parent,
                                                              user=request.user)
            publisher_perms = is_publisher(permission)
            if not publisher_perms:
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


# @method_decorator(staff_member_required, name='dispatch')
class EditorWebsiteWebpathView(generics.RetrieveUpdateDestroyAPIView):
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
            # if parent in request data, check permission on parent
            new_parent = serializer.validated_data.get('parent')
            if new_parent:
                # check permissions on parent
                permission = EditorialBoardEditors.get_permission(webpath=new_parent,
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
            parent = serializer.validated_data.get('parent')
            # check permissions on parent
            permission = EditorialBoardEditors.get_permission(webpath=parent,
                                                              user=request.user)
            publisher_perms = is_publisher(permission)
            if not publisher_perms:
                raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                             resource=request.method)
            return super().put(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        item = self.get_queryset().first()
        if not item: raise Http404
        permission = EditorialBoardEditors.get_permission(webpath=item.parent,
                                                          user=request.user)
        publisher_perms = is_publisher(permission)
        if not publisher_perms:
            raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                         resource=request.method)
        return super().delete(request, *args, **kwargs)
