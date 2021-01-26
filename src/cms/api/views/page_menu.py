from cms.pages.models import *
from cms.pages.serializers import *

from .. views.page import PageRelatedObject, PageRelatedObjectList


class PageMenuList(PageRelatedObjectList):
    """
    """
    description = ""
    search_fields = ['menu__name']
    serializer_class = PageMenuSerializer

    def get_queryset(self):
        """
        """
        super().get_data()
        items = PageMenu.objects.filter(page=self.page)
        return items


class PageMenuView(PageRelatedObject):
    """
    """
    description = ""
    serializer_class = PageMenuSerializer

    def get_queryset(self):
        """
        """
        super().get_data()
        items = PageMenu.objects.filter(pk=self.pk, page=self.page)
        return items
