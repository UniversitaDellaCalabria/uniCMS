from cms.pages.forms import PageHeadingForm
from cms.pages.models import *
from cms.pages.serializers import *

from rest_framework.response import Response
from rest_framework.views import APIView

from .. serializers import UniCMSFormSerializer
from .. views.page import PageRelatedObject, PageRelatedObjectList


class PageHeadingList(PageRelatedObjectList):
    """
    """
    description = ""
    search_fields = ['title', 'description']
    serializer_class = PageHeadingSerializer

    def get_queryset(self):
        """
        """
        super().get_data()
        if self.page:
            return PageHeading.objects.filter(page=self.page)
        return PagePublication.objects.none() # pragma: no cover


class PageHeadingView(PageRelatedObject):
    """
    """
    description = ""
    serializer_class = PageHeadingSerializer

    def get_queryset(self):
        """
        """
        super().get_data()
        items = PageHeading.objects.filter(pk=self.pk, page=self.page)
        return items


class PageHeadingFormView(APIView):

    def get(self, *args, **kwargs):
        form = PageHeadingForm(page_id=kwargs.get('page_id'))
        form_fields = UniCMSFormSerializer.serialize(form)
        return Response(form_fields)
