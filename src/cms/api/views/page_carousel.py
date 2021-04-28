from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404

from cms.pages.forms import PageCarouselForm
from cms.pages.models import *
from cms.pages.serializers import *

from rest_framework.response import Response
from rest_framework.schemas.openapi import AutoSchema
from rest_framework.views import APIView

from .. serializers import UniCMSFormSerializer
from .. views.page import PageRelatedObject, PageRelatedObjectList, PageRelatedObjectLogsView


class PageCarouselList(PageRelatedObjectList):
    """
    """
    description = ""
    search_fields = ['carousel__name', 'carousel__description']
    ordering_fields = ['id', 'carousel__name',
                       'is_active', 'order']
    serializer_class = PageCarouselSerializer

    def get_queryset(self):
        """
        """
        super().get_data()
        if self.page:
            return PageCarousel.objects.filter(page=self.page)
        return PageCarousel.objects.none() # pragma: no cover


class PageCarouselView(PageRelatedObject):
    """
    """
    description = ""
    serializer_class = PageCarouselSerializer

    def get_queryset(self):
        """
        """
        super().get_data()
        items = PageCarousel.objects.filter(pk=self.pk, page=self.page)
        return items


class PageCarouselFormView(APIView):

    def get(self, *args, **kwargs):
        form = PageCarouselForm(page_id=kwargs.get('page_id'))
        form_fields = UniCMSFormSerializer.serialize(form)
        return Response(form_fields)


class PageCarouselLogsSchema(AutoSchema):
    def get_operation_id(self, path, method):# pragma: no cover
        return 'listPageCarouselLogs'


class PageCarouselLogsView(PageRelatedObjectLogsView):

    schema = PageCarouselLogsSchema()

    def get_queryset(self):
        """
        """
        super().get_data()
        item = get_object_or_404(PageCarousel.objects.select_related('page'),
                                 pk=self.pk, page=self.page)
        content_type_id = ContentType.objects.get_for_model(item).pk
        return super().get_queryset(self.pk, content_type_id)
