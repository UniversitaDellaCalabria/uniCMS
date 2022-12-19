from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from cms.api.utils import check_user_permission_on_object
from cms.contexts.models_abstract import AbstractLockable
from cms.medias.models import Media
from cms.templates.models import (CMS_LINKS_LABELS,
                                  ActivableModel,
                                  CreatedModifiedBy,
                                  SortableModel,
                                  TimeStampedModel)


class Carousel(ActivableModel, TimeStampedModel, CreatedModifiedBy,
               AbstractLockable):
    name = models.CharField(max_length=160)
    description = models.TextField(max_length=2048)

    class Meta:
        ordering = ['name']
        verbose_name_plural = _("Carousels")

    def get_items(self, lang=settings.LANGUAGE):
        items = []
        for i in self.carouselitem_set.filter(is_active=True).order_by('order'):
            if not i.is_published: continue
            i.links = i.get_links(lang)
            items.append(i.localized(lang=lang))
        return items

    def __str__(self):
        return self.name


class CarouselItem(ActivableModel, TimeStampedModel,
                   SortableModel, CreatedModifiedBy):
    carousel = models.ForeignKey(Carousel,
                                 on_delete=models.CASCADE)
    image = models.ForeignKey(Media,
                              on_delete=models.PROTECT,
                              related_name="image")
    mobile_image = models.ForeignKey(Media,
                                     on_delete=models.PROTECT,
                                     blank=True, null=True,
                                     related_name="mobile_image")
    pre_heading = models.CharField(
        max_length=120, blank=True, default='', help_text=_('Pre Heading')
    )
    heading = models.CharField(
        max_length=120, blank=True, default='', help_text=_('Heading')
    )

    # hopefully markdown here!
    description = models.TextField(default='', blank=True)
    date_start = models.DateTimeField(blank=True, null=True)
    date_end = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name_plural = _("Carousel Items")

    def get_links(self, lang=settings.LANGUAGE):
        links = []
        for i in self.carouselitemlink_set.filter(is_active=True).order_by('order'):
            links.append(i.localized(lang=lang))
        return links

    def localized(self, lang=settings.LANGUAGE):
        i18n = CarouselItemLocalization.objects.filter(carousel_item=self,
                                                       language=lang,
                                                       is_active=True)\
                                                .first()
        if i18n:
            self.heading = i18n.heading
            self.pre_heading = i18n.pre_heading
            self.description = i18n.description
        return self

    def is_lockable_by(self, user):
        item = self.carousel
        permission = check_user_permission_on_object(user=user, obj=item)
        return permission['granted']

    @property
    def is_published(self) -> bool:
        now = timezone.localtime()
        if self.date_start and self.date_start > now: return False
        if self.date_end and self.date_end <= now: return False
        return True

    def __str__(self):
        return '[{}] {}'.format(self.carousel, self.heading)


class CarouselItemLocalization(ActivableModel,
                               TimeStampedModel, SortableModel,
                               CreatedModifiedBy):
    carousel_item = models.ForeignKey(CarouselItem,
                                      on_delete=models.CASCADE)
    language = models.CharField(choices=settings.LANGUAGES, max_length=12, default='en')
    pre_heading = models.CharField(
        max_length=120, blank=True, default='', help_text=_('Pre Heading')
    )
    heading = models.CharField(
        max_length=120, blank=True, default='', help_text=_('Heading')
    )

    # hopefully markdown here!
    description = models.TextField(blank=True, default='')

    class Meta:
        verbose_name_plural = _("Carousel Item Localization")

    def is_lockable_by(self, user):
        item = self.carousel_item.carousel
        permission = check_user_permission_on_object(user=user, obj=item)
        return permission['granted']

    def __str__(self):
        return '{} {}'.format(self.carousel_item, self.language)


class CarouselItemLink(ActivableModel, TimeStampedModel, SortableModel,
                       CreatedModifiedBy):
    carousel_item = models.ForeignKey(CarouselItem,
                                      on_delete=models.CASCADE)
    title_preset = models.CharField(choices=CMS_LINKS_LABELS,
                                    default='custom',
                                    max_length=33)
    title = models.CharField(max_length=120, blank=True, default='', help_text=_('Title'))
    url = models.CharField(max_length=2048)

    class Meta:
        verbose_name_plural = _("Carousel Item Links")

    def get_title(self):
        labels_dict = dict(CMS_LINKS_LABELS)
        return self.title if self.title_preset == 'custom' else labels_dict[self.title_preset]

    def localized(self, lang=settings.LANGUAGE):
        i18n = CarouselItemLinkLocalization.objects.filter(carousel_item_link=self,
                                                           language=lang,
                                                           is_active=True)\
                                                    .first()
        if i18n:
            self.title = i18n.title
            self.url = i18n.url
        return self

    def is_lockable_by(self, user):
        item = self.carousel_item.carousel
        permission = check_user_permission_on_object(user=user, obj=item)
        return permission['granted']

    def __str__(self):
        return '{} {}'.format(self.carousel_item, self.url)


class CarouselItemLinkLocalization(ActivableModel, TimeStampedModel,
                                   SortableModel, CreatedModifiedBy):
    carousel_item_link = models.ForeignKey(CarouselItemLink,
                                           on_delete=models.CASCADE)
    language = models.CharField(choices=settings.LANGUAGES, max_length=12, default='en')
    title = models.CharField(max_length=120, blank=True, default='', help_text=_('Title'))
    url = models.CharField(max_length=2048)

    class Meta:
        verbose_name_plural = _("Carousel Item Links")

    def is_lockable_by(self, user):
        item = self.carousel_item_link.carousel_item.carousel
        permission = check_user_permission_on_object(user=user, obj=item)
        return permission['granted']

    def __str__(self):
        return '{} {}'.format(self.carousel_item_link.carousel_item.carousel,
                              self.carousel_item_link.url)
