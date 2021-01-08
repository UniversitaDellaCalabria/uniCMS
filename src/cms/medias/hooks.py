import logging
import magic
import os

from cms.medias.utils import get_file_type_size
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile

from . import settings as app_settings
from . utils import to_webp


logger = logging.getLogger(__name__)
FILETYPE_IMAGE = getattr(settings, 'FILETYPE_IMAGE',
                         app_settings.FILETYPE_IMAGE)


def set_file_meta(media_object):
    data = get_file_type_size(media_object)
    media_object.file_size = data['file_size']
    media_object.file_type = data['mime_type']


def webp_image_optimizer(media_object):

    for field_name in ('file', 'image'):
        field = getattr(media_object, field_name, None)
        if field:
            break

    if not getattr(field, '_file', None): # pragma: no cover
        return

    mimetype = magic.Magic(mime=True).from_buffer(field._file.file.read())
    if mimetype in FILETYPE_IMAGE:
        field._file.seek(0)
        byte_io = to_webp(field._file)
        byte_io.seek(0, os.SEEK_END)
        content_size = byte_io.tell()
        byte_io.seek(0)

        fname = '.'.join(field.name.split('.')[:-1]) + '.webp'
        field._file = InMemoryUploadedFile(file = byte_io,
                                           name = fname,
                                           content_type = 'image/webp',
                                           size = content_size,
                                           charset='utf-8',
                                           field_name = field_name)
        field._file._name = fname
        field.name = fname

        field._file.size = content_size
        field._file.content_type = 'image/webp'

        # if they are valuable ... otherwise nothins happens to model
        media_object.file_size = content_size
        media_object.file_type = 'image/webp'
        logger.info(f'Image {fname} converted from {mimetype} to {media_object.file_type}')
        return True


def remove_file(media_object):
    fpath = media_object.file.path
    try:
        os.remove(fpath)
    except Exception as e: # pragma: no cover
        _msg = 'Media Hook remove_file: {} cannot be removed: {}'
        logger.error(_msg.format(fpath, e))
