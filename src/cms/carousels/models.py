from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from cms.contexts.models import CreatedModifiedBy
from cms.contexts.models_abstract import AbstractLockable
from cms.medias.models import Media
from cms.templates.models import (CMS_LINKS_LABELS,
                                  ActivableModel,
                                  SortableModel,
                                  TimeStampedModel)


class Carousel(ActivableModel, TimeStampedModel, CreatedModifiedBy,
               AbstractLockable):
    name = models.CharField(max_length=160, blank=False,
                            null=False, unique=False)
    description = models.TextField(max_length=2048,
                                   null=False, blank=False)

    class Meta:
        ordering = ['name']
        verbose_name_plural = _("Carousels")

    def get_items(self, lang=settings.LANGUAGE):
        items = []
        for i in self.carouselitem_set.filter(carousel=self,
                                              is_active=True,).order_by('order'):
            items.append(i.localized(lang=lang))
        return items

    def __str__(self):
        return self.name


class CarouselItem(ActivableModel, TimeStampedModel,
                   SortableModel, CreatedModifiedBy):
    carousel = models.ForeignKey(Carousel,
                                 on_delete=models.CASCADE)
    image = models.ForeignKey(Media, on_delete=models.CASCADE)
    pre_heading = models.CharField(max_length=120, blank=True, null=True,
                                   help_text=_("Pre Heading"))
    heading = models.CharField(max_length=120, blank=True, null=True,
                               help_text=_("Heading"))

    # hopefully markdown here!
    description = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name_plural = _("Carousel Items")

    def get_links(self):
        return self.carouselitemlink_set.filter(is_active=True)

    def localized(self, lang=settings.LANGUAGE):
        i18n = CarouselItemLocalization.objects.filter(carousel_item=self,
                                                       language=lang).first()
        if i18n:
            self.heading = i18n.heading
            self.pre_heading = i18n.pre_heading
            self.description = i18n.description
        return self

    def __str__(self):
        return '{} {}'.format(self.carousel, self.heading)


class CarouselItemLocalization(ActivableModel,
                               TimeStampedModel, SortableModel,
                               CreatedModifiedBy):
    carousel_item = models.ForeignKey(CarouselItem,
                                      on_delete=models.CASCADE)
    language = models.CharField(choices=settings.LANGUAGES,
                                max_length=12, null=False,blank=False,
                                default='en')
    pre_heading = models.CharField(max_length=120, blank=True, null=True,
                                   help_text=_("Pre Heading"))
    heading = models.CharField(max_length=120, blank=True, null=True,
                               help_text=_("Heading"))

    # hopefully markdown here!
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = _("Carousel Item Localization")

    def __str__(self):
        return '{} {}'.format(self.carousel_item, self.language)


class CarouselItemLink(ActivableModel, TimeStampedModel, SortableModel,
                       CreatedModifiedBy):
    carousel_item = models.ForeignKey(CarouselItem,
                                      on_delete=models.CASCADE)
    title_preset = models.CharField(choices=CMS_LINKS_LABELS,
                                    default='custom',
                                    max_length=33)
    title = models.CharField(max_length=120, blank=True, null=True,
                             help_text=_("Title"))
    url = models.CharField(max_length=2048)

    class Meta:
        verbose_name_plural = _("Carousel Item Links")

    def get_title(self):
        return self.title if self.title_preset == 'custom' else self.title_preset

    def __str__(self):
        return '{} {}'.format(self.carousel_item, self.url)


class CarouselItemLinkLocalization(ActivableModel, TimeStampedModel,
                                   SortableModel, CreatedModifiedBy):
    carousel_item_link = models.ForeignKey(CarouselItemLink,
                                           on_delete=models.CASCADE)
    language = models.CharField(choices=settings.LANGUAGES,
                                max_length=12, null=False,blank=False,
                                default='en')
    title = models.CharField(max_length=120, blank=True, null=True,
                             help_text=_("Title"))

    class Meta:
        verbose_name_plural = _("Carousel Item Links")

    def __str__(self):
        return '{} {}'.format(self.carousel_item_link.carousel_item.carousel,
                              self.carousel_item_link.url)
