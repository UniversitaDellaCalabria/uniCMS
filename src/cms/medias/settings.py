CMS_IMAGE_CATEGORY_SIZE = 128
CMS_IMAGE_THUMBSIZE = 128

# file validation
# allowed file types: detected mimetype -> allowed file name extensions.
# This is the only source of allowed file types (see filetypes.py).
# File extension must be consistent with the content,
# to prevent uploads of files served as html/svg/js by the web server.
# Every 'image/*' mimetype is opened and converted to WebP by Pillow:
# add only image formats supported by Pillow
FILETYPE_ALLOWED_EXTENSIONS = {
    'application/pdf': ('pdf',),
    'text/csv': ('csv', 'txt'),
    'application/json': ('json',),
    'application/vnd.ms-excel': ('xls', 'xlsx', 'csv'),
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ('xlsx',),
    'application/vnd.oasis.opendocument.spreadsheet': ('ods',),
    'application/wps-office.xls': ('xls', 'et'),
    'text/plain': ('txt', 'csv', 'json'),
    'application/vnd.oasis.opendocument.text': ('odt',),
    'application/msword': ('doc',),
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ('docx',),
    'image/webp': ('webp',),
    'image/jpeg': ('jpg', 'jpeg', 'jpe', 'jfif'),
    'image/png': ('png',),
    'image/gif': ('gif',),
    'image/x-ms-bmp': ('bmp',),
    'video/mp4': ('mp4', 'm4v'),
    'application/pkcs7-mime': ('p7m',),
}

# maximum permitted filename lengh in attachments, uploads
FILE_NAME_MAX_LEN = 128

# 2.5MB - 2621440
# 5MB - 5242880
# 10MB - 10485760
# 20MB - 20971520
# 50MB - 5242880
# 100MB 104857600
# 250MB - 214958080
# 500MB - 429916160
FILE_MAX_SIZE = 5242880

# maximum number of pixels (width * height * frames) of uploaded images.
# Pillow decodes the whole image in memory: it prevents decompression bombs
CMS_IMAGE_MAX_PIXELS = 40000000

FILETYPE_IMAGE_YX_RATIO_MIN = 0.28
FILETYPE_IMAGE_YX_RATIO_MAX = 0.6

CMS_MEDIA_HANDLER_PATH = 'uuid-media'
