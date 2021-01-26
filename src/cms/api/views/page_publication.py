

from cms.pages.models import *
from cms.pages.serializers import *

from .. views.page import PageRelatedObject, PageRelatedObjectList


class PagePublicationList(PageRelatedObjectList):
    """
    """
    description = ""
    search_fields = ['block__name']
    serializer_class = PagePublicationSerializer

    def get_queryset(self):
        """
        """
        super().get_queryset()
        items = PagePublication.objects.filter(page=self.page)
        return items


class PagePublicationView(PageRelatedObject):
    """
    """
    description = ""
    serializer_class = PagePublicationSerializer

    def get_queryset(self):
        """
        """
        super().get_queryset()
        items = PagePublication.objects.filter(pk=self.pk, page=self.page)
        return items
