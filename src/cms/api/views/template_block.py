from django_filters.rest_framework import DjangoFilterBackend

from cms.templates.models import PageTemplateBlock, TemplateBlock
from cms.templates.serializers import (TemplateBlockSerializer,
                                       TemplatesBlockSerializer)

from rest_framework import generics
from rest_framework import filters
from rest_framework.permissions import IsAdminUser
from rest_framework.schemas.openapi import AutoSchema

from .. pagination import UniCmsApiPagination


class TemplatesBlockList(generics.ListAPIView):
    """
    """
    description = ""
    permission_classes = [IsAdminUser]
    filter_backends = [filters.SearchFilter,
                       DjangoFilterBackend,
                       filters.OrderingFilter]
    filterset_fields = ['is_active', 'created', 'modified']
    pagination_class = UniCmsApiPagination
    search_fields = ['name', 'description', 'type']
    serializer_class = TemplatesBlockSerializer
    queryset = TemplateBlock.objects.filter(is_active=True)


class TemplatesBlockView(generics.RetrieveAPIView):
    """
    """
    description = ""
    permission_classes = [IsAdminUser]
    serializer_class = TemplatesBlockSerializer
    queryset = TemplateBlock.objects.filter(is_active=True)


class SingleTemplateBlockListSchema(AutoSchema):
    def get_operation_id(self, path, method):# pragma: no cover
        return 'listSingleTemplateBlocks'


class TemplateBlockList(generics.ListAPIView):
    """
    """
    description = ""
    permission_classes = [IsAdminUser]
    filter_backends = [filters.SearchFilter,
                       DjangoFilterBackend,
                       filters.OrderingFilter]
    filterset_fields = ['is_active', 'created', 'modified']
    pagination_class = None
    schema = SingleTemplateBlockListSchema()
    search_fields = ['name', 'description']
    serializer_class = TemplateBlockSerializer

    def get_queryset(self):
        """
        """
        template_id = self.kwargs.get('template_id')
        if template_id:
            return PageTemplateBlock.objects.filter(is_active=True,
                                                    template__pk=template_id)
        return PageTemplateBlock.objects.none() # pragma: no cover


class SingleTemplateBlockListDetail(AutoSchema):
    def get_operation_id(self, path, method):# pragma: no cover
        return 'retrieveSingleTemplateBlock'


class TemplateBlockView(generics.RetrieveAPIView):
    """
    """
    description = ""
    permission_classes = [IsAdminUser]
    serializer_class = TemplateBlockSerializer
    schema = SingleTemplateBlockListDetail()

    def get_queryset(self):
        """
        """
        template_id = self.kwargs['template_id']
        item_id = self.kwargs['pk']
        items = PageTemplateBlock.objects\
                                 .filter(pk=item_id,
                                         template__pk=template_id,
                                         is_active=True)
        return items
