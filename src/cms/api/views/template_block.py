from django_filters.rest_framework import DjangoFilterBackend

from cms.templates.models import TemplateBlock
from cms.templates.serializers import TemplateBlockSerializer

from rest_framework import generics
from rest_framework import filters
from rest_framework.permissions import IsAdminUser

from .. pagination import UniCmsApiPagination


class TemplateBlockList(generics.ListAPIView):
    """
    """
    description = ""
    permission_classes = [IsAdminUser]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_fields = ['is_active', 'created', 'modified']
    pagination_class = UniCmsApiPagination
    search_fields = ['name', 'description']
    serializer_class = TemplateBlockSerializer
    queryset = TemplateBlock.objects.filter(is_active=True)


class TemplateBlockView(generics.RetrieveAPIView):
    """
    """
    description = ""
    permission_classes = [IsAdminUser]
    serializer_class = TemplateBlockSerializer
    queryset = TemplateBlock.objects.filter(is_active=True)
