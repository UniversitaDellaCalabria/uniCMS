from django_filters.rest_framework import DjangoFilterBackend

from cms.templates.models import PageTemplate
from cms.templates.serializers import PageTemplateSerializer

from rest_framework import generics
from rest_framework import filters
from rest_framework.permissions import IsAdminUser

from .. pagination import UniCmsApiPagination


class PageTemplateList(generics.ListAPIView):
    """
    """
    description = ""
    permission_classes = [IsAdminUser]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_fields = ['is_active', 'created', 'modified']
    pagination_class = UniCmsApiPagination
    search_fields = ['name']
    serializer_class = PageTemplateSerializer
    queryset = PageTemplate.objects.filter(is_active=True)


class PageTemplateView(generics.RetrieveAPIView):
    """
    """
    description = ""
    permission_classes = [IsAdminUser]
    serializer_class = PageTemplateSerializer
    queryset = PageTemplate.objects.filter(is_active=True)
