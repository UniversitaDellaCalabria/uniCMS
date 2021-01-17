from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from cms.contexts.models import *
from cms.medias.models import Media, MediaCollection, AbstractMedia
from cms.pages.models import AbstractPublicable, PAGE_STATES
from cms.templates.models import (TemplateBlock,
                                  ActivableModel,
                                  SectionAbstractModel,
                                  SortableModel,
                                  TimeStampedModel)
from markdown import markdown
from markdownify import markdownify
from taggit.managers import TaggableManager

from . settings import *


class AbstractPublication(TimeStampedModel, ActivableModel):
    CONTENT_TYPES = (('markdown', 'markdown'),
                     ('html', 'html'))

    title = models.CharField(max_length=256,
                             null=False, blank=False,
                             help_text=_("Heading, Headline"))

    subheading = models.TextField(max_length=1024,
                                  null=True,blank=True,
                                  help_text=_("Strap line (press)"))
    content = models.TextField(null=True,blank=True,
                               help_text=_('Content'))
    content_type = models.CharField(choices=CONTENT_TYPES,
                                    null=False, blank=False,
                                    max_length=33,
                                    default='markdown')
    presentation_image = models.ForeignKey(Media, null=True, blank=True,
                                           on_delete=models.CASCADE)
    state = models.CharField(choices=PAGE_STATES,
                             max_length=33,
                             default='draft')
    date_start = models.DateTimeField()
    date_end = models.DateTimeField()
    category = models.ManyToManyField('cmspages.Category')

    note = models.TextField(null=True,blank=True,
                            help_text=_('Editorial Board notes'))

    class Meta:
        abstract = True
        indexes = [
           models.Index(fields=['title']),
        ]


class Publication(AbstractPublication, AbstractPublicable,
                  CreatedModifiedBy):
    slug = models.SlugField(null=True, blank=True)
    tags = TaggableManager()
    relevance = models.IntegerField(default=0, blank=True)

    class Meta:
        verbose_name_plural = _("Publications")

    def serialize(self):
        return {'slug': self.slug,
                'image': self.image_url(),
                'title': self.title,
                'published': self.date_start,
                'subheading': self.subheading,
                'categories': (i.name for i in self.categories),
                'tags': (i.name for i in self.tags.all()),
                'published_in': (f'{i.webpath.site}{i.webpath.fullpath}'
                                 for i in self.publicationcontext_set.all())}

    def active_translations(self):
        return PublicationLocalization.objects.filter(publication=self,
                                                      is_active=True)

    def image_url(self):
        if self.presentation_image:
            image_path = self.presentation_image.file
        else: # pragma: no cover
            image_path = self.category.first().image
        return sanitize_path(f'{settings.MEDIA_URL}/{image_path}')

    @property
    def categories(self):
        return self.category.all()

    @property
    def related_publications(self):
        related = PublicationRelated.objects.filter(publication=self,
                                                    related__is_active=True)
        return [i for i in related if i.related.is_publicable]

    @property
    def related_contexts(self):
        return PublicationContext.objects.filter(publication=self,
                                                 webpath__is_active=True)

    @property
    def first_available_url(self):
        pubcontx = PublicationContext.objects.filter(publication=self,
                                                     webpath__is_active=True)
        if pubcontx:
            return pubcontx.first().url

    @property
    def related_links(self):
        return self.publicationlink_set.all()

    @property
    def related_galleries(self):
        return PublicationGallery.objects.filter(publication=self,
                                                 is_active=True)

    def translate_as(self, lang):
        """
        returns translation if available
        """
        trans = PublicationLocalization.objects.filter(publication=self,
                                                       language=lang,
                                                       is_active=True).first()
        if trans:
            self.title = trans.title
            self.subheading = trans.subheading
            self.content = trans.content

    @property
    def available_in_languages(self) -> list:
        return [(i, i.get_language_display())
                for i in
                PublicationLocalization.objects.filter(publication=self,
                                                       is_active=True)]

    def title2slug(self):
        return slugify(self.title)

    def content_save_switch(self):
        old_content_type = None
        if self.pk:
            current_entry = self.__class__.objects.filter(pk=self.pk).first()
            if current_entry:
                old_content_type = current_entry.content_type

        if all((old_content_type,
                self.content,
                self.pk,
                self.content_type != old_content_type)):

            # markdown to html
            if old_content_type == 'html':
                self.content = markdownify(self.content)
            elif old_content_type == 'markdown':
                self.content = markdown(self.content)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.title2slug()
        self.content_save_switch()
        super(self.__class__, self).save(*args, **kwargs)

    def get_attachments(self):
        return PublicationAttachment.objects.filter(publication=self,
                                                    is_active=True).\
                                             order_by('order')

    def get_publication_contexts(self, webpath=None):
        qdict = dict(publication=self, is_active=True)
        if webpath:
            qdict['webpath'] = webpath
        pub_context = PublicationContext.objects.filter(**qdict)
        return pub_context

    def get_publication_context(self, webpath=None):
        return self.get_publication_contexts(webpath=webpath).first()

    def url(self, webpath=None):
        pub_context = self.get_publication_context(webpath=webpath)
        if not pub_context: return ''
        return pub_context.url

    def get_url_list(self, webpath=None, category_name=None):
        pub_context = self.get_publication_context(webpath=webpath)
        if not pub_context: return ''
        return pub_context.get_url_list(category_name=category_name)

    @property
    def html_content(self):
        content = ''
        if self.content_type == 'markdown':
            content = markdown(self.content)
        elif self.content_type == 'html':
            content = self.content
        return content

    def __str__(self):
        return '{} [{}]'.format(self.title, self.state)


