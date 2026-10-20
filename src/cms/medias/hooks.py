import logging
import magic
import os

from cms.medias.utils import get_file_type_size
from django.core.files.uploadedfile import InMemoryUploadedFile

from . filetypes import FILETYPE_IMAGE
from . utils import to_webp


logger = logging.getLogger(__name__)


def set_file_meta(media_object):
    data = get_file_type_size(media_object)
    media_object.file_size = data['file_size']
    media_object.file_type = data['mime_type']


def webp_image_optimizer(media_object):

    for field_name in ('file', 'image'):
        field = getattr(media_object, field_name, None)
        if field:
            break

    if not getattr(field, '_file', None):
        return

    mimetype = magic.Magic(mime=True).from_buffer(field._file.file.read())
    if mimetype in FILETYPE_IMAGE:
        field._file.seek(0)
        byte_io = to_webp(field._file)
        # conversion failed: the original image is stored
        if not byte_io:
            field._file.seek(0)
            return
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


def _get_file_field(media_object):
    for field_name in ('file', 'image'):
        if hasattr(media_object, field_name):
            return field_name, getattr(media_object, field_name)
    return None, None


def _delete_stored_file(field, name):
    if not name: return
    try:
        if field.storage.exists(name):
            field.storage.delete(name)
    except Exception as e:
        _msg = 'Media Hook: {} cannot be removed: {}'
        logger.error(_msg.format(name, e))


def remove_file(media_object):
    """
    POSTDELETE: removes the file of a deleted object
    """
    field_name, field = _get_file_field(media_object)
    if field is not None:
        _delete_stored_file(field, field.name)


def store_previous_file(media_object):
    """
    PRESAVE: stores the name of the file actually saved,
    to be compared with the new one after save
    """
    field_name, field = _get_file_field(media_object)
    if not field_name or not media_object.pk: return
    media_object._previous_file = media_object.__class__.objects\
                                              .filter(pk=media_object.pk)\
                                              .values_list(field_name, flat=True)\
                                              .first()


def remove_replaced_file(media_object):
    """
    POSTSAVE: removes the previous file if it has been replaced by a new one
    """
    previous = getattr(media_object, '_previous_file', None)
    field_name, field = _get_file_field(media_object)
    if field is not None and previous and previous != field.name:
        _delete_stored_file(field, previous)
    media_object._previous_file = None
