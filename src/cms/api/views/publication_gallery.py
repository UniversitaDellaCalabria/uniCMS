from cms.publications.forms import PublicationGalleryForm
from cms.publications.models import *
from cms.publications.serializers import *

from rest_framework.response import Response
from rest_framework.views import APIView

from .. serializers import UniCMSFormSerializer
from .. views.publication import PublicationRelatedObject, PublicationRelatedObjectList


class PublicationGalleryList(PublicationRelatedObjectList):
    """
    """
    description = ""
    search_fields = ['collection__name', 'collection__description']
    ordering_fields = ['id', 'collection__name',
                       'collection__description', 'order', 'is_active']
    serializer_class = PublicationGallerySerializer

    def get_queryset(self):
        """
        """
        super().get_data()
        if self.publication:
            return PublicationGallery.objects.filter(publication=self.publication)
        return PublicationGallery.objects.none() # pragma: no cover


class PublicationGalleryView(PublicationRelatedObject):
    """
    """
    description = ""
    serializer_class = PublicationGallerySerializer

    def get_queryset(self):
        """
        """
        super().get_data()
        return PublicationGallery.objects.filter(pk=self.pk,
                                                 publication=self.publication)


class PublicationGalleryFormView(APIView):

    def get(self, *args, **kwargs):
        form = PublicationGalleryForm(publication_id=kwargs.get('publication_id'))
        form_fields = UniCMSFormSerializer.serialize(form)
        return Response(form_fields)
