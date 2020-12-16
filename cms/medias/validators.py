import os

from django.conf import settings
from django.core.exceptions import ValidationError

from . import settings as app_settings
from . utils import get_image_width_height


FILETYPE_IMAGE = getattr(settings, 'FILETYPE_IMAGE', 
                         app_settings.FILETYPE_IMAGE)
FILETYPE_ALLOWED = getattr(settings, 'FILETYPE_ALLOWED', 
                           app_settings.FILETYPE_ALLOWED)
FILE_MAX_SIZE = getattr(settings, 'FILE_MAX_SIZE', 
                        app_settings.FILE_MAX_SIZE)


def validate_file_size(value):
    if not hasattr(value._file, 'size'):
        return
    content_size = None
    try:
        content_size = int(value._file.size)
    except ValueError:
        _msg = "Can't detect file size: {}"
        raise ValidationError(_msg.format(value._file.__dict__))
    if content_size > FILE_MAX_SIZE:
        _max_size_mb = (FILE_MAX_SIZE/1024)/1024
        _msg = f'File size exceed the maximum value ({_max_size_mb} MB)'
        raise ValidationError(_msg)


def validate_file_extension(value):
    if not hasattr(value._file, 'content_type'):
        return
    content_type = value._file.content_type
    if content_type not in FILETYPE_ALLOWED:
        raise ValidationError(f'Unsupported file extension {content_type}')


def validate_image_size_ratio(value):
    if not hasattr(value._file, 'content_type'):
        return
    if value._file.content_type in FILETYPE_IMAGE:
        w, y = get_image_width_height(value._file)
        ratio = y / w
        if ratio < 0.28 or ratio > 0.6:
            rratio = f'{ratio:.2f}'
            raise ValidationError(f'Image have invalid y / w ratio {rratio}')
    
