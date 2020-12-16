import logging

from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from django.utils.module_loading import import_string
from django.utils.text import slugify
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from cms.contexts.models import *
from cms.contexts.utils import sanitize_path
from cms.carousels.models import Carousel
from cms.medias import settings as cms_media_settings
from cms.medias.validators import *
from cms.menus.models import NavigationBar
from cms.templates.models import (CMS_TEMPLATE_BLOCK_SECTIONS,
                                  TemplateBlock,
                                  ActivableModel,
                                  PageTemplate,
                                  SectionAbstractModel,
                                  SortableModel,
                                  TimeStampedModel)

from taggit.managers import TaggableManager


logger = logging.getLogger(__name__)
PAGE_STATES = (('draft', _('Draft')),
               ('published', _('Published')),)

CMS_IMAGE_CATEGORY_SIZE = getattr(settings, 'CMS_IMAGE_CATEGORY_SIZE',
                                  cms_media_settings.CMS_IMAGE_CATEGORY_SIZE)


class AbstractDraftable(models.Model):
    draft_of = models.IntegerField(null=True, blank=True)

    class Meta:
        abstract = True


class AbstractPublicable(models.Model):

    @property
    def is_publicable(self) -> bool:
        now = timezone.localtime()
        result = False
        if self.is_active and \
           self.state == 'published' and \
           self.date_start <= now :
            result = True
        if self.date_end and self.date_end <= now:
            result = False
        return result
    
    class Meta:
        abstract = True


class Page(TimeStampedModel, ActivableModel, AbstractDraftable,
           AbstractPublicable, CreatedModifiedBy):
    name = models.CharField(max_length=160,
                            blank=False, null=False)
    webpath = models.ForeignKey(WebPath,
                                on_delete=models.CASCADE,
                                limit_choices_to={'is_active': True},)
    base_template = models.ForeignKey(PageTemplate,
                                      on_delete=models.CASCADE,
                                      limit_choices_to={'is_active': True},)
    description = models.TextField(null=True, blank=True,
                                    help_text=_("Description"
                                                "used for SEO."))
    date_start = models.DateTimeField()
    date_end = models.DateTimeField(null=True, blank=True)
    state = models.CharField(choices=PAGE_STATES, max_length=33,
                             default='draft')

    type = models.CharField(max_length=33,
                            default="standard",
                            choices=(('standard', _('Page')),
                                     ('home', _('Home Page'))))
    tags = TaggableManager()

    class Meta:
        verbose_name_plural = _("Pages")


    def get_blocks(self, section=None):
        query_params = dict(is_active=True)
        if section:
            query_params['section'] = section
        blocks = PageBlock.objects.filter(page=self,
                                          **query_params).\
                                   order_by('section', 'order').\
                                   values_list('order', 'block__pk')
        template_blocks = self.base_template.\
                            pagetemplateblock_set.\
                            filter(**query_params).\
                            order_by('section', 'order').\
                            values_list('order', 'block__pk')
        excluded_blocks = PageBlock.objects.filter(page=self,
                                                   is_active=False).\
                                   values_list('block__pk', flat=True)
        order_pk = []
        # CHECK concurrent ordering sorting
        for i in blocks:
            order_pk.append(i)
        for i in template_blocks:
            # check if a template blocks has not been disabled in the page
            if i[1] not in excluded_blocks:
                order_pk.append(i)
        ordered = sorted(order_pk)
        unique = []
        for i in ordered:
            if i[1] not in unique:
                unique.append(i)
        final_blocks = [TemplateBlock.objects.get(pk=v)
                        for k,v in unique]
        return final_blocks


    def delete(self, *args, **kwargs):
        PageRelated.objects.filter(related_page=self).delete()
        super(self.__class__, self).delete(*args, **kwargs)


    def save(self, *args, **kwargs):
        super(self.__class__, self).save(*args, **kwargs)

        for rel in PageRelated.objects.filter(page=self):
            if not PageRelated.objects.\
                    filter(page=rel.related_page, related_page=self):
                PageRelated.objects.\
                    create(page=rel.page, related_page=self,
                           is_active=True)

    def get_category_img(self):
        return [i.image_as_html() for i in self.category.all()]

    def __str__(self):
        return '{} {}'.format(self.name, self.state)


