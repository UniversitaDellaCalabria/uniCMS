from cms.publications.models import PublicationAttachment
from cms.publications.serializers import PublicationAttachmentSerializer

from .. views.publication import PublicationRelatedObject, PublicationRelatedObjectList


class PublicationAttachmentList(PublicationRelatedObjectList):
    """
    """
    description = ""
    search_fields = ['name', 'file', 'description']
    serializer_class = PublicationAttachmentSerializer

    def get_queryset(self):
        """
        """
        super().get_data()
        return PublicationAttachment.objects.filter(publication=self.publication)


class PublicationAttachmentView(PublicationRelatedObject):
    """
    """
    description = ""
    serializer_class = PublicationAttachmentSerializer

    def get_queryset(self):
        """
        """
        super().get_data()
        return PublicationAttachment.objects.filter(pk=self.pk,
                                                    publication=self.publication)
