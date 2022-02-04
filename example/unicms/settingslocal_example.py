import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'your_secret_key'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']
AUTH_USER_MODEL = 'accounts.User'

# multisite preferences (comment these options if unnecessary)
SESSION_COOKIE_DOMAIN=".unical.it"
MAIN_WEBSITE = 2

# Application definition

INSTALLED_APPS = [
    'accounts',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.sitemaps',
    'django.contrib.staticfiles',

    'taggit',
    'taggit_serializer',
    'nested_admin',

    'cms.templates',
    'cms.contacts',
    'cms.contexts',
    'cms.carousels',
    'cms.menus',
    'cms.medias',
    'cms.pages',
    'cms.publications',
    'cms.api',
    'cms.search',

    'sass_processor',
    'unicms_template_unical',
    'unicms_template_italia',
    'bootstrap_italia_template',

    'rest_framework',
    'django_filters',

    # editorial board app
    # 'unicms_editorial_board',

    # Unical storage API hanler
    # 'unicms_unical_storage_handler',

    # uniCMS calendar
    # 'unicms_calendar',

    # SAML2 SP
    # 'djangosaml2',
    # 'saml2_sp',

]

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

DATA_UPLOAD_MAX_NUMBER_FIELDS = 100 * 100

# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'it-it'
LANGUAGE = LANGUAGE_CODE.split('-')[0]
TIME_ZONE = 'UTC'
# TIME_ZONE = 'Europe/Rome'
USE_I18N = True
USE_L10N = True
USE_TZ = True

LANGUAGES = [('ar', 'Arabic'),
             ('en', 'English'),
             ('es', 'Spanish'),
             ('fr', 'French'),
             ('it', 'Italian'),
             ('pt', 'Portuguese')]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # html minify
    'htmlmin.middleware.HtmlMinifyMiddleware',
    'htmlmin.middleware.MarkRequestMiddleware',

    # unicms
    'cms.contexts.middleware.detect_language_middleware',
    'cms.contexts.middleware.show_template_blocks_sections',
    'cms.contexts.middleware.show_cms_draft_mode',
]

# HTML MINIFY
HTML_MINIFY = True
EXCLUDE_FROM_MINIFYING = ('^admin/',)

if os.environ.get('CI'):
    CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': '/var/tmp/django_cache',
        'TIMEOUT': 60,
        'OPTIONS': {
            'MAX_ENTRIES': 1000
        }
    }
}
else:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": "redis://10.0.3.89:6379/unicms",
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

CMS_CACHE_ENABLED = True

CMS_CACHE_KEY_PREFIX = 'unicms_'
# in seconds
CMS_CACHE_TTL = 25
# set to 0 means infinite
CMS_CACHE_MAX_ENTRIES = 0
# request.get_raw_uri() that matches the following would be ignored by cache ...
CMS_CACHE_EXCLUDED_MATCHES =  ['/search?']

CMS_PATH_PREFIX = 'portale/'
CMS_CACHE_EXCLUDED_MATCHES.append('/portale/search?')

# Static files (CSS, JavaScript, Images)
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# STATICFILES_DIRS = [
    # os.path.join(BASE_DIR, 'static'),
# ]

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'


ADMINS = [
    ('Giuseppe De Marco', 'giuseppe.demarco@unical.it'),
    ('Francesco Filicetti', 'francesco.filicetti@unical.it'),
]
MANAGERS = ADMINS

# Default to dummy email backend. Configure dev/production/local backend
# as per https://docs.djangoproject.com/en/stable/topics/email/#email-backends
EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'
EMAIL_SUBJECT_PREFIX = '[Portale Unical] '

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'formatters': {
        'default': {
            # exact format is not important, this is the minimum information
            'format': '%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
        },
        'detailed': {
            'format': '[%(asctime)s] %(message)s [(%(levelname)s)] %(args)s %(name)s %(filename)s.%(funcName)s:%(lineno)s]'
        },
        'json': {
            'format': '{"timestamp": "%(asctime)s", "msg": %(message)s, "level": "%(levelname)s",  "name": "%(name)s", "path": "%(filename)s.%(funcName)s:%(lineno)s", "@source":"django-audit"}'
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            'formatter': 'detailed',
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'cms.contexts': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'cms.search': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'cms.medias.hooks': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    }
}

CMS_TEMPLATES_FOLDER = 'templates/unicms'

