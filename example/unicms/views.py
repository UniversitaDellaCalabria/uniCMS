from django.conf import settings
from django.contrib.sitemaps import GenericSitemap
from django.contrib.sitemaps.views import sitemap
from django.http import HttpResponse

from cms.contexts.views import base_unicms_sitemap


def unicms_sitemap(request):
    unicms_sitemap = base_unicms_sitemap(request)

    if 'unicms_calendar' in settings.INSTALLED_APPS:
        from unicms_calendar.views import unicms_calendar_sitemap
        calendar_sitemap = unicms_calendar_sitemap(request)
        unicms_sitemap.update(calendar_sitemap)

    sitemaps = sitemap(request, sitemaps=unicms_sitemap)
    return HttpResponse(sitemaps.render(), content_type='text/xml')
