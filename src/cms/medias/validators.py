import magic

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
FILETYPE_IMAGE_YX_RATIO_MIN = getattr(settings, 'FILETYPE_IMAGE_YX_RATIO_MIN',
                                      app_settings.FILETYPE_IMAGE_YX_RATIO_MIN)
FILETYPE_IMAGE_YX_RATIO_MAX = getattr(settings, 'FILETYPE_IMAGE_YX_RATIO_MAX',
                                      app_settings.FILETYPE_IMAGE_YX_RATIO_MAX)


def validate_file_size(value):
    if not hasattr(value.file, 'size'): # pragma: no cover
        return
    content_size = None
    try:
        content_size = int(value._file.size)
    except ValueError: # pragma: no cover
        _msg = "Can't detect file size: {}"
        raise ValidationError(_msg.format(value._file.__dict__))
    if content_size > FILE_MAX_SIZE:
        _max_size_mb = (FILE_MAX_SIZE / 1024) / 1024
        _msg = f'File size exceed the maximum value ({_max_size_mb} MB)'
        raise ValidationError(_msg)


def validate_file_extension(value):
    if not hasattr(value.file, 'file'): # pragma: no cover
        return

    mimetype = magic.Magic(mime=True).from_buffer(value._file.file.read())
    value._file.file.seek(0)

    if mimetype not in FILETYPE_ALLOWED:
        raise ValidationError(f'Unsupported file extension {mimetype}')


def validate_image_size_ratio(value):
    if not hasattr(value.file, 'content_type'): # pragma: no cover
        return

    mimetype = magic.Magic(mime=True).from_buffer(value._file.file.read())
    value._file.file.seek(0)

    if mimetype in FILETYPE_IMAGE:
        w, y = get_image_width_height(value._file)
        ratio = y / w
        if ratio < FILETYPE_IMAGE_YX_RATIO_MIN or \
           ratio > FILETYPE_IMAGE_YX_RATIO_MAX:
            rratio = f'{ratio:.2f}'
            raise ValidationError(f'Image have invalid y / w ratio {rratio}')
