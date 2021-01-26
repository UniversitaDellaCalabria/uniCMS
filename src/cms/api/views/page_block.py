

from cms.pages.models import *
from cms.pages.serializers import *

from .. views.page import PageRelatedObject, PageRelatedObjectList


class PageBlockList(PageRelatedObjectList):
    """
    """
    description = ""
    search_fields = ['block__name']
    filterset_fields = ['is_active']
    serializer_class = PageBlockSerializer

    def get_queryset(self):
        """
        """
        super().get_data()
        items = PageBlock.objects.filter(page=self.page)
        return items


class PageBlockView(PageRelatedObject):
    """
    """
    description = ""
    serializer_class = PageBlockSerializer

    def get_queryset(self):
        """
        """
        super().get_data()
        items = PageBlock.objects.filter(pk=self.pk, page=self.page)
        return items
