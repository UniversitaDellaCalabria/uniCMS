import logging

from django.db import models
from django.utils import timezone
from django.utils.module_loading import import_string
from django.utils.translation import gettext_lazy as _

from cms.contexts.models import *
from cms.contexts.models_abstract import AbstractLockable

from cms.carousels.models import Carousel

from cms.medias.models import Media, MediaCollection
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


class AbstractDraftable(models.Model):
    draft_of = models.IntegerField(null=True, blank=True)

    def toggleState(self, force_actual_state=''):
        actual_state = force_actual_state or self.state
        if self.draft_of:
            published = self.__class__.objects.filter(pk=self.draft_of).first()
            # if not published:
            # self.message_user(request,
            # "Draft missed its parent page ... ",
            # level = messages.ERROR)
            if published and published.webpath == self.webpath:
                published.is_active = False
                published.save()
            self.draft_of = None
        if actual_state == 'draft':
            self.state = 'published'
            self.is_active = True
        else:
            self.state = 'draft'
        self.save()

    class Meta:
        abstract = True


class AbstractPublicable(models.Model):

    @property
    def is_publicable(self) -> bool:
        now = timezone.localtime()
        result = False
        if self.is_active and self.date_start <= now :
            result = True
        if getattr(self, 'state', False) != 'published':
            result = False
        if self.date_end and self.date_end <= now:
            result = False
        return result

    class Meta:
        abstract = True


