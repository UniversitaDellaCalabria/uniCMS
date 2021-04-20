from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from cms.api.utils import check_user_permission_on_object

from cms.contexts.models import *
from cms.contexts.models_abstract import AbstractLockable

from django.utils.safestring import mark_safe

from cms.medias import settings as cms_media_settings
from cms.medias.models import Media, MediaCollection, AbstractMedia
from cms.medias.validators import *

from cms.pages.models import AbstractPublicable

from cms.templates.models import (TemplateBlock,
                                  ActivableModel,
                                  SectionAbstractModel,
                                  SortableModel,
                                  TimeStampedModel)
from markdown import markdown
from markdownify import markdownify
from taggit.managers import TaggableManager

from . settings import *


CMS_IMAGE_CATEGORY_SIZE = getattr(settings, 'CMS_IMAGE_CATEGORY_SIZE',
                                  cms_media_settings.CMS_IMAGE_CATEGORY_SIZE)


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


class AbstractPublication(TimeStampedModel, ActivableModel):
    CONTENT_TYPES = (('markdown', 'markdown'),
                     ('html', 'html'))

    name = models.CharField(max_length=256,
                            null=False, blank=False)
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
                                    default='html')
    presentation_image = models.ForeignKey(Media, null=True, blank=True,
                                           on_delete=models.CASCADE)
    # state = models.CharField(choices=PAGE_STATES,
    # max_length=33,
    # default='draft')
    # date_start = models.DateTimeField()
    # date_end = models.DateTimeField()
    category = models.ManyToManyField(Category)

    note = models.TextField(null=True,blank=True,
                            help_text=_('Editorial Board notes'))

    class Meta:
        abstract = True
        indexes = [
           models.Index(fields=['title']),
        ]


# class Publication(AbstractPublication, AbstractPublicable, CreatedModifiedBy):
class Publication(AbstractPublication, CreatedModifiedBy, AbstractLockable):
    slug = models.SlugField(null=True, blank=True)
    tags = TaggableManager()
    relevance = models.IntegerField(default=0, blank=True)

    class Meta:
        verbose_name_plural = _("Publications")

    def serialize(self):
        return {'slug': self.slug,
                'image': self.image_url(),
                'name': self.name,
                'title': self.title,
                # 'published': self.date_start,
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
        # return [i for i in related if i.related.is_publicable]
        return [i for i in related]

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
        if getattr(self, '_related_galleries', None): # pragma: no cover
            return self._related_galleries
        pub_galleries = PublicationGallery.objects.filter(publication=self,
                                                          is_active=True,
                                                          collection__is_active=True)
        # galleries = []
        # for pub_gallery in pub_galleries:
        # if pub_gallery.collection.get_items():
        # galleries.append(pub_gallery)
        self._related_galleries = pub_galleries
        return self._related_galleries

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

    def is_localizable_by(self, user=None):
        if not user: return False

        # check if user has Django permissions to change object
        permission = check_user_permission_on_object(user, self)
        # if permission
        if permission['granted']: return True

        # if no permissions and no locks
        if not permission.get('locked', False):
            # check if user has EditorialBoard translator permissions on object
            pub_ctxs = self.get_publication_contexts()
            for pub_ctx in pub_ctxs:
                webpath = pub_ctx.webpath
                webpath_perms = webpath.is_localizable_by(user=user)
                if webpath_perms: return True
        # if no permissions
        return False

    def is_editable_by(self, user=None):
        if not user: return False

        # check if user has Django permissions to change object
        permission = check_user_permission_on_object(user, self)
        # if permission
        if permission['granted']: return True

        # if no permissions and no locks
        if not permission.get('locked', False):
            # check if user has EditorialBoard editor permissions on object
            pub_ctxs = self.get_publication_contexts()
            for pub_ctx in pub_ctxs:
                webpath = pub_ctx.webpath
                webpath_perms = webpath.is_editable_by(user=user, obj=self)
                if webpath_perms: return True
        # if no permissions
        return False

    def is_publicable_by(self, user=None):
        if not user: return False

        # check if user has Django permissions to change object
        permission = check_user_permission_on_object(user, self)
        # if permission
        if permission['granted']: return True

        # if no permissions and no locks
        if not permission.get('locked', False):
            # check if user has EditorialBoard editor permissions on object
            pub_ctxs = self.get_publication_contexts()
            for pub_ctx in pub_ctxs:
                webpath = pub_ctx.webpath
                webpath_perms = webpath.is_publicable_by(user=user, obj=self)
                if webpath_perms: return True
        # if no permissions
        return False

    def is_lockable_by(self, user):
        return True if self.is_editable_by(user) else False

    def __str__(self):
        return f'{self.name} ({self.title})'


class PublicationContext(TimeStampedModel, ActivableModel,
                         AbstractPublicable, SectionAbstractModel,
                         SortableModel, CreatedModifiedBy):
    publication = models.ForeignKey(Publication, null=False, blank=False,
                                    on_delete=models.CASCADE)
    webpath = models.ForeignKey(WebPath, on_delete=models.CASCADE)
    date_start = models.DateTimeField()
    date_end = models.DateTimeField()
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

    # @property
    # def related_publication_contexts(self):
        # related = PublicationContextRelated.objects.filter(publication_context=self,
        # related__is_active=True)
        # return [i for i in related if i.related.is_publicable]

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


class PublicationRelated(TimeStampedModel, SortableModel, ActivableModel,
                         CreatedModifiedBy):
    publication = models.ForeignKey(Publication, null=False, blank=False,
                                    related_name='parent_publication',
                                    on_delete=models.CASCADE)
    related = models.ForeignKey(Publication, null=False, blank=False,
                                on_delete=models.CASCADE,
                                related_name="related_publication")

    class Meta:
        verbose_name_plural = _("Related Publications")
        unique_together = ("publication", "related")

    def __str__(self):
        return '{} {}'.format(self.publication, self.related)


class PublicationLink(TimeStampedModel, CreatedModifiedBy):
    publication = models.ForeignKey(Publication, null=False, blank=False,
                                    on_delete=models.CASCADE)
    name = models.CharField(max_length=256, null=False, blank=False)
    url = models.URLField(help_text=_("url"))

    class Meta:
        verbose_name_plural = _("Publication Links")

    def __str__(self):
        return '{} {}'.format(self.publication, self.name)


class PublicationBlock(SectionAbstractModel,TimeStampedModel,
                       ActivableModel, SortableModel, CreatedModifiedBy):
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


class PublicationGallery(TimeStampedModel, ActivableModel, SortableModel,
                         CreatedModifiedBy):
    publication = models.ForeignKey(Publication,
                                    on_delete=models.CASCADE)
    collection = models.ForeignKey(MediaCollection,
                                   on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = _("Publication Image Gallery")

    def __str__(self):
        return '{} {}'.format(self.publication, self.collection)


def publication_attachment_path(instance, filename): # pragma: no cover
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'publications_attachments/{}/{}'.format(instance.publication.pk,
                                                   filename)


class PublicationAttachment(TimeStampedModel, SortableModel, ActivableModel,
                            AbstractMedia, CreatedModifiedBy):

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
