from cms.pages.forms import PagePublicationForm
from cms.pages.models import *
from cms.pages.serializers import *

from rest_framework.response import Response
from rest_framework.views import APIView

from .. serializers import UniCMSFormSerializer
from .. views.page import PageRelatedObject, PageRelatedObjectList


class PagePublicationList(PageRelatedObjectList):
    """
    """
    description = ""
    search_fields = ['publication__name','publication__title',
                     'publication__subheading', 'publication__content']
    ordering_fields = ['id', 'publication__name', 'publication__title',
                       'publication__subheading', 'order', 'is_active']
    serializer_class = PagePublicationSerializer

    def get_queryset(self):
        """
        """
        super().get_data()
        if self.page:
            return PagePublication.objects.filter(page=self.page)
        return PagePublication.objects.none() # pragma: no cover


class PagePublicationView(PageRelatedObject):
    """
    """
    description = ""
    serializer_class = PagePublicationSerializer

    def get_queryset(self):
        """
        """
        super().get_data()
        items = PagePublication.objects.filter(pk=self.pk, page=self.page)
        return items


class PagePublicationFormView(APIView):

    def get(self, *args, **kwargs):
        form = PagePublicationForm(page_id=kwargs.get('page_id'))
        form_fields = UniCMSFormSerializer.serialize(form)
        return Response(form_fields)
