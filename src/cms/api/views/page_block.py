from cms.pages.forms import PageBlockForm
from cms.pages.models import *
from cms.pages.serializers import *

from rest_framework.response import Response
from rest_framework.views import APIView

from .. serializers import UniCMSFormSerializer
from .. views.page import PageRelatedObject, PageRelatedObjectList


class PageBlockList(PageRelatedObjectList):
    """
    """
    description = ""
    search_fields = ['block__name', 'section']
    filterset_fields = ['is_active']
    serializer_class = PageBlockSerializer
    ordering_fields = ['id', 'block__name',
                       'block__description', 'section',
                       'is_active', 'order']

    def get_queryset(self):
        """
        """
        super().get_data()
        if self.page:
            return PageBlock.objects.filter(page=self.page)
        return PageBlock.objects.none() # pragma: no cover


class PageBlockView(PageRelatedObject):
    """
    """
    description = ""
    serializer_class = PageBlockSerializer

    def get_queryset(self):
        """
        """
        super().get_data()
        items = PageBlock.objects.filter(pk=self.pk, page=self.page)
        return items


class PageBlockFormView(APIView):

    def get(self, *args, **kwargs):
        form = PageBlockForm(page_id=kwargs.get('page_id'))
        form_fields = UniCMSFormSerializer.serialize(form)
        return Response(form_fields)
