from cms.publications.forms import PublicationLinkForm
from cms.publications.models import *
from cms.publications.serializers import *

from rest_framework.response import Response
from rest_framework.views import APIView

from .. serializers import UniCMSFormSerializer
from .. views.publication import PublicationRelatedObject, PublicationRelatedObjectList


class PublicationLinkList(PublicationRelatedObjectList):
    """
    """
    description = ""
    search_fields = ['name', 'url']
    filterset_fields = ['created', 'modified']
    serializer_class = PublicationLinkSerializer

    def get_queryset(self):
        """
        """
        super().get_data()
        if self.publication:
            return PublicationLink.objects.filter(publication=self.publication)
        return PublicationLink.objects.none() # pragma: no cover


class PublicationLinkView(PublicationRelatedObject):
    """
    """
    description = ""
    serializer_class = PublicationLinkSerializer

    def get_queryset(self):
        """
        """
        super().get_data()
        return PublicationLink.objects.filter(pk=self.pk,
                                              publication=self.publication)


class PublicationLinkFormView(APIView):

    def get(self, *args, **kwargs):
        form = PublicationLinkForm(publication_id=kwargs.get('publication_id'))
        form_fields = UniCMSFormSerializer.serialize(form)
        return Response(form_fields)
