from . settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

LOCKS_CACHE_TTL = 0

# CACHES = {
# 'default': {
    # 'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
    # 'LOCATION': '/var/tmp/django_cache',
    # 'TIMEOUT': 60,
    # 'OPTIONS': {
        # 'MAX_ENTRIES': 1000
    # }
# }
# }

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://localhost:6379/unicms",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "COMPRESSOR": "django_redis.compressors.zlib.ZlibCompressor",
            # improve resilience
            "IGNORE_EXCEPTIONS": True,
            "SOCKET_CONNECT_TIMEOUT": 2,  # seconds
            "SOCKET_TIMEOUT": 2,  # seconds
        }
    }
}
DJANGO_REDIS_LOG_IGNORED_EXCEPTIONS = True

MONGO_URL = 'mongodb://localhost:27017'
MONGO_CONNECTION_PARAMS = dict()
