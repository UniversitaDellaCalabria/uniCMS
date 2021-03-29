from cms.pages.forms import PageMediaForm
from cms.pages.models import *
from cms.pages.serializers import *

from rest_framework.response import Response
from rest_framework.views import APIView

from .. serializers import UniCMSFormSerializer
from .. views.page import PageRelatedObject, PageRelatedObjectList


class PageMediaList(PageRelatedObjectList):
    """
    """
    description = ""
    search_fields = ['media__title', 'media__file', 'media__description']
    serializer_class = PageMediaSerializer

    def get_queryset(self):
        """
        """
        super().get_data()
        if self.page:
            return PageMedia.objects.filter(page=self.page)
        return PageMedia.objects.none() # pragma: no cover


class PageMediaView(PageRelatedObject):
    """
    """
    description = ""
    serializer_class = PageMediaSerializer

    def get_queryset(self):
        """
        """
        super().get_data()
        items = PageMedia.objects.filter(pk=self.pk, page=self.page)
        return items


class PageMediaFormView(APIView):

    def get(self, *args, **kwargs):
        form = PageMediaForm(page_id=kwargs.get('page_id'))
        form_fields = UniCMSFormSerializer.serialize(form)
        return Response(form_fields)
