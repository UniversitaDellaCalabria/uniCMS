from cms.publications.models import *
from cms.publications.serializers import *

from .. views.publication import PublicationRelatedObject, PublicationRelatedObjectList


class PublicationBlockList(PublicationRelatedObjectList):
    """
    """
    description = ""
    search_fields = ['block__name']
    serializer_class = PublicationBlockSerializer

    def get_queryset(self):
        """
        """
        super().get_data()
        return PublicationBlock.objects.filter(publication=self.publication)


class PublicationBlockView(PublicationRelatedObject):
    """
    """
    description = ""
    serializer_class = PublicationBlockSerializer

    def get_queryset(self):
        """
        """
        super().get_data()
        return PublicationBlock.objects.filter(pk=self.pk,
                                               publication=self.publication)
