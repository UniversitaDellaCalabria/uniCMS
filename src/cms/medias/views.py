from django.core.cache import cache
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404

from . models import Media


def get_media_file(request, *args, **kwargs):
    uuid = kwargs['unique_code']
    url = cache.get(f'media-{uuid}')
    if not url:
        item = get_object_or_404(Media, uuid=uuid)
        url = item.file.url
        cache.set(f'media-{uuid}', url)
    return HttpResponseRedirect(url)
