import logging

from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _

from cms.templates.models import ActivableModel, TimeStampedModel, CreatedModifiedBy

from . import settings as app_settings
from . exceptions import ReservedWordException
from . utils import (append_slash, is_editor,
                     is_publisher, is_translator,
                     sanitize_path)


logger = logging.getLogger(__name__)
CMS_CONTEXT_PERMISSIONS = getattr(settings, 'CMS_CONTEXT_PERMISSIONS',
                                  app_settings.CMS_CONTEXT_PERMISSIONS)
CMS_PATH_PREFIX = getattr(settings, 'CMS_PATH_PREFIX', '')


class WebSite(ActivableModel):
    name = models.CharField(max_length=254,
                            unique=True,
                            blank=False, null=False)
    domain = models.CharField(max_length=254,
                              blank=False, null=False,
                              unique=True)

    class Meta:
        verbose_name_plural = _("Sites")

    def serialize(self):
        return {'id': self.pk,
                'name': self.name,
                'domain': self.domain,
                'is_active': self.is_active}

    def is_managed_by(self, user):
        if user.is_superuser: return True
        permissions = EditorialBoardEditors.objects.filter(webpath__site=self,
                                                           user=user,
                                                           is_active=True,
                                                           permission__gt=0)
        if permissions: return True
        return False

    def __str__(self):
        return self.domain


class WebPath(ActivableModel, TimeStampedModel, CreatedModifiedBy):
    """
    A Page can belong to one or more Context
    A editor/moderator can belong to one or more Context
    The same for Page Templates
    """
    site = models.ForeignKey(WebSite,
                             null=True, blank=True,
                             on_delete=models.CASCADE)
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
        """
        if this webpath is an alias this attribute
        will be valued with a redirect url
        """ # noqa
        if self.alias:
            return self.alias.get_full_path()
        return self.alias_url

    def get_full_path(self):
        if self.is_alias:
            return self.redirect_url
        url = f'/{CMS_PATH_PREFIX}{self.fullpath}'
        return sanitize_path(url)

    def save(self, *args, **kwargs):
        # manage aliases
        if self.alias:
            self.site = self.alias.site

        # alias or alias_url
        if self.alias and self.alias_url: # pragma: no cover
            self.alias = None

        # store a correct fullpath
        self.path = append_slash(self.path)
        self.path = sanitize_path(self.path)
        if self.parent:
            self.site = self.parent.site
            # update fullpath
            fullpath = sanitize_path(f'{self.parent.fullpath}/{self.path}')
        elif self.is_alias:
            fullpath = self.redirect_url
        else:
            fullpath = self.path

        for reserved_word in settings.CMS_HANDLERS_PATHS:
            if reserved_word in fullpath:
                _msg = f'{fullpath} matches with the reserved word: {reserved_word}'
                raise ReservedWordException(_msg)

        if fullpath != self.fullpath:
            self.fullpath = fullpath

        existent = WebPath.objects.filter(site=self.site,
                                          fullpath=self.fullpath)\
                                  .exclude(pk=self.pk)\
                                  .first()
        if existent:
            raise Exception(f'Existent path "{self.get_full_path()}". Change it')

        super(WebPath, self).save(*args, **kwargs)
        # update also its childs
        for child_path in WebPath.objects.filter(parent=self):
            child_path.save()

    def get_parent_fullpath(self):
        return self.parent.get_full_path() if self.parent else ''

    def is_localizable_by(self, user=None, obj=None, parent=False):
        if not user: return False
        if user.is_superuser: return True
        self if not obj else obj
        parent = self.parent if parent else self
        eb_permission = EditorialBoardEditors.get_permission(parent, user)
        perms = is_translator(eb_permission)
        # if user has not editor permissions
        if not perms: return False
        webpath_lock_ok = EditorialBoardLockUser.check_for_locks(self, user)
        return webpath_lock_ok

    def is_editable_by(self, user=None, obj=None, parent=False):
        if not user: return False
        if user.is_superuser: return True
        item = self if not obj else obj
        parent = self.parent if parent else self
        eb_permission = EditorialBoardEditors.get_permission(parent, user)
        perms = is_editor(eb_permission)
        # if user has not editor permissions
        if not perms: return False
        # if user can edit only created by him pages
        if perms['only_created_by'] and item.created_by != user:
            return False
        webpath_lock_ok = EditorialBoardLockUser.check_for_locks(self, user)
        return webpath_lock_ok

    def is_publicable_by(self, user=None, obj=None, parent=False):
        if not user: return False
        if user.is_superuser: return True
        item = self if not obj else obj
        parent = self.parent if parent else self
        eb_permission = EditorialBoardEditors.get_permission(parent, user)
        perms = is_publisher(eb_permission)
        # if user has not editor permissions
        if not perms: return False
        # if user can edit only created by him pages
        if perms['only_created_by'] and item.created_by != user:
            return False
        webpath_lock_ok = EditorialBoardLockUser.check_for_locks(self, user)
        return webpath_lock_ok

    def is_lockable_by(self, user):
        return self.is_publicable_by(user, parent=True)

    def __str__(self):
        return '{} @ {}{}'.format(self.name, self.site, self.get_full_path())


