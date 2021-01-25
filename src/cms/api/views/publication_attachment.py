from django.http import Http404

from rest_framework import filters, generics
from rest_framework.permissions import IsAdminUser

# from cms.api.serializers import PublicationSerializer


from cms.publications.models import PublicationAttachment
from cms.publications.serializers import PublicationAttachmentSerializer

from .. exceptions import LoggedPermissionDenied
from .. pagination import UniCmsApiPagination
from .. views.publication import PublicationRelatedObject, PublicationRelatedObjectList


class PublicationAttachmentList(PublicationRelatedObjectList):
    """
    """
    description = ""
    search_fields = ['name', 'file', 'descripion']
    serializer_class = PublicationAttachmentSerializer

    def get_queryset(self):
        """
        """
        pub_id = self.kwargs['publication_id']
        items = PublicationAttachment.objects.filter(publication__pk=pub_id)
        is_active = self.request.GET.get('is_active')
        if is_active:
            items = items.filter(is_active=is_active)
        return items


class PublicationAttachmentView(PublicationRelatedObject):
    """
    """
    description = ""
    serializer_class = PublicationAttachmentSerializer

    def get_queryset(self):
        """
        """
        pub_id = self.kwargs['publication_id']
        pk = self.kwargs['pk']
        attachments = PublicationAttachment.objects.filter(pk=pk,
                                                           publication__pk=pub_id)
        return attachments
