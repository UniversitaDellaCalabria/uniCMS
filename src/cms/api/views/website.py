
from rest_framework.permissions import IsAdminUser
from rest_framework.views import APIView

from cms.contexts.models import WebSite

from .. pagination import UniCmsApiPagination


class EditorWebsiteList(APIView, UniCmsApiPagination):
    """
    Editor user available active websites
    """
    description = "Get user editorial boards websites"
    permission_classes = [IsAdminUser]

    def get(self, request):
        result_list = []
        websites = WebSite.objects.filter(is_active=True)
        result_list = [i.serialize() for i in websites if i.is_managed_by(request.user)]
        results = self.paginate_queryset(result_list, request, view=self)
        return self.get_paginated_response(results)
