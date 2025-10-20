from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class PublicationsConfig(AppConfig):
    name = 'cms.publications'
    label = 'cmspublications'
    verbose_name = _('publications')
