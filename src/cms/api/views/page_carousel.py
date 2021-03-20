from cms.pages.forms import PageCarouselForm
from cms.pages.models import *
from cms.pages.serializers import *

from rest_framework.response import Response
from rest_framework.views import APIView

from .. serializers import UniCMSFormSerializer
from .. views.page import PageRelatedObject, PageRelatedObjectList


class PageCarouselList(PageRelatedObjectList):
    """
    """
    description = ""
    search_fields = ['carousel__name', 'carousel__description']
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
