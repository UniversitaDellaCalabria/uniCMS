import logging

from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _

from rest_framework import generics, status
from rest_framework import filters
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from cms.contexts import settings as contexts_settings
from cms.contexts.models import EditorialBoardEditors, WebPath, WebSite
from cms.contexts.utils import is_editor

from cms.publications.models import PublicationContext
from cms.publications.serializers import PublicationContextSerializer

from .. pagination import UniCmsApiPagination


CMS_CONTEXT_PERMISSIONS = getattr(settings, 'CMS_CONTEXT_PERMISSIONS',
                                  contexts_settings.CMS_CONTEXT_PERMISSIONS)

logger = logging.getLogger(__name__)


class EditorWebpathPublicationList(generics.ListCreateAPIView):
    """
    """
    description = ""
    filter_backends = [filters.SearchFilter]
    search_fields = ['in_evidence_start','publication__title']
    pagination_class = UniCmsApiPagination
    permission_classes = [IsAdminUser]
    serializer_class = PublicationContextSerializer

    def get_queryset(self):
        """
        """
        site_id = self.kwargs['site_id']
        webpath_id = self.kwargs['webpath_id']
        site = get_object_or_404(WebSite, pk=site_id, is_active=True)
        webpath = get_object_or_404(WebPath,
                                    pk=webpath_id,
                                    site=site)
        publications = PublicationContext.objects.filter(webpath=webpath)
        self.webpath = webpath
        is_active = self.request.GET.get('is_active')
        if is_active:
            publications = publications.filter(is_active=is_active)
        return publications

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            # get webpath
            webpath = serializer.validated_data.get('webpath')
            # check permissions on webpath
            permission = EditorialBoardEditors.get_permission(webpath=webpath,
                                                              user=request.user)
            editor_perms = is_editor(permission)
            if not editor_perms:
                error_msg = _("You don't have permissions")
                return Response(error_msg, status=status.HTTP_403_FORBIDDEN)

            publication = serializer.validated_data.get('publication')
            state = publication['state']
            if state == 'published' and permission not in publisher_perms:
                error_msg = _("You don't have permissions to save a published item, set draft instead")
                return Response(error_msg, status=status.HTTP_403_FORBIDDEN)
            return super().post(request, *args, **kwargs)
