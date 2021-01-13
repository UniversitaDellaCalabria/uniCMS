import logging

from django.conf import settings

from rest_framework.permissions import IsAdminUser
from rest_framework.views import APIView

from cms.contexts.models import EditorialBoardEditors, WebSite
from cms.contexts import settings as contexts_settings

from .. pagination import UniCmsApiPagination


CMS_CONTEXT_PERMISSIONS = getattr(settings, 'CMS_CONTEXT_PERMISSIONS',
                                  contexts_settings.CMS_CONTEXT_PERMISSIONS)

logger = logging.getLogger(__name__)


class EditorWebsiteList(APIView, UniCmsApiPagination):
    """
    Editor user available active websites
    """
    description = "Get user editorial boards websites"
    permission_classes = [IsAdminUser]

    def get(self, request):
        permissions = EditorialBoardEditors.objects.filter(user=request.user,
                                                           is_active=True)
        websites = []
        for permission in permissions:
            webpath = permission.webpath
            # can access to all active websites
            if not webpath:
                websites = []
                sites = WebSite.objects.filter(is_active=True)
                for site in sites:
                    websites.append(site.serialize())
                break
            # can access to active webpath' websites
            permissions = permissions.filter(webpath__is_active=True,
                                             webpath__site__is_active=True)
            site = permission.webpath.site
            serialized_site = site.serialize()
            if serialized_site not in websites:
                websites.append(serialized_site)
        results = self.paginate_queryset(websites, request, view=self)
        return self.get_paginated_response(results)