class PublicationContext(TimeStampedModel, ActivableModel,
                         SectionAbstractModel, SortableModel,
                         CreatedModifiedBy):
    publication = models.ForeignKey(Publication, null=False, blank=False,
                                    on_delete=models.CASCADE)
    webpath = models.ForeignKey(WebPath, on_delete=models.CASCADE)
    in_evidence_start = models.DateTimeField(null=True,blank=True)
    in_evidence_end = models.DateTimeField(null=True,blank=True)

    class Meta:
        verbose_name_plural = _("Publication Contexts")

    @property
    def path_prefix(self):
        return getattr(settings, 'CMS_PUBLICATION_VIEW_PREFIX_PATH',
                                 CMS_PUBLICATION_VIEW_PREFIX_PATH)

    def get_url_list(self, category_name=None):
        list_prefix = getattr(settings, 'CMS_PUBLICATION_LIST_PREFIX_PATH',
                              CMS_PUBLICATION_LIST_PREFIX_PATH)
        url = sanitize_path(f'{self.webpath.get_full_path()}/{list_prefix}')
        if category_name:
            url += f'/?category_name={category_name}'
        return sanitize_path(url)

    @property
    def url(self):
        url = f'{self.webpath.get_full_path()}{self.path_prefix}/{self.publication.slug}'
        return sanitize_path(url)

    @property
    def name(self):
        return self.publication.title

    def translate_as(self, *args, **kwargs):
        self.publication.translate_as(*args, **kwargs)

    def serialize(self):
        result = self.publication.serialize()
        result['path'] = self.url
        return result

    def __str__(self):
        return '{} {}'.format(self.publication, self.webpath)


class PublicationLink(TimeStampedModel):
    publication = models.ForeignKey(Publication, null=False, blank=False,
                                    on_delete=models.CASCADE)
    name = models.CharField(max_length=256, null=False, blank=False)
    url = models.URLField(help_text=_("url"))

    class Meta:
        verbose_name_plural = _("Publication Links")

    def __str__(self):
        return '{} {}'.format(self.publication, self.name)


class PublicationBlock(SectionAbstractModel,TimeStampedModel,
                       ActivableModel, SortableModel):
    publication = models.ForeignKey(Publication, null=False, blank=False,
                                    on_delete=models.CASCADE)
    block = models.ForeignKey(TemplateBlock, null=False, blank=False,
                              on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = _("Publication Page Block")

    def __str__(self):
        return '{} {} {}:{}'.format(self.publication,
                                    self.block.name,
                                    self.order or '#',
                                    self.section or '#')


class PublicationGallery(TimeStampedModel, ActivableModel, SortableModel):
    publication = models.ForeignKey(Publication,
                                    on_delete=models.CASCADE)
    collection = models.ForeignKey(MediaCollection,
                                   on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = _("Publication Image Gallery")

    def __str__(self):
        return '{} {}'.format(self.publication, self.collection)


class PublicationRelated(TimeStampedModel, SortableModel, ActivableModel):
    publication = models.ForeignKey(Publication, null=False, blank=False,
                                    related_name='parent_page',
                                    on_delete=models.CASCADE)
    related = models.ForeignKey(Publication, null=False, blank=False,
                                on_delete=models.CASCADE,
                                related_name="related_page")

    class Meta:
        verbose_name_plural = _("Related Publications")
        unique_together = ("publication", "related")

    def __str__(self):
        return '{} {}'.format(self.publication, self.related)


def publication_attachment_path(instance, filename): # pragma: no cover
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'publications_attachments/{}/{}'.format(instance.publication.pk,
                                                   filename)


class PublicationAttachment(TimeStampedModel, SortableModel, ActivableModel,
                            AbstractMedia):

    publication = models.ForeignKey(Publication, null=False, blank=False,
                                    related_name='page_attachment',
                                    on_delete=models.CASCADE)
    name = models.CharField(max_length=60, blank=True, null=True,
                            help_text=_("Specify the container "
                                        "section in the template where "
                                        "this block would be rendered."))
    file = models.FileField(upload_to=publication_attachment_path)
    description = models.TextField()

    class Meta:
        verbose_name_plural = _("Publication Attachments")

    def __str__(self):
        return '{} {} ({})'.format(self.publication, self.name,
                                   self.file_type)


class PublicationLocalization(TimeStampedModel, ActivableModel,
                              CreatedModifiedBy):
    title = models.CharField(max_length=256,
                             null=False, blank=False,
                             help_text=_("Heading, Headline"))
    publication = models.ForeignKey(Publication,
                                    null=False, blank=False,
                                    on_delete=models.CASCADE)
    language = models.CharField(choices=settings.LANGUAGES,
                                max_length=12, null=False,blank=False,
                                default='en')
    subheading = models.TextField(max_length=1024,
                                  null=True,blank=True,
                                  help_text=_("Strap line (press)"))
    content = models.TextField(null=True,blank=True,
                               help_text=_('Content'))

    class Meta:
        verbose_name_plural = _("Publication Localizations")

    def __str__(self):
        return '{} {}'.format(self.publication, self.language)
