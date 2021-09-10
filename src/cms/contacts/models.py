from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from cms.api.utils import check_user_permission_on_object
from cms.contexts.models_abstract import AbstractLockable
from cms.medias.models import Media
from cms.templates.models import (ActivableModel,
                                  CreatedModifiedBy,
                                  SortableModel,
                                  TimeStampedModel)


CONTACT_TYPES = (('person', _('Person')),
                 ('structure', _('Structure')),)
EXTRA_INFO_TYPES = (('email', _('Email')),
                    ('location', _('Location')),
                    ('phone', _('Phone')),
                    ('website', _('Website')))


class Contact(ActivableModel, TimeStampedModel, CreatedModifiedBy,
              AbstractLockable):
    name = models.CharField(max_length=160)
    contact_type = models.CharField(choices=CONTACT_TYPES,
                                    max_length=10)
    description = models.TextField(max_length=2048,
                                   blank=True,
                                   default='')
    image = models.ForeignKey(Media, on_delete=models.PROTECT,
                              null=True, blank=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = _("Contacts")

    def localized(self, lang=settings.LANGUAGE):
        i18n = ContactLocalization.objects.filter(contact=self,
                                                  language=lang,
                                                  is_active=True)\
                                              .first()
        if i18n:
            self.name = i18n.name
            self.description = i18n.description
        return self

    def get_infos(self, lang=settings.LANGUAGE):
        infos = []
        for i in self.contactinfo_set.filter(contact=self,
                                             is_active=True)\
                .order_by('order'):
            infos.append(i.localized(lang=lang))
        return infos

    def __str__(self):
        return self.name


class ContactLocalization(ActivableModel,
                          TimeStampedModel, SortableModel,
                          CreatedModifiedBy):
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE)
    language = models.CharField(choices=settings.LANGUAGES,
                                max_length=12,
                                default='en')
    name = models.CharField(max_length=160,
                            blank=True,
                            default='')
    description = models.TextField(max_length=2048,
                                   blank=True,
                                   default='')

    class Meta:
        verbose_name_plural = _("Contact Localization")

    def is_lockable_by(self, user):
        item = self.contact
        permission = check_user_permission_on_object(user=user, obj=item)
        return permission['granted']

    def __str__(self):
        return '{} {}'.format(self.contact, self.language)


class ContactInfo(ActivableModel, TimeStampedModel,
                  SortableModel, CreatedModifiedBy):
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE)
    info_type = models.CharField(choices=EXTRA_INFO_TYPES,
                                 max_length=15)
    label = models.CharField(max_length=160)
    value = models.CharField(max_length=160)

    class Meta:
        verbose_name_plural = _("Contact extra infos")

    def localized(self, lang=settings.LANGUAGE):
        i18n = ContactInfoLocalization.objects.filter(contact_info=self,
                                                      language=lang,
                                                      is_active=True)\
                                              .first()
        if i18n:
            self.label = i18n.label
            self.value = i18n.value
        return self

    def is_lockable_by(self, user):
        item = self.contact
        permission = check_user_permission_on_object(user=user, obj=item)
        return permission['granted']

    def __str__(self):
        return '[{}] {}: {}'.format(self.contact,
                                    self.info_type, self.value)


class ContactInfoLocalization(ActivableModel,
                              TimeStampedModel, SortableModel,
                              CreatedModifiedBy):
    contact_info = models.ForeignKey(ContactInfo,
                                     on_delete=models.CASCADE)
    language = models.CharField(choices=settings.LANGUAGES,
                                max_length=12,
                                default='en')
    label = models.CharField(max_length=160)
    value = models.CharField(max_length=160)

    class Meta:
        verbose_name_plural = _("Contact Info Localizations")

    def is_lockable_by(self, user):
        item = self.contact_info.contact
        permission = check_user_permission_on_object(user=user, obj=item)
        return permission['granted']

    def __str__(self):
        return '{} {}'.format(self.contact_info, self.language)
