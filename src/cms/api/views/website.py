from django.shortcuts import get_object_or_404

from cms.contexts.models import WebSite

from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from .. exceptions import LoggedPermissionDenied
from .. pagination import UniCmsApiPagination


class EditorWebsiteList(APIView, UniCmsApiPagination):
    """
    Editor user available active websites
    """
    name = "Websites"
    description = "Get user editorial boards websites"
    permission_classes = [IsAdminUser]

    def get(self, request):
        result_list = []
        websites = WebSite.objects.filter(is_active=True)
        result_list = [i.serialize() for i in websites if i.is_managed_by(request.user)]
        results = self.paginate_queryset(result_list, request, view=self)
        return self.get_paginated_response(results)


class EditorWebsiteView(APIView):
    """
    Editor user get website webpath permissions
    """
    name = "Website"
    description = "Get user\'s editorial boards websites single webpath"
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        """
        """
        pk = self.kwargs['pk']
        site = get_object_or_404(WebSite, pk=pk, is_active=True)
        if not site.is_managed_by(self.request.user): # pragma: no cover
            raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                         resource=site)
        return site

    def get(self, request, *args, **kwargs):
        return Response(self.get_queryset().serialize())
