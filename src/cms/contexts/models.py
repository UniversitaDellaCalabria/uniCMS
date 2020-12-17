import logging

from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from cms.contexts.utils import sanitize_path
from cms.templates.models import TimeStampedModel

from . import settings as app_settings


logger = logging.getLogger(__name__)
CMS_CONTEXT_PERMISSIONS = getattr(settings, 'CMS_CONTEXT_PERMISSIONS',
                                  app_settings.CMS_CONTEXT_PERMISSIONS)
CMS_PATH_PREFIX = getattr(settings, 'CMS_PATH_PREFIX', '')


class CreatedModifiedBy(models.Model):
    created_by = models.ForeignKey(get_user_model(),
                                   null=True, blank=True,
                                   on_delete=models.CASCADE,
                                   related_name='%(class)s_created_by')
    modified_by = models.ForeignKey(get_user_model(),
                                    null=True, blank=True,
                                    on_delete=models.CASCADE,
                                    related_name='%(class)s_modified_by')
    
    class Meta:
        abstract = True


class WebSite(models.Model):
    name = models.CharField(max_length=254, blank=False, null=False)
    domain = models.CharField(max_length=254, blank=False, null=False)
    is_active   = models.BooleanField(default=False, blank=True)

    class Meta:
        verbose_name_plural = _("Sites")

    def __str__(self):
        return self.domain


class WebPath(TimeStampedModel, CreatedModifiedBy):
    """
    A Page can belong to one or more Context
    A editor/moderator can belong to one or more Context
    The same for Page Templates
    """
    site = models.ForeignKey(WebSite, on_delete=models.CASCADE)
    name = models.CharField(max_length=254, blank=False, null=False)
    parent = models.ForeignKey('WebPath',
                               null=True, blank=True,
                               on_delete=models.CASCADE,
                               related_name="related_path",
                               help_text=_('path be prefixed with '
                                           'the parent one, on save'))
    alias = models.ForeignKey('WebPath',
                           null=True, blank=True,
                           on_delete=models.CASCADE,
                           related_name="alias_path",
                           help_text=_('Alias that would be '
                                       'redirected to ...'))
    alias_url = models.TextField(max_length=2048,
                                 null=True, blank=True)
    path = models.TextField(max_length=2048, null=False, blank=False)
    fullpath = models.TextField(max_length=2048, null=True, blank=True,
                                help_text=_("final path prefixed with the "
                                            "parent path"))
    is_active   = models.BooleanField()

    class Meta:
        verbose_name_plural = _("Site Contexts (WebPaths)")

    def split(self) -> list:
        """
        return splitted nodes in a list
        """
        path = sanitize_path(self.path)
        if path == '/':
            return ['/']
        return path.split('/')

    @property
    def is_alias(self):
        return True if (self.alias or self.alias_url) else False

    @property
    def redirect_url(self):
        if self.alias:
            return self.alias.fullpath
        return self.alias_url

    def get_full_path(self):
        if self.is_alias:
            return self.redirect_url
        url = f'/{CMS_PATH_PREFIX}{self.fullpath}'
        return sanitize_path(url)

    def save(self, *args, **kwargs):
        self.path = self.path if self.path[-1] == '/' else f'{self.path}/'
        self.path = sanitize_path(self.path)
        if self.parent:
            # update fullpath
            fullpath = sanitize_path(f'{self.parent.fullpath}/{self.path}')
        else:
            fullpath = self.path

        for reserved_word in settings.CMS_HANDLERS_PATHS:
            if reserved_word in fullpath:
                _msg = f'{fullpath} matches with the reserved word: {reserved_word}'
                raise ReservedWordException(_msg)

        if fullpath != self.fullpath:
            self.fullpath = fullpath

        return super(WebPath, self).save(*args, **kwargs)
        # update also its childs
        for child_path in WebPath.objects.filter(parent=self):
            child_path.save()

    def __str__(self):
        return '{} @ {}{}'.format(self.name, self.site, self.get_full_path())


class EditorialBoardEditors(TimeStampedModel, CreatedModifiedBy):
    """
    A Page can belong to one or more Context
    A editor/moderator can belong to one or more Context
    The same for Page Templates
    """
    user = models.ForeignKey(get_user_model(),
                             on_delete=models.CASCADE)
    permission = models.CharField(max_length=5, blank=False, null=False,
                                  choices=CMS_CONTEXT_PERMISSIONS)
    webpath = models.ForeignKey(WebPath,
                                on_delete=models.CASCADE,
                                null=True, blank=True)
    is_active   = models.BooleanField()

    class Meta:
        verbose_name_plural = _("Editorial Board Users")

    def __str__(self):
        if getattr(self, 'webpath'):
            return '{} {} in {}'.format(self.user, self.permission, self.webpath)
        else:
            return '{} {}'.format(self.user, self.permission)


class EditorialBoardLocks(models.Model):
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        verbose_name=_("content type"),
        related_name="%(app_label)s_%(class)s_locked_items",
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()
    
    locked_by = models.ForeignKey(get_user_model(), 
                                  on_delete=models.CASCADE,
                                  null=True, blank=True)
    locked_time = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name_plural = _("Editorial Board Locks")
        ordering = ('-locked_time',)
        
    @property
    def is_active(self):
        now = timezone.localtime() 
        unlock_time = self.locked_time + timezone.timedelta(minutes = 1)
        return now < unlock_time
    
    def __str__(self):
        return f'{self.content_type} {self.object_id}'
