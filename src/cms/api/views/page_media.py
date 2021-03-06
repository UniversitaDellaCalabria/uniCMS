from cms.pages.models import *
from cms.pages.serializers import *

from .. views.page import PageRelatedObject, PageRelatedObjectList


class PageMediaList(PageRelatedObjectList):
    """
    """
    description = ""
    search_fields = ['media__title', 'media__file', 'media_description']
    serializer_class = PageMediaSerializer

    def get_queryset(self):
        """
        """
        super().get_data()
        items = PageMedia.objects.filter(page=self.page)
        return items


class PageMediaView(PageRelatedObject):
    """
    """
    description = ""
    serializer_class = PageMediaSerializer

    def get_queryset(self):
        """
        """
        super().get_data()
        items = PageMedia.objects.filter(pk=self.pk, page=self.page)
        return items
