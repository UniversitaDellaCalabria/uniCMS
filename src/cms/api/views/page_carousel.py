

from cms.pages.models import *
from cms.pages.serializers import *

from .. views.page import PageRelatedObject, PageRelatedObjectList


class PageCarouselList(PageRelatedObjectList):
    """
    """
    description = ""
    search_fields = ['block__name']
    serializer_class = PageCarouselSerializer

    def get_queryset(self):
        """
        """
        super().get_queryset()
        items = PageCarousel.objects.filter(page=self.page)
        return items


class PageCarouselView(PageRelatedObject):
    """
    """
    description = ""
    serializer_class = PageCarouselSerializer

    def get_queryset(self):
        """
        """
        super().get_queryset()
        items = PageCarousel.objects.filter(pk=self.pk, page=self.page)
        return items
