import logging

from django.db import models
from django.utils import timezone
from django.utils.module_loading import import_string
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from cms.contexts.models import *
from cms.carousels.models import Carousel
from cms.medias import settings as cms_media_settings
from cms.medias.models import Media
from cms.medias.validators import *
from cms.menus.models import NavigationBar
from cms.templates.models import (TemplateBlock,
                                  ActivableModel,
                                  PageTemplate,
                                  SectionAbstractModel,
                                  SortableModel,
                                  TimeStampedModel)

from itertools import chain
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
    title = models.CharField(max_length=256,
                             null=False, blank=False)
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

    def clean_related_caches(self):
        deleted = []
        for i in [k for k in self.__dict__.keys()]:
            for e in '_blocks_', '_pubs', '_carousels', '_medias', '_links':
                if e in i:
                    delattr(self, i)
                    deleted.append(i)
        logger.debug(f'Deleted from page {self}, these related caches: '
                     f'{"".join(deleted)}')

    def get_blocks(self, section=None):
        # something that caches ...
        if hasattr(self, f'_blocks_{section}'):
            return getattr(self, f'_blocks_{section}')
        #

        query_params = dict(is_active=True)
        if section:
            query_params['section'] = section
        blocks = PageBlock.objects.filter(page=self,
                                          **query_params,
                                          block__is_active=True).\
            order_by('section', 'order').\
            values_list('order', 'block__pk', 'section')
        excluded_blocks = PageBlock.objects.filter(page=self,
                                                   is_active=False).\
            values_list('block__pk', flat=True)
        template_blocks = self.base_template.\
            pagetemplateblock_set.\
            filter(**query_params).\
            exclude(pk__in=excluded_blocks).\
            order_by('section', 'order').\
            values_list('order', 'block__pk', 'section')
        order_pk = set()
        for i in chain(blocks, template_blocks):
            order_pk.add(i)
        ordered = list(order_pk)
        ordered.sort(key=lambda x:x[0])

        _blocks = []
        # add a on-the-fly section attribute on the blocks ...
        for block in ordered:
            _block = TemplateBlock.objects.get(pk=block[1])
            _block.section = block[2]
            _blocks.append(_block)

        if _blocks:
            # cache result ...
            setattr(self, f'_blocks_{section}', _blocks)

        return _blocks

    def get_blocks_placeholders(self):
        blocks = self.get_blocks()
        placeholders = [block for block in blocks
                        if 'PlaceHolderBlock' in
                        [i.__name__
                         for i in import_string(block.type).__bases__]]
        return placeholders

    def get_publications(self):
        if getattr(self, '_pubs', None): # pragma: no cover
            return self._pubs
        self._pubs = PagePublication.objects.filter(page=self,
                                                    is_active=True,
                                                    publication__is_active=True).\
            order_by('order')
        return self._pubs

    def get_carousels(self):
        if getattr(self, '_carousels', None): # pragma: no cover
            return self._carousels
        self._carousels = PageCarousel.objects.filter(page=self,
                                                      is_active=True,
                                                      carousel__is_active=True).\
            order_by('order')
        return self._carousels

    def get_medias(self):
        if getattr(self, '_medias', None): # pragma: no cover
            return self._medias
        self._medias = PageMedia.objects.filter(page=self,
                                                is_active=True,
                                                media__is_active=True).\
            order_by('order')
        return self._medias

    def get_menus(self):
        if getattr(self, '_menus', None):
            return self._menus
        self._menus = PageMenu.objects.filter(page=self,
                                              is_active=True,
                                              menu__is_active=True).\
            order_by('order')
        return self._menus

    def get_links(self):
        if getattr(self, '_links', None):
            return self._links
        self._links = PageLink.objects.filter(page=self).\
            order_by('order')
        return self._links

    def delete(self, *args, **kwargs):
        PageRelated.objects.filter(related_page=self).delete()
        super(self.__class__, self).delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        super(self.__class__, self).save(*args, **kwargs)

        # can't remember why I wrote this code ...!
        # for rel in PageRelated.objects.filter(page=self):
        # if not PageRelated.objects.\
        # filter(page=rel.related_page, related_page=self):
        # PageRelated.objects.\
        # create(page=rel.page, related_page=self,
        # is_active=True)

    def translate_as(self, lang):
        """
        returns translation if available
        """
        trans = PageLocalization.objects.filter(page=self,
                                                language=lang,
                                                is_active=True).first()
        if trans:
            self.title = trans.title

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


class PageLocalization(TimeStampedModel, ActivableModel,
                       CreatedModifiedBy):
    title = models.CharField(max_length=256,
                             null=False, blank=False)
    page = models.ForeignKey(Page,
                             null=False, blank=False,
                             on_delete=models.CASCADE)
    language = models.CharField(choices=settings.LANGUAGES,
                                max_length=12, null=False,blank=False,
                                default='en')

    class Meta:
        verbose_name_plural = _("Page Localizations")

    def __str__(self):
        return '{} {}'.format(self.page, self.language)


class PageMedia(SectionAbstractModel, ActivableModel, SortableModel,
                TimeStampedModel):
    page = models.ForeignKey(Page, null=False, blank=False,
                             on_delete=models.CASCADE)
    media = models.ForeignKey(Media, null=False, blank=False,
                              on_delete=models.CASCADE)
    url = models.URLField(help_text=_("url"),
                          null=True, blank=True)

    class Meta:
        verbose_name_plural = _("Page Medias")

    def __str__(self):
        return '{} {} :{}'.format(self.page, self.media,
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


class PageLink(TimeStampedModel, SortableModel):
    page = models.ForeignKey(Page, null=False, blank=False,
                             on_delete=models.CASCADE)
    name = models.CharField(max_length=256, null=False, blank=False)
    url = models.URLField(help_text=_("url"))

    class Meta:
        verbose_name_plural = _("Page Links")

    def __str__(self):
        return '{} {}'.format(self.page, self.name)


class PagePublication(TimeStampedModel, SortableModel, ActivableModel):
    page = models.ForeignKey(Page, null=False, blank=False,
                             related_name='container_page',
                             on_delete=models.CASCADE)
    publication = models.ForeignKey('cmspublications.Publication',
                                    null=False, blank=False,
                                    on_delete=models.CASCADE,
                                    related_name="publication_content")

    class Meta:
        verbose_name_plural = _("Publication Contents")

    def __str__(self):
        return '{} {}'.format(self.page, self.publication)


class Category(TimeStampedModel, CreatedModifiedBy):
    name = models.CharField(max_length=160, blank=False,
                            null=False, unique=False)
    description = models.TextField(max_length=1024,
                                   null=False, blank=False)
    image = models.ImageField(upload_to="images/categories",
                              null=True, blank=True,
                              max_length=512,
                              validators=[validate_file_extension,
                                          validate_file_size])

    class Meta:
        ordering = ['name']
        verbose_name_plural = _("Content Categories")

    def __str__(self):
        return self.name

    def image_as_html(self):
        res = ""
        try:
            res = f'<img width={CMS_IMAGE_CATEGORY_SIZE} src="{self.image.url}"/>'
        except ValueError:  # pragma: no cover
            # *** ValueError: The 'image' attribute has no file associated with it.
            res = f"{settings.STATIC_URL}images/no-image.jpg"
        return mark_safe(res) # nosec

    image_as_html.short_description = _('Image of this Category')
    image_as_html.allow_tags = True
