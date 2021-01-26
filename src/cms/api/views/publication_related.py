

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
        pub_id = self.kwargs['publication_id']
        items = PublicationRelated.objects.filter(publication__pk=pub_id)
        return items


class PublicationRelatedView(PublicationRelatedObject):
    """
    """
    description = ""
    serializer_class = PublicationRelatedSerializer

    def get_queryset(self):
        """
        """
        pub_id = self.kwargs['publication_id']
        pk = self.kwargs['pk']
        related = PublicationRelated.objects.filter(pk=pk,
                                                    publication__pk=pub_id)
        return related
