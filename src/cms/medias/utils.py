import logging
import magic
import os

from io import BytesIO
from PIL import Image

logger = logging.getLogger(__name__)


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
    pil = Image.open(fopen)
    return pil.size


def to_webp(fobj):
    byte_io = BytesIO()
    im = Image.open(fobj)
    try:
        im.save(byte_io, format = "WebP",
                optimize=True, quality=66)
    except Exception as e: # pragma: no cover
        logger.exception(f'Media Hook image_optimized failed: {e}')
        return
    byte_io.seek(0)
    return byte_io
