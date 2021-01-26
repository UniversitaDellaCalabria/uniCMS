

from cms.publications.models import *
from cms.publications.serializers import *

from .. views.publication import PublicationRelatedObject, PublicationRelatedObjectList


class PublicationGalleryList(PublicationRelatedObjectList):
    """
    """
    description = ""
    serializer_class = PublicationGallerySerializer

    def get_queryset(self):
        """
        """
        super().get_data()
        return PublicationGallery.objects.filter(publication=self.publication)


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
