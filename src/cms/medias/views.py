from django.http import FileResponse
from django.shortcuts import get_object_or_404

from . models import Media


def get_media_file(request, *args, **kwargs):
    uuid = kwargs['unique_code']
    item = get_object_or_404(Media, uuid=uuid)
    return FileResponse(item.file)
