from django.conf import settings

from .settings import FILETYPE_ALLOWED_EXTENSIONS


# FILETYPE_ALLOWED_EXTENSIONS is the only source of allowed file types.
# Allowed, image and media mimetypes are derived from its keys
FILETYPE_ALLOWED_EXTENSIONS = getattr(settings, 'FILETYPE_ALLOWED_EXTENSIONS',
                                      FILETYPE_ALLOWED_EXTENSIONS)

FILETYPE_ALLOWED = tuple(FILETYPE_ALLOWED_EXTENSIONS.keys())
FILETYPE_IMAGE = tuple(i for i in FILETYPE_ALLOWED if i.startswith('image/'))
FILETYPE_VIDEO = tuple(i for i in FILETYPE_ALLOWED if i.startswith('video/'))
FILETYPE_MEDIA = FILETYPE_IMAGE + FILETYPE_VIDEO
