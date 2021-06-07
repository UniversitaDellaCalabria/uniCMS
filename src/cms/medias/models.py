import logging

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from cms.api.utils import check_user_permission_on_object
from cms.contexts.models_abstract import AbstractLockable
from cms.templates.models import (ActivableModel,
                                  CreatedModifiedBy,
                                  SortableModel,
                                  TimeStampedModel)

from taggit.managers import TaggableManager

from . settings import *
from . validators import *

logger = logging.getLogger(__name__)
FILETYPE_ALLOWED = getattr(settings, 'FILETYPE_ALLOWED',
                           FILETYPE_ALLOWED)


def context_media_path(instance, filename): # pragma: no cover
    # file will be uploaded to MEDIA_ROOT/<year>/<filename>
    return 'medias/{}/{}'.format(timezone.now().year,
                                 filename)


class AbstractMedia(models.Model):
    file_size = models.IntegerField(blank=True, null=True)
    file_type = models.CharField(choices=((i,i) for i in FILETYPE_ALLOWED),
                                 max_length=256, blank=True, null=True)

    @property
    def file_size_kb(self):
        if isinstance(self.file_size, int):
            return round(self.file_size / 1024)

    @property
    def file_size_mb(self):
        if isinstance(self.file_size, int):
            return round(self.file_size_kb / 1024)

    class Meta:
        abstract = True


class MediaCollection(ActivableModel, TimeStampedModel,
                      AbstractLockable, CreatedModifiedBy):
    name = models.CharField(max_length=160, blank=False,
                            null=False, unique=False)
    description = models.TextField(max_length=1024,
                                   null=False, blank=False)
    tags = TaggableManager()

    class Meta:
        ordering = ['name']
        verbose_name_plural = _("Media Collections")

    def get_items(self): # pragma: no cover
        return MediaCollectionItem.objects.filter(collection=self,
                                                  is_active=True)

    def __str__(self): # pragma: no cover
        return self.name


class Media(TimeStampedModel, AbstractMedia,
            AbstractLockable, CreatedModifiedBy):
    title = models.CharField(max_length=60, blank=False, null=False,
                             help_text=_("Media file title"))
    file = models.FileField(upload_to=context_media_path,
                            validators=[validate_file_extension,
                                        validate_file_size,
                                        validate_image_size_ratio])
    description = models.TextField()

    class Meta:
        verbose_name_plural = _("Media")
        ordering = ['pk']

    def get_media_path(self):
        return f'{settings.MEDIA_URL}{self.file}'

    def __str__(self):
        return '{} {}'.format(self.title, self.file_type)


class MediaCollectionItem(ActivableModel, SortableModel,
                          TimeStampedModel, CreatedModifiedBy):
    media = models.ForeignKey(Media, on_delete=models.PROTECT)
    collection = models.ForeignKey(MediaCollection,
                                   on_delete=models.CASCADE)

    class Meta:
        ordering = ['order']
        verbose_name_plural = _("Media Collection Items")

    def is_lockable_by(self, user): # pragma: no cover
        item = self.collection
        permission = check_user_permission_on_object(user=user, obj=item)
        return permission['granted']

    def __str__(self): # pragma: no cover
        return '[{}] {}'.format(self.collection, self.media)
