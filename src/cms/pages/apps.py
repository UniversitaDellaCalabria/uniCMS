from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class PagesConfig(AppConfig):
    name = 'cms.pages'
    label = 'cmspages'
    verbose_name = _('pages')