class Page(TimeStampedModel, ActivableModel, AbstractDraftable,
           AbstractPublicable, CreatedModifiedBy, AbstractLockable):
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
                                   help_text=_("Description "
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

        # query_params = dict(is_active=True)
        query_params = {}
        if section:
            query_params['section'] = section

        # get all page blocks (if section, filter by section)
        page_blocks = PageBlock.objects.filter(page=self,
                                               **query_params).\
            order_by('section', 'order').\
            values_list('order', 'block__pk', 'section',
                        'block__is_active', 'is_active')
        blocks_list = []
        excluded_blocks_list = []
        # for every page block, check if it's active and if
        # relative block is active and populate two lists
        # blocks_list = []
        # excluded_blocks_list = []
        # enumerating block position in same section order level
        # (multiple blocks with same order value in same section!)
        for (count, block) in enumerate(page_blocks):
            block = list(block)
            page_block_is_active = block.pop()
            block_is_active = block.pop()
            block = tuple(block)
            if block_is_active and page_block_is_active:
                blocks_list.append((block, count))
            elif not page_block_is_active:
                excluded_blocks_list.append(block)
        # get all active template blocks
        template_blocks = self.base_template.\
            pagetemplateblock_set.\
            filter(**query_params).\
            filter(is_active=True).\
            order_by('section', 'order').\
            values_list('order', 'block__pk', 'section')

        # populate a list with block params and enumerate value
        # for every section order position
        template_blocks_list = []
        for (count, block) in enumerate(template_blocks):
            template_blocks_list.append((block, count))

        for exc_block in excluded_blocks_list:
            for tpl_block in template_blocks_list:
                if tpl_block[0] == exc_block:
                    template_blocks_list.remove(tpl_block)
                    break

        # populate a set excluding template blocks existing in page_blocks
        # (same active blocks in same section and same order position!)
        order_pk = set()
        for i in chain(blocks_list, template_blocks_list):
            order_pk.add(i)
        ordered = list(order_pk)
        ordered.sort(key=lambda x:x[0][0])
        _blocks = []
        # add a on-the-fly section attribute on the blocks ...
        for item in ordered:
            block = item[0]
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

    def get_media_collections(self):
        if getattr(self, '_media_collections', None): # pragma: no cover
            return self._media_collections
        self._media_collections = PageMediaCollection.objects.filter(page=self,
                                                                     is_active=True,
                                                                     collection__is_active=True).\
            order_by('order')
        return self._media_collections

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

    def get_headings(self):
        if getattr(self, '_headings', None): # pragma: no cover
            return self._headings
        self._headings = PageHeading.objects.filter(page=self,
                                                    is_active=True).\
            order_by('order')
        return self._headings

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

    def is_localizable_by(self, user=None):
        if not user: return False
        # check if user has EditorialBoard editor permissions on object
        # and check for locks on webpath
        webpath = self.webpath
        webpath_perms = webpath.is_localizable_by(user=user)
        if not webpath_perms: return False
        # check for locks on object
        return EditorialBoardLockUser.check_for_locks(self, user)

    def is_editable_by(self, user=None):
        if not user: return False
        # check if user has EditorialBoard editor permissions on object
        # and check for locks on webpath
        webpath = self.webpath
        webpath_perms = webpath.is_editable_by(user=user, obj=self)
        if not webpath_perms: return False
        # check for locks on object
        return EditorialBoardLockUser.check_for_locks(self, user)

    def is_publicable_by(self, user=None):
        if not user: return False
        # check if user has EditorialBoard editor permissions on object
        # and check for locks on webpath
        webpath = self.webpath
        webpath_perms = webpath.is_publicable_by(user=user, obj=self)
        if not webpath_perms: return False
        # check for locks on object
        return EditorialBoardLockUser.check_for_locks(self, user)

    def is_lockable_by(self, user):
        return True if self.is_editable_by(user) else False

    def __str__(self):
        return '{} [{}]'.format(self.name, self.state)


class PageCarousel(SectionAbstractModel, ActivableModel, SortableModel,
                   TimeStampedModel, CreatedModifiedBy):
    page = models.ForeignKey(Page, null=False, blank=False,
                             on_delete=models.CASCADE)
    carousel = models.ForeignKey(Carousel, null=False, blank=False,
                                 on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = _("Page Carousel")

    def __str__(self):
        return '{} {} :{}'.format(self.page, self.carousel,
                                  self.section or '#')


class PageLocalization(TimeStampedModel, ActivableModel, CreatedModifiedBy):
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
                TimeStampedModel, CreatedModifiedBy):
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
               TimeStampedModel, CreatedModifiedBy):
    page = models.ForeignKey(Page, null=False, blank=False,
                             on_delete=models.CASCADE)
    menu = models.ForeignKey(NavigationBar, null=False, blank=False,
                             on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = _("Page Navigation Bars")

    def __str__(self):
        return '{} {} :{}'.format(self.page, self.menu,
                                  self.section or '#')


class PageBlock(ActivableModel, SectionAbstractModel, SortableModel,
                TimeStampedModel, CreatedModifiedBy):
    page = models.ForeignKey(Page, null=False, blank=False,
                             on_delete=models.CASCADE)
    block = models.ForeignKey(TemplateBlock, null=False, blank=False,
                              limit_choices_to={'is_active': True},
                              on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = _("Page Block")

    def __str__(self):
        return '{} {} {}:{}'.format(self.page,
                                    self.block.name,
                                    self.order or '#',
                                    self.section or '#')


class PageRelated(TimeStampedModel, SortableModel, ActivableModel,
                  CreatedModifiedBy):
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


class PageLink(TimeStampedModel, SortableModel, CreatedModifiedBy):
    page = models.ForeignKey(Page, null=False, blank=False,
                             on_delete=models.CASCADE)
    name = models.CharField(max_length=256, null=False, blank=False)
    url = models.URLField(help_text=_("url"))

    class Meta:
        verbose_name_plural = _("Page Links")

    def __str__(self):
        return '{} {}'.format(self.page, self.name)


class PagePublication(TimeStampedModel, SortableModel, ActivableModel,
                      CreatedModifiedBy):
    page = models.ForeignKey(Page, null=False, blank=False,
                             # related_name='container_page',
                             on_delete=models.CASCADE)
    publication = models.ForeignKey('cmspublications.Publication',
                                    null=False, blank=False,
                                    on_delete=models.CASCADE)
    # related_name="publication_content")

    class Meta:
        verbose_name_plural = _("Publication Contents")

    def __str__(self):
        return '{} {}'.format(self.page, self.publication)


class PageMediaCollection(SectionAbstractModel, ActivableModel, SortableModel,
                          TimeStampedModel, CreatedModifiedBy):
    page = models.ForeignKey(Page, on_delete=models.CASCADE)
    collection = models.ForeignKey(MediaCollection,
                                   on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = _("Page Media Collection")

    def __str__(self):
        return '{} {}'.format(self.page, self.collection)


class PageHeading(SectionAbstractModel, ActivableModel, SortableModel,
                  TimeStampedModel, CreatedModifiedBy):
    page = models.ForeignKey(Page, null=False, blank=False,
                             on_delete=models.CASCADE)
    title = models.CharField(max_length=256, null=False, blank=False)
    description = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name_plural = _("Page Headings")

    def translate_as(self, lang):
        """
        returns translation if available
        """
        trans = PageHeadingLocalization.objects.filter(heading=self,
                                                       language=lang,
                                                       is_active=True).first()
        if trans:
            self.title = trans.title
            self.description = trans.description

    def __str__(self):
        return '{} {}'.format(self.page, self.title)


class PageHeadingLocalization(ActivableModel,
                              TimeStampedModel, SortableModel,
                              CreatedModifiedBy):
    heading = models.ForeignKey(PageHeading, on_delete=models.CASCADE)
    language = models.CharField(choices=settings.LANGUAGES,
                                max_length=12, null=False,blank=False,
                                default='en')
    title = models.CharField(max_length=256, null=False, blank=False)
    description = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name_plural = _("Page Heading Localizations")

    def __str__(self):
        return '{} {}'.format(self.heading, self.language)
