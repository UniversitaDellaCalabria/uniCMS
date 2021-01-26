

from cms.publications.models import *
from cms.publications.serializers import *

from .. views.publication import PublicationRelatedObject, PublicationRelatedObjectList


class PublicationLinkList(PublicationRelatedObjectList):
    """
    """
    description = ""
    search_fields = ['name', 'url']
    serializer_class = PublicationLinkSerializer

    def get_queryset(self):
        """
        """
        pub_id = self.kwargs['publication_id']
        items = PublicationLink.objects.filter(publication__pk=pub_id)
        return items


class PublicationLinkView(PublicationRelatedObject):
    """
    """
    description = ""
    serializer_class = PublicationLinkSerializer

    def get_queryset(self):
        """
        """
        pub_id = self.kwargs['publication_id']
        pk = self.kwargs['pk']
        links = PublicationLink.objects.filter(pk=pk, publication__pk=pub_id)
        return links
