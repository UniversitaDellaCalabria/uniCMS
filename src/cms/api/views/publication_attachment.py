from cms.publications.forms import PublicationAttachmentForm
from cms.publications.models import PublicationAttachment
from cms.publications.serializers import PublicationAttachmentSerializer

from rest_framework.response import Response
from rest_framework.views import APIView

from .. serializers import UniCMSFormSerializer
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
        if self.publication:
            return PublicationAttachment.objects.filter(publication=self.publication)
        return PublicationAttachment.objects.none() # pragma: no cover


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


class PublicationAttachmentFormView(APIView):

    def get(self, *args, **kwargs):
        form = PublicationAttachmentForm(publication_id=kwargs.get('publication_id'))
        form_fields = UniCMSFormSerializer.serialize(form)
        return Response(form_fields)
