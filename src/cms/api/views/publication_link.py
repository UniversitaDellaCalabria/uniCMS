

from cms.publications.models import *
from cms.publications.serializers import *

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
        return PublicationLink.objects.filter(publication=self.publication)


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