CMS_PUBLICATION_VIEW_PREFIX_PATH = 'contents/news/view/'
CMS_PUBLICATION_LIST_PREFIX_PATH = 'contents/news/list'
CMS_PUBLICATION_URL_LIST_REGEXP = f'^(?P<webpath>[\/a-zA-Z0-9\.\-\_]*)({CMS_PUBLICATION_LIST_PREFIX_PATH})/?$'
CMS_PUBLICATION_URL_VIEW_REGEXP = f'^(?P<webpath>[\/a-zA-Z0-9\.\-\_]*)({CMS_PUBLICATION_VIEW_PREFIX_PATH})(?P<slug>[a-z0-9\-]*)'

CMS_HANDLERS_PATHS = [CMS_PUBLICATION_VIEW_PREFIX_PATH,
                      CMS_PUBLICATION_LIST_PREFIX_PATH]

CMS_APP_REGEXP_URLPATHS = {
    'cms.publications.handlers.PublicationViewHandler' : CMS_PUBLICATION_URL_VIEW_REGEXP,
    'cms.publications.handlers.PublicationListHandler' : CMS_PUBLICATION_URL_LIST_REGEXP,
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates',
                 f'{CMS_TEMPLATES_FOLDER}',
                 f'{CMS_TEMPLATES_FOLDER}/admin',
                 f'{CMS_TEMPLATES_FOLDER}/pages',
                 f'{CMS_TEMPLATES_FOLDER}/blocks'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

OAS3_CONFIG = {'title': "Portale dell'Università della Calabria",
               # 'permission_classes': (permissions.AllowAny,),
               'description': "Portale dell'Università della Calabria",
               'termsOfService': 'https://tos.unical.it',
               'x-api-id': '00000000-0000-0000-0000-000000000024',
               'x-summary': "Portale dell'Università della Calabria",
               'license': dict(name='apache2',
                               url='http://www.apache.org/licenses/LICENSE-2.0.html'),
               'servers': [dict(description='description',
                                url='https://www.unical.it'),
                           dict(description='description',
                                url='https://www.unical.it')],
               'tags': [dict(description='description',
                             name='api'),
                        dict(description='description',
                             name='public')],
               'contact': dict(email = 'giuseppe.demarco@unical.it',
                               name = 'Giuseppe De Marco',
                               url = 'https://github.com/UniversitaDellaCalabria'),
               'version': "0.1.2"
}

# MONGO_URL = 'mongodb://10.0.3.217:27017'
# MONGO_CONNECTION_PARAMS = dict(username='username',
                                 # password='password',
                                 # connectTimeoutMS=5000,
                                 # socketTimeoutMS=5000,
                                 # serverSelectionTimeoutMS=5000)
MONGO_URL = 'mongodb://localhost:27017'
MONGO_CONNECTION_PARAMS = dict()

MONGO_DB_NAME = 'unicms'
MONGO_COLLECTION_NAME = 'search'
MODEL_TO_MONGO_MAP = {
    'cmspages.Page': 'cms.search.models.page_to_entry',
    'cmspublications.Publication': 'cms.search.models.publication_to_entry'
}

CMS_HOOKS = {
    'Publication': {
        'PRESAVE': [],
        'POSTSAVE': ['cms.search.hooks.publication_se_insert',
                     'cms.contexts.hooks.used_by'],
        'PREDELETE': ['cms.search.hooks.searchengine_entry_remove',],
        'POSTDELETE': []
    },
    'PublicationContext': {
        'PRESAVE': [],
        'POSTSAVE': ['cms.search.hooks.publication_context_se_insert',],
        'PREDELETE': ['cms.search.hooks.publication_context_se_delete',],
        'POSTDELETE': []
    },
    'Page': {
        'PRESAVE': [],
        'POSTSAVE': ['cms.search.hooks.page_se_insert',
                     'cms.contexts.hooks.used_by'],
        'PREDELETE': ['cms.search.hooks.searchengine_entry_remove',],
        'POSTDELETE': []
    },
    'Media': {
        'PRESAVE': ['cms.medias.hooks.set_file_meta',
                    'cms.medias.hooks.webp_image_optimizer'],
        'POSTSAVE': ['cms.contexts.hooks.used_by'],
        'PREDELETE': [],
        'POSTDELETE': ['cms.medias.hooks.remove_file']
    },
    'MediaCollection': {
        'PRESAVE': [],
        'POSTSAVE': ['cms.contexts.hooks.used_by'],
        'PREDELETE': [],
        'POSTDELETE': []
    },
    'NavigationBar': {
        'PRESAVE': [],
        'POSTSAVE': ['cms.contexts.hooks.used_by'],
        'PREDELETE': [],
        'POSTDELETE': []
    },
    'Category': {
        'PRESAVE': ['cms.medias.hooks.webp_image_optimizer'],
        'POSTSAVE': [],
        'PREDELETE': [],
        'POSTDELETE': ['cms.medias.hooks.remove_file']
    },
    'Carousel': {
        'POSTSAVE': ['cms.contexts.hooks.used_by'],
    },
    'PageNavigationBar': {
        'POSTSAVE': ['cms.contexts.hooks.used_by'],
    },
    'PublicationAttachment': {
        'PRESAVE': ['cms.medias.hooks.set_file_meta',],
        'POSTSAVE': [],
        'PREDELETE': [],
        'POSTDELETE': []
    }
}

# UNICMS ITALIA TEMPLATE
if "unicms_template_italia" in INSTALLED_APPS:
    from unicms_template_italia.settings import *
# END UNICMS ITALIA TEMPLATE

# UNICMS UNICAL TEMPLATE
if "unicms_template_unical" in INSTALLED_APPS:
    from unicms_template_unical.settings import *
# END UNICMS UNICAL TEMPLATE

# UNICMS CALENDAR HANDLER
if "unicms_calendar" in INSTALLED_APPS:
    from unicms_calendar.settings import *

    CMS_HANDLERS_PATHS.extend(CMS_CALENDAR_HANDLERS_PATHS)
    CMS_APP_REGEXP_URLPATHS.update(CMS_CALENDAR_APP_REGEXP_URLPATHS)

    CMS_HOOKS.update(CMS_CALENDAR_HOOKS)
    MODEL_TO_MONGO_MAP.update(CMS_CALENDAR_MONGO_MAP)
# END UNICMS CALENDAR HANDLER

# UNICAL STORAGE HANDLER
if "unicms_unical_storage_handler" in INSTALLED_APPS:
    from unicms_unical_storage_handler.settings import *

    CMS_HANDLERS_PATHS.extend(CMS_STORAGE_HANDLERS_PATHS)
    CMS_APP_REGEXP_URLPATHS.update(CMS_STORAGE_APP_REGEXP_URLPATHS)

    ALLOWED_UNICMS_SITES = [2]
    ALLOWED_CDS_COURSETYPES = ['L','LM','LM5','LM6','M1-270','M2-270']
    ALLOWED_STRUCTURE_TYPES = ['ARE','DRZ', 'AMCEN', 'APL',
                               'DIP', 'MCRA','SET', 'SEV','SRZ',
                               'CDS', 'CEN', 'CCS', 'UDS', 'DIR']
    ALLOWED_ADDRESSBOOK_ROLES = ['PO', 'PA', 'RU', 'RD', 'ND', 'AR',
                                 'BS', 'CB', 'CC', 'DR', 'NM', 'DC']
    ALLOWED_TEACHER_ROLES = ['PO', 'PA', 'RU', 'RD']
    INITIAL_STRUCTURE_FATHER = "170005"

    CURRENT_YEAR = "2021"
# END UNICAL STORAGE HANDLER

SEARCH_ELEMENTS_IN_PAGE = 4

# DjangoSAML2 conf
if 'djangosaml2'  in INSTALLED_APPS:
    from saml2_sp.settings import *

    MIDDLEWARE.append('djangosaml2.middleware.SamlSessionMiddleware')

    # pySAML2 SP mandatory
    SESSION_EXPIRE_AT_BROWSER_CLOSE=True

    SAML2_URL_PREFIX = 'saml2'
    LOGIN_URL = f'/{SAML2_URL_PREFIX}/login'
    LOGOUT_URL = f'/{SAML2_URL_PREFIX}/logout'

    AUTHENTICATION_BACKENDS = (
        'django.contrib.auth.backends.ModelBackend',
        'djangosaml2.backends.Saml2Backend',
    )
else:
    LOCAL_URL_PREFIX = 'local'
    LOGIN_URL = f'/{LOCAL_URL_PREFIX}/login/'
    LOGOUT_URL = f'/{LOCAL_URL_PREFIX}/logout/'

LOGOUT_REDIRECT_URL=f'/{CMS_PATH_PREFIX}'

FILETYPE_IMAGE_YX_RATIO_MIN = 0.25
FILETYPE_IMAGE_YX_RATIO_MAX = 2
