from cms.pages.models import *
from cms.pages.serializers import *

from .. views.page import PageRelatedObject, PageRelatedObjectList


class PageLinkList(PageRelatedObjectList):
    """
    """
    description = ""
    search_fields = ['name', 'url']
    filterset_fields = ['created', 'modified']
    serializer_class = PageLinkSerializer

    def get_queryset(self):
        """
        """
        super().get_data()
        items = PageLink.objects.filter(page=self.page)
        return items


class PageLinkView(PageRelatedObject):
    """
    """
    description = ""
    serializer_class = PageLinkSerializer

    def get_queryset(self):
        """
        """
        super().get_data()
        items = PageLink.objects.filter(pk=self.pk, page=self.page)
        return items
