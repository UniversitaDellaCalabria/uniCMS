

from cms.pages.models import *
from cms.pages.serializers import *

from .. views.page import PageRelatedObject, PageRelatedObjectList


class PageRelatedList(PageRelatedObjectList):
    """
    """
    description = ""
    search_fields = ['block__name']
    serializer_class = PageRelatedSerializer

    def get_queryset(self):
        """
        """
        super().get_queryset()
        items = PageRelated.objects.filter(page=self.page)
        return items


class PageRelatedView(PageRelatedObject):
    """
    """
    description = ""
    serializer_class = PageRelatedSerializer

    def get_queryset(self):
        """
        """
        super().get_queryset()
        items = PageRelated.objects.filter(pk=self.pk, page=self.page)
        return items