class PageCarousel(SectionAbstractModel, ActivableModel, SortableModel,
                   TimeStampedModel):
    page = models.ForeignKey(Page, null=False, blank=False,
                             on_delete=models.CASCADE)
    carousel = models.ForeignKey(Carousel, null=False, blank=False,
                                 on_delete=models.CASCADE)


    class Meta:
        verbose_name_plural = _("Page Carousel")

    def __str__(self):
        return '{} {} :{}'.format(self.page, self.carousel,
                                  self.section or '#')


class PageMenu(SectionAbstractModel, ActivableModel, SortableModel,
               TimeStampedModel):
    page = models.ForeignKey(Page, null=False, blank=False,
                             on_delete=models.CASCADE)
    menu = models.ForeignKey(NavigationBar, null=False, blank=False,
                             on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = _("Page Navigation Bars")

    def __str__(self):
        return '{} {} :{}'.format(self.page, self.menu,
                                  self.section or '#')


class PageBlock(ActivableModel, SectionAbstractModel, SortableModel):
    page = models.ForeignKey(Page, null=False, blank=False,
                             on_delete=models.CASCADE)
    block = models.ForeignKey(TemplateBlock, null=False, blank=False,
                              on_delete=models.CASCADE)
    class Meta:
        verbose_name_plural = _("Page Block")

    def __str__(self):
        return '{} {} {}:{}'.format(self.page,
                                    self.block.name,
                                    self.order or '#',
                                    self.section or '#')


class PageRelated(TimeStampedModel, SortableModel, ActivableModel):
    page = models.ForeignKey(Page, null=False, blank=False,
                             related_name='parent_page',
                             on_delete=models.CASCADE)
    related_page = models.ForeignKey(Page, null=False, blank=False,
                                     on_delete=models.CASCADE,
                                     related_name="related_page")

    class Meta:
        verbose_name_plural = _("Related Pages")
        unique_together = ("page", "related_page")

    def __str__(self):
        return '{} {}'.format(self.page, self.related_page)


class PageLink(TimeStampedModel):
    page = models.ForeignKey(Page, null=False, blank=False,
                             on_delete=models.CASCADE)
    name = models.CharField(max_length=256, null=False, blank=False)
    url = models.URLField(help_text=_("url"))

    class Meta:
        verbose_name_plural = _("Page Links")

    def __str__(self):
        return '{} {}'.format(self.page, self.name)


class Category(TimeStampedModel, CreatedModifiedBy):
    name        = models.CharField(max_length=160, blank=False,
                                   null=False, unique=False)
    description = models.TextField(max_length=1024,
                                   null=False, blank=False)
    image       = models.ImageField(upload_to="images/categories",
                                    null=True, blank=True,
                                    max_length=512,
                                    validators=[validate_file_extension,
                                                validate_file_size])

    class Meta:
        ordering = ['name']
        verbose_name_plural = _("Content Categories")

    def __str__(self):
        return self.name
    
    # now handled with hooks
    # def delete(self, *args, **kwargs):
        # remove_file(self.image.url)
        # super(self.cls, self).delete(*args, **kwargs)

    def image_as_html(self):
        res = ""
        try:
            res = f'<img width={CMS_IMAGE_CATEGORY_SIZE} src="{self.image.url}"/>'
        except ValueError as e:
            # *** ValueError: The 'image' attribute has no file associated with it.
            res = f"{settings.STATIC_URL}images/no-image.jpg"
        return mark_safe(res)

    image_as_html.short_description = _('Image of this Category')
    image_as_html.allow_tags = True