class EditorialBoardEditors(TimeStampedModel, CreatedModifiedBy, ActivableModel):
    """
    A Page can belong to one or more Context
    A editor/moderator can belong to one or more Context
    The same for Page Templates
    """
    user = models.ForeignKey(get_user_model(),
                             on_delete=models.CASCADE)
    permission = models.IntegerField(blank=False, null=False,
                                     choices=CMS_CONTEXT_PERMISSIONS,
                                     default=0)
    webpath = models.ForeignKey(WebPath,
                                on_delete=models.CASCADE,
                                null=True, blank=True)

    class Meta:
        verbose_name_plural = _("Editorial Board Users")

    def serialize(self):
        return {'webpath': f'{self.webpath}',
                'permission': self.permission}

    @classmethod
    def get_permission(cls, webpath, user, check_all=True, consider_zero=True):

        # webpath and user must be true
        if not all((webpath, user)):
            return 0

        # return max value
        if user.is_superuser: return 7

        permissions = cls.objects.filter(user=user, is_active=True).\
            order_by('-permission')
        webpath_permission = permissions.filter(webpath=webpath).first()
        if webpath_permission:
            permission = webpath_permission.permission
            # consider zero value?
            if consider_zero and permission >= 0:
                return permission
            # or not
            if not consider_zero and permission > 0:
                return permission

        # search for user permissions in webpath parents
        # select only permissions on descendants (2,5,7)
        # refer cms.contexts.settings.CMS_CONTEXT_PERMISSIONS
        parent_permission = cls.get_permission(webpath=webpath.parent,
                                               user=user,
                                               check_all=False,
                                               consider_zero=False)
        if parent_permission in (2, 5, 7):
            return parent_permission

        # search for global permissions
        result = 0
        if check_all:
            all_permissions = permissions.filter(webpath=None)
            for entry in all_permissions:
                if entry.permission > result:
                    result = entry.permission
            return result

        return 0

    def __str__(self):
        if self.webpath:
            return '{} {} in {}'.format(self.user, self.permission, self.webpath)
        else: # pragma: no cover
            return '{} {}'.format(self.user, self.permission)


class EditorialBoardLock(models.Model):
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        verbose_name=_("content type"),
        related_name="%(app_label)s_%(class)s_locked_items",
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()
    locked_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = _("Editorial Board Locks")
        ordering = ('-locked_time',)

    def __str__(self): # pragma: no cover
        return f'{self.content_type} {self.object_id}'


class EditorialBoardLockUser(models.Model):
    lock = models.ForeignKey(EditorialBoardLock,
                             on_delete=models.CASCADE,
                             null=False, blank=False)
    user = models.ForeignKey(get_user_model(),
                             on_delete=models.CASCADE,
                             null=False, blank=False)

    class Meta:
        verbose_name_plural = _("Editorial Board Locks Owners")

    @classmethod
    def get_object_locks(cls, content_type, object_id):
        return cls.objects.filter(lock__content_type=content_type,
                                  lock__object_id=object_id)

    @classmethod
    def get_user_object_locks(cls, user, content_type, object_id):
        return cls.get_object_locks(content_type=content_type,
                                    object_id=object_id).filter(user=user)

    @classmethod
    def check_for_locks(cls, obj, user):
        # check for locks on object
        content_type = ContentType.objects.get_for_model(obj)
        locks = cls.get_object_locks(content_type=content_type,
                                     object_id=obj.pk)
        # if there is not lock, ok
        if not locks: return True
        # if user is in lock user list, has permissions
        if locks.filter(user=user): return True
        # else no permissions but obj is locked
        return False

    def __str__(self): # pragma: no cover
        return f'{self.lock} {self.user}'


class EntryUsedBy(models.Model):
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        verbose_name=_("content type"),
        related_name="%(app_label)s_%(class)s_entry",
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    used_by_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        verbose_name=_("used by content type"),
        related_name="%(app_label)s_%(class)s_usedby",
    )
    used_by_object_id = models.PositiveIntegerField()
    used_by_content_object = GenericForeignKey('used_by_content_type',
                                               'used_by_object_id')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = _("Entries Used By")

    @property
    def object(self): # pragma: no cover
        return self.content_object

    @property
    def used_by(self): # pragma: no cover
        return self.used_by_content_object

    def __str__(self): # pragma: no cover
        return (f'{self.content_type} {self.object_id} used by '
                f'{self.used_by_content_type} {self.used_by_object_id}')
