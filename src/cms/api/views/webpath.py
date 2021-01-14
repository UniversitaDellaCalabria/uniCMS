import logging

from django.conf import settings
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from rest_framework import generics, status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from cms.contexts.models import EditorialBoardEditors, WebPath, WebSite
from cms.contexts.serializers import WebPathSerializer
from cms.contexts import settings as contexts_settings

from .. pagination import UniCmsApiPagination


CMS_CONTEXT_PERMISSIONS = getattr(settings, 'CMS_CONTEXT_PERMISSIONS',
                                  contexts_settings.CMS_CONTEXT_PERMISSIONS)

logger = logging.getLogger(__name__)


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
        is_active = self.request.GET.get('is_active')
        if is_active:
            webpaths = webpaths.filter(is_active=is_active)
        return webpaths

    def get(self, request, *args, **kwargs):
        context_permissions = dict(CMS_CONTEXT_PERMISSIONS)
        webpaths = []

        for webpath in self.get_queryset():
            permission = EditorialBoardEditors.get_permission(user=request.user,
                                                              webpath=webpath)
            webpath_data = self.get_serializer(instance=webpath).data
            webpath_data["permission_id"] = permission
            permission_label = context_permissions[permission] if permission else ''
            webpath_data["permission_label"] = permission_label
            webpaths.append(webpath_data)
        results = self.paginate_queryset(webpaths)
        return self.get_paginated_response(results)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            # get parent
            parent = serializer.validated_data.get('parent')
            # check permissions on parent
            permission = EditorialBoardEditors.get_permission(webpath=parent,
                                                              user=request.user)
            publisher_perms = (6,7,8)
            if permission not in publisher_perms or (permission == 6 and parent.created_by != request.user):
                error_msg = _("You don't have permissions")
                return Response(error_msg, status=status.HTTP_403_FORBIDDEN)

            webpath = serializer.save()
            # add permission to webpath
            if permission != 8:
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
    description = "Get user\'s editorial boards websites single webpath"
    permission_classes = [IsAdminUser]
    serializer_class = WebPathSerializer

    def get_queryset(self):
        """
        """
        site_id = self.kwargs['site_id']
        pk = self.kwargs['pk']
        site = get_object_or_404(WebSite, pk=site_id, is_active=True)
        webpaths = WebPath.objects.filter(pk=pk, site=site)
        return webpaths

    def get(self, request, *args, **kwargs):
        webpath = self.get_queryset().first()
        if not webpath: raise Http404
        context_permissions = dict(CMS_CONTEXT_PERMISSIONS)
        result = self.get_serializer(instance=webpath).data
        permission = EditorialBoardEditors.get_permission(webpath, request.user)
        result["permission_id"] = permission
        webpath_permission = context_permissions[permission] if permission else None
        result["permission_label"] = webpath_permission
        return Response(result)

    def patch(self, request, *args, **kwargs):
        webpath = self.get_queryset().first()
        if not webpath: raise Http404
        parent = webpath.parent
        dict(CMS_CONTEXT_PERMISSIONS)

        serializer = self.get_serializer(instance=webpath,
                                         data=request.data,
                                         partial=True)
        if serializer.is_valid(raise_exception=True):
            # parent in request data
            new_parent = serializer.validated_data.get('parent')
            if new_parent:
                # get active parent
                parent = new_parent

            # check permissions on parent
            publisher_perms = (6,7,8)
            parent_permission = EditorialBoardEditors.get_permission(webpath=parent,
                                                                     user=request.user)
            if parent_permission not in publisher_perms or (parent_permission == 6 and parent.created_by != request.user):
                error_msg = _("You don't have permissions on webpath {}").format(parent)
                return Response(error_msg, status=status.HTTP_403_FORBIDDEN)

            return super().patch(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        webpath = self.get_queryset().first()
        if not webpath: raise Http404
        dict(CMS_CONTEXT_PERMISSIONS)
        permission = EditorialBoardEditors.get_permission(webpath=webpath,
                                                          user=request.user)
        publisher_perms = (6,7,8)
        # if user isn't a publisher
        # or can manage only created by him objects and he is not the webpath creator
        if permission not in publisher_perms or (permission == 6 and webpath.created_by != request.user):
            error_msg = _("You don't have permissions on webpath {}").format(webpath)
            return Response(error_msg, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(instance=webpath,
                                         data=request.data)
        if serializer.is_valid(raise_exception=True):
            parent = serializer.validated_data.get('parent')
            # check permissions on parent
            parent_permission = EditorialBoardEditors.get_permission(webpath=parent,
                                                                     user=request.user)
            if parent_permission not in publisher_perms or (parent_permission == 6 and parent.created_by != request.user):
                error_msg = _("You don't have permissions on webpath {}").format(parent)
                return Response(error_msg, status=status.HTTP_403_FORBIDDEN)

            return super().put(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        webpath = self.get_queryset().first()
        if not webpath: raise Http404
        permission = EditorialBoardEditors.get_permission(webpath=webpath,
                                                          user=request.user)
        publisher_perms = (6,7,8)
        if permission not in publisher_perms or (permission == 6 and webpath.created_by != request.user):
            error_msg = _("You don't have permissions on webpath {}").format(webpath)
            return Response(error_msg, status=status.HTTP_403_FORBIDDEN)
        return super().delete(request, *args, **kwargs)
