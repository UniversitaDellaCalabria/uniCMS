import logging

from django.conf import settings
from django.db import models
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from . import settings as app_settings

logger = logging.getLogger(__name__)

CMS_BLOCK_TYPES = getattr(settings, 'CMS_BLOCK_TYPES',
                          app_settings.CMS_BLOCK_TYPES)
CMS_BLOCK_TEMPLATES = getattr(settings, 'CMS_BLOCK_TEMPLATES',
                            app_settings.CMS_BLOCK_TEMPLATES)
CMS_TEMPLATE_BLOCK_SECTIONS = getattr(settings, 'CMS_TEMPLATE_BLOCK_SECTIONS',
                                      app_settings.CMS_TEMPLATE_BLOCK_SECTIONS)
CMS_PAGE_TEMPLATES = getattr(settings, 'CMS_PAGE_TEMPLATES',
                             app_settings.CMS_PAGE_TEMPLATES)
CMS_LINKS_LABELS = getattr(settings, 'CMS_LINKS_LABELS',
                           app_settings.CMS_LINKS_LABELS)


class TimeStampedModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified =  models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SortableModel(models.Model):
    order = models.IntegerField(null=True, blank=True, default=10)

    class Meta:
        abstract = True
        ordering = ['order']


class ActivableModel(models.Model):
    is_active    = models.BooleanField()

    class Meta:
        abstract = True


class SectionAbstractModel(models.Model):
    section = models.CharField(max_length=60, blank=True, null=True,
                               help_text=_("Specify the container "
                                           "section in the template where "
                                           "this block would be rendered."),
                               choices=CMS_TEMPLATE_BLOCK_SECTIONS)
    class Meta:
        abstract = True


class AbstractPageBlock(TimeStampedModel, ActivableModel):
    name = models.CharField(max_length=60, blank=True, null=True,
                            help_text=_("Specify the container "
                                        "section in the template where "
                                        "this block would be rendered."))
    type = models.TextField(choices=CMS_BLOCK_TYPES,
                            blank=False, null=False)
    content = models.TextField(help_text=_("according to the "
                                           "block template schema"),
                               blank=True, null=True)

    class Meta:
        abstract = True


class PageTemplate(TimeStampedModel, ActivableModel):
    name = models.CharField(max_length=160,
                            blank=True, null=True)
    template_file = models.CharField(max_length=1024,
                                     blank=False, null=False,
                                     choices=CMS_PAGE_TEMPLATES or \
                                     (('', 'No templates found'),))
    note = models.TextField(null=True, blank=True,
                            help_text=_("Editorial Board Notes, "
                                        "not visible by public."))

    class Meta:
        ordering = ['name']
        verbose_name_plural = _("Page Templates")

    def __str__(self):
        return '{} ({})'.format(self.name, self.template_file)


class TemplateBlock(AbstractPageBlock):
    name = models.CharField(max_length=60, blank=True, null=True,
                            help_text=_("Specify the container "
                                        "section in the template where "
                                        "this block would be rendered."))
    description = models.TextField(null=True,blank=True,
                                   help_text=_('Description of this block'))
    type = models.TextField(choices=CMS_BLOCK_TYPES,
                            blank=False, null=False)
    content = models.TextField(help_text=_("according to the "
                                           "block template schema"),
                               blank=True, null=True)
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = _("Template Blocks")

    def __str__(self):
        return self.name if self.name else self.path


class PageTemplateBlock(TimeStampedModel,
                        SortableModel, ActivableModel):
    template = models.ForeignKey(PageTemplate,
                                 on_delete=models.CASCADE,
                                 limit_choices_to={'is_active': True},)
    block = models.ForeignKey(TemplateBlock, null=False, blank=False,
                              on_delete=models.CASCADE)
    section = models.CharField(max_length=33, blank=True, null=True,
                               help_text=_("Specify the container "
                                           "section in the template where "
                                           "this block would be rendered."),
                               choices=CMS_TEMPLATE_BLOCK_SECTIONS)
    
    @property
    def type(self):
        return self.block.type
    
    @property
    def content(self):
        return self.block.content
    
    class Meta:
        verbose_name_plural = _("Page Template Blocks")

    def __str__(self):
        return '({}) {} {}:{}'.format(self.template, self.block,
                                      self.order or 0,
                                      self.section or '')
