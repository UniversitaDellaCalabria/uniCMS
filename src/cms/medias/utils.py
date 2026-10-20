import logging
import magic
import os

from django.conf import settings
from io import BytesIO
from PIL import Image, ImageOps

from . import settings as app_settings
from . filetypes import FILETYPE_IMAGE

logger = logging.getLogger(__name__)

CMS_IMAGE_MAX_PIXELS = getattr(settings, 'CMS_IMAGE_MAX_PIXELS',
                               app_settings.CMS_IMAGE_MAX_PIXELS)


def get_file_type_size(media_obj) -> dict:
    fopen = media_obj.file
    mime = magic.Magic(mime=True)
    fopen.seek(0)
    content_type = mime.from_buffer(fopen.read())
    fopen.seek(0, os.SEEK_END)
    content_size = fopen.tell()
    fopen.seek(0)
    data = dict(mime_type=content_type, file_size=content_size)
    logger.debug(f'Media item hook get_file_type_size: {data}')
    return data


def get_image_width_height(fopen):
    mime = magic.Magic(mime=True)
    fopen.seek(0)
    mimetype = mime.from_buffer(fopen.read())
    fopen.seek(0)
    if mimetype in FILETYPE_IMAGE:
        try:
            pil = Image.open(fopen)
        except Exception as e: # pragma: no cover
            logger.warning(f'Image size detection failed: {e}')
            return
        return pil.size


def image_exceeds_max_pixels(im) -> bool:
    """
    Image.open() reads only the header: the check is done
    before decoding the image in memory
    """
    if not CMS_IMAGE_MAX_PIXELS: return False
    w, h = im.size
    return w * h * getattr(im, 'n_frames', 1) > CMS_IMAGE_MAX_PIXELS


def to_webp(fobj):
    byte_io = BytesIO()
    try:
        im = Image.open(fobj)
        if image_exceeds_max_pixels(im):
            logger.warning(f'Media Hook image_optimized: image {im.size} '
                           f'exceeds {CMS_IMAGE_MAX_PIXELS} pixels')
            return
        animated = getattr(im, 'is_animated', False)
        if not animated:
            # WebP doesn't keep EXIF orientation
            im = ImageOps.exif_transpose(im)
            # WebP supports only RGB and RGBA (eg: CMYK jpeg)
            if im.mode not in ('RGB', 'RGBA'):
                has_alpha = 'A' in im.mode or 'transparency' in im.info
                im = im.convert('RGBA' if has_alpha else 'RGB')
        im.save(byte_io, format = "WebP",
                optimize=True, quality=66,
                save_all=animated)
    except Exception as e: # pragma: no cover
        logger.exception(f'Media Hook image_optimized failed: {e}')
        return
    byte_io.seek(0)
    return byte_io

