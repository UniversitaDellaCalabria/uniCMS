import logging

from django.conf import settings
from django.http import HttpResponseRedirect
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
        # site in url kwargs
        site_id = kwargs['site_id']
        site = get_object_or_404(WebSite,
                                 pk=site_id,
                                 is_active=True)

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            # get parent
            parent_pk = request.data.get('parent')
            parent = WebPath.objects.filter(pk=parent_pk, site=site).first()
            # check permissions on parent
            permission = EditorialBoardEditors.get_permission(webpath=parent,
                                                              user=request.user)
            publisher_perms = (6,7,8)
            if permission not in publisher_perms or (permission == 6 and parent.created_by != request.user):
                error_msg = _("You don't have permissions")
                return Response(error_msg, status=status.HTTP_403_FORBIDDEN)

            webpath = serializer.save()
            # ToDo HOOK ON SAVE
            # webpath.created_by = request.user
            # webpath.modified_by = request.user
            # webpath.save()
            # add permission to webpath
            if permission != 8:
                EditorialBoardEditors.objects.create(user=request.user,
                                                     webpath=webpath,
                                                     permission=permission,
                                                     is_active=True)
            url = reverse('unicms_api:editorial-board-site-webpath',
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
        webpaths = WebPath.objects.filter(pk=pk, site=site)
        return webpaths

    def get(self, request, *args, **kwargs):
        context_permissions = dict(CMS_CONTEXT_PERMISSIONS)
        webpath = self.get_queryset().first()
        result = self.get_serializer(instance=webpath).data
        permission = EditorialBoardEditors.get_permission(webpath, request.user)
        result["permission_id"] = permission
        webpath_permission = context_permissions[permission] if permission else None
        result["permission_label"] = webpath_permission
        return Response(result)

    def patch(self, request, *args, **kwargs):
        site_id = kwargs['site_id']
        webpath = self.get_queryset().first()
        parent = webpath.parent
        dict(CMS_CONTEXT_PERMISSIONS)

        # site id in request.data
        site_pk = request.data.get('site')
        if site_pk and int(site_pk) != site_id:
            error_msg = _("Site must be {}").format(webpath.site)
            return Response(error_msg, status=status.HTTP_403_FORBIDDEN)

        # parent in request data
        parent_pk = request.data.get('parent')
        if parent_pk:
            # get active parent
            new_parent = WebPath.objects.filter(pk=parent_pk,
                                                site=webpath.site).first()
            if not new_parent:
                error_msg = _("Parent not found")
                return Response(error_msg, status=status.HTTP_404_NOT_FOUND)
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
        dict(CMS_CONTEXT_PERMISSIONS)
        site_id = kwargs['site_id']
        webpath = self.get_queryset().first()
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
            # parent in request data
            parent_pk = request.data.get('parent')
            # get active parent
            parent = WebPath.objects.filter(pk=parent_pk,
                                            site=webpath.site).first()
            # check permissions on parent
            parent_permission = EditorialBoardEditors.get_permission(webpath=parent,
                                                                     user=request.user)
            if parent_permission not in publisher_perms or (parent_permission == 6 and parent.created_by != request.user):
                error_msg = _("You don't have permissions on webpath {}").format(parent)
                return Response(error_msg, status=status.HTTP_403_FORBIDDEN)

            return super().put(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        site_id = kwargs['site_id']
        pk = kwargs['pk']
        site = get_object_or_404(WebSite, pk=site_id, is_active=True)
        webpath = get_object_or_404(WebPath, pk=pk, site=site)
        permission = EditorialBoardEditors.get_permission(webpath=webpath,
                                                          user=request.user)
        publisher_perms = (6,7,8)
        if permission not in publisher_perms or (permission == 6 and webpath.created_by != request.user):
            error_msg = _("You don't have permissions on webpath {}").format(webpath)
            return Response(error_msg, status=status.HTTP_403_FORBIDDEN)

        return super().delete(request, *args, **kwargs)
