from cms.publications.forms import PublicationRelatedForm
from cms.publications.models import *
from cms.publications.serializers import *

from rest_framework.response import Response
from rest_framework.views import APIView

from .. serializers import UniCMSFormSerializer
from .. views.publication import PublicationRelatedObject, PublicationRelatedObjectList


class PublicationRelatedList(PublicationRelatedObjectList):
    """
    """
    description = ""
    serializer_class = PublicationRelatedSerializer
    search_fields = ['related__name', 'related__title']

    def get_queryset(self):
        """
        """
        super().get_data()
        if self.publication:
            return PublicationRelated.objects.filter(publication=self.publication)
        return PublicationRelated.objects.none() # pragma: no cover


class PublicationRelatedView(PublicationRelatedObject):
    """
    """
    description = ""
    serializer_class = PublicationRelatedSerializer

    def get_queryset(self):
        """
        """
        super().get_data()
        return PublicationRelated.objects.filter(pk=self.pk,
                                                 publication=self.publication)


class PublicationRelatedFormView(APIView):

    def get(self, *args, **kwargs):
        form = PublicationRelatedForm(publication_id=kwargs.get('publication_id'))
        form_fields = UniCMSFormSerializer.serialize(form)
        return Response(form_fields)
