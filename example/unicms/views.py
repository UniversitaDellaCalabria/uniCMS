from django.conf import settings
from django.contrib.sitemaps.views import sitemap
from django.http import HttpResponse

from cms.contexts.views import base_unicms_sitemap


def unicms_sitemap(request):
    unicms_sitemap = base_unicms_sitemap(request)
    sitemaps = sitemap(request, sitemaps=unicms_sitemap)
    return HttpResponse(sitemaps.render(), content_type='text/xml')
