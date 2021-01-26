

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
        pub_id = self.kwargs['publication_id']
        items = PublicationBlock.objects.filter(publication__pk=pub_id)
        return items


class PublicationBlockView(PublicationRelatedObject):
    """
    """
    description = ""
    serializer_class = PublicationBlockSerializer

    def get_queryset(self):
        """
        """
        pub_id = self.kwargs['publication_id']
        pk = self.kwargs['pk']
        blocks = PublicationBlock.objects.filter(pk=pk,
                                                 publication__pk=pub_id)
        return blocks
