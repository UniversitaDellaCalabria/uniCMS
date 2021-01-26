

from cms.publications.models import *
from cms.publications.serializers import *

from .. views.publication import PublicationRelatedObject, PublicationRelatedObjectList


class PublicationRelatedList(PublicationRelatedObjectList):
    """
    """
    description = ""
    serializer_class = PublicationRelatedSerializer

    def get_queryset(self):
        """
        """
        super().get_data()
        return PublicationRelated.objects.filter(publication=self.publication)


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
