Setup
-----

#### Prepare Environment and Install Requirements

````
apt install python3-pip
pip3 install virtualenv
mkdir unicms_project && cd "$_"
virtualenv -ppython3 env
source env/bin/activate

pip install unicms
````

To complete the installation make sure you have correctly loaded unicms modules to your project settings file.

````
INSTALLED_APPS = [
    'accounts',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # templates - you can load your own templates
    'sass_processor',
    'bootstrap_italia_template',
    'unicms_template_italia', # for example
    'unicms_template_unical', # for example

    # unicms
    'nested_admin', # for admin CRUD
    'taggit', # page and publication tags
    'taggit-serializer', # taggit tags serializer
    'rest_framework' # api
    'cms.templates',
    'cms.contexts',
    'cms.carousels',
    'cms.menus',
    'cms.medias',
    'cms.pages',
    'cms.publications',
    'cms.api',
    'cms.search',
]
````

#### Getting Started

You can start the project/examples available in uniCMS repository as follow.
````
git clone https://github.com/UniversitaDellaCalabria/uniCMS.git
cd uniCMS/example
````

Prepare Database and Preload example data
````
./manage.py migrate

# install your templates in settings.INSTALLED_APPS and then create CMS template symbolic links
./manage.py unicms_collect_templates

# if you want to load some example datas
./manage.py loaddata ../dumps/cms.json

./manage.py createsuperuser
./manage.py runserver
````

Go to `/admin` and submit superuser credentials to start.


#### URLs

uniCMS URLs are fully managed with `cms.context` via admin interface.
This feature enable users to load/import third-party django applications. It's important to keep in mind that the user should configure django application URLs before defining uniCMS's own URLs. Otherwise uniCMS will intercept those parameters and there is a good chance that the user will hit 404 page. The user can set the environment variable `CMS_PATH_PREFIX` to a desidered path, eg: `portale/`, to restrict uniCMS URL matching to specified root path.

Here is an example of project urls.py
````
if 'cms.contexts' in settings.INSTALLED_APPS:
    urlpatterns += path('',
                        include(('cms.contexts.urls', 'cms'),
                                 namespace="unicms"),
                        name="unicms"),

if 'cms.api' in settings.INSTALLED_APPS:
    urlpatterns += path('',
                        include(('cms.api.urls', 'cms'),
                                namespace="unicms_api"),
                        name="unicms_api"),


if 'cms.search' in settings.INSTALLED_APPS:
    urlpatterns += path('',
                        include(('cms.search.urls', 'cms_search'),
                                namespace="unicms_search"),
                        name="unicms_search"),
````

URLs that match the namespace within configuration in the `urls.py` of the the master project will be handled by uniCMS. uniCMS can match two type of resources:

1. WebPath (Context) corresponsing to a single Page (Home page and associated pages)
2. Application Handlers, a typical example would be the Pubblication List and the View resources

for the latter, uniCMS uses some reserved keywords as prefix to specific URL routings.
These configurations are typically stored in settings file. See the following [Handlers](#handlers) for instance.

See `cms.contexts.settings` as example.
See `cms.contexts.views.cms_dispatcher` to figure how an HTTP request is intercepted and handled by uniCMS to establish if either to use a Handler or a Standard Page as response.


#### Settings

uniCMS by default have standard settings for its applications, in their respective settings.py file, as shown in the examples `cms/pages/settings.py` and `cms/contexts/settings.py`.
Each of these parameters declared can be added to your project general (global) `settings.py` file.

uniCMS parameters are the followings.

###### Editorial Board Permissions

````
CMS_CONTEXT_PERMISSIONS = (
                           (0, _('no permissions in context')),

                           (1, _('can translate content in their own context')),
                           (2, _('can translate content in their own context and descendants')),

                           (3, _('can edit content created by them in their own context')),
                           (4, _('can edit content in their own context')),
                           (5, _('can edit content in their own context and descendants')),

                           (6, _('can publish content created by them in their own context')),
                           (7, _('can publish content in their own context')),
                           (8, _('can publish content in their own context and descendants')),
                          )
````

###### Media

````
CMS_IMAGE_CATEGORY_SIZE = 128
CMS_IMAGE_THUMBSIZE = 128

# file validation
FILETYPE_PDF = ('application/pdf',)
FILETYPE_DATA = ('text/csv', 'application/json',
                 'application/vnd.ms-excel',
                 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                 'application/vnd.oasis.opendocument.spreadsheet',
                 'application/wps-office.xls',
                 )
FILETYPE_TEXT = ('text/plain',
                 'application/vnd.oasis.opendocument.text',
                 'application/msword',
                 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                )
FILETYPE_IMAGE = ('image/webp', 'image/jpeg', 'image/png',
                  'image/gif', 'image/x-ms-bmp')
FILETYPE_P7M = ('application/pkcs7-mime',)
FILETYPE_SIGNED = FILETYPE_PDF + FILETYPE_P7M
FILETYPE_ALLOWED = FILETYPE_TEXT + FILETYPE_DATA + FILETYPE_IMAGE + FILETYPE_SIGNED

# maximum permitted filename lengh in attachments, uploads
FILE_NAME_MAX_LEN = 128

FILE_MAX_SIZE = 5242880
````

###### Publications

````
# as per documentation reference or default
CMS_PUBLICATION_VIEW_PREFIX_PATH = 'contents/news/view/'
CMS_PUBLICATION_LIST_PREFIX_PATH = 'contents/news/list'

CMS_PUBLICATION_URL_LIST_REGEXP = f'^(?P<webpath>[\/a-zA-Z0-9\.\-\_]*)({CMS_PUBLICATION_LIST_PREFIX_PATH})/?$'
CMS_PUBLICATION_URL_VIEW_REGEXP = f'^(?P<webpath>[\/a-zA-Z0-9\.\-\_]*)({CMS_PUBLICATION_VIEW_PREFIX_PATH})(?P<slug>[a-z0-9\-]*)'
CMS_APP_REGEXP_URLPATHS = {
    'cms.handlers.PublicationViewHandler' : CMS_PUBLICATION_URL_VIEW_REGEXP,
    'cms.handlers.PublicationListHandler' : CMS_PUBLICATION_URL_LIST_REGEXP,
}

CMS_HANDLERS_PATHS = [CMS_PUBLICATION_VIEW_PREFIX_PATH,
                      CMS_PUBLICATION_LIST_PREFIX_PATH]

# content paginator
CMS_PAGE_SIZE = 3

CMS_HOOKS = {
    'Publication': {
        'PRESAVE': [],
        'POSTSAVE': ['cms.search.hooks.publication_se_insert',],
        'PREDELETE': ['cms.search.hooks.searchengine_entry_remove',],
        'POSTDELETE': []
    },
    'Page': {
        'PRESAVE': [],
        'POSTSAVE': ['cms.search.hooks.page_se_insert',],
        'PREDELETE': ['cms.search.hooks.searchengine_entry_remove',],
        'POSTDELETE': []
    }
}
````

###### Templates

````
# see unicms-templates
CMS_TEMPLATE_BLOCK_SECTIONS =

CMS_BLOCK_TYPES = (
                   ('cms.templates.blocks.HtmlBlock', 'HTML Block'),
                   ('cms.templates.blocks.JSONBlock', 'JSON Block'),
                   ('cms.templates.blocks.CarouselPlaceholderBlock', 'Carousel Placeholder Block'),
                   ('cms.templates.blocks.LinkPlaceholderBlock', 'Link Placeholder Block'),
                   ('cms.templates.blocks.PublicationContentPlaceholderBlock', 'Publication Content Placeholder Block'),
)

CMS_TEMPLATES_FOLDER = f'{BASE_DIR}/templates/unicms'
CMS_BLOCK_TEMPLATES = []
CMS_PAGE_TEMPLATES = []


CMS_LINKS_LABELS = (('view', _('View')),
                    ('open', _('Open')),
                    ('read more', _('Read More')),
                    ('more', _('More')),
                    ('get in', _('Get in')),
                    ('enter', _('Enter')),
                    ('submit', _('Submit')),
                    ('custom', _('custom'))
                  )
````

###### Redis (Cache)

uniCMS can cache HTTP responses based on relevant parameters outlined below:
````
################
# Django config
################

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

######################
# Redis uniCMS config
######################

CMS_CACHE_ENABLED = True

CMS_CACHE_KEY_PREFIX = 'unicms_'
# in seconds
CMS_CACHE_TTL = 25
# set to 0 means infinite
CMS_CACHE_MAX_ENTRIES = 0
# request.get_raw_uri() that matches the following would be ignored by cache ...
CMS_CACHE_EXCLUDED_MATCHES =  ['/search?',]
````

###### MongoDB (Search Engine)
uniCMS default search engine is built on top of mongodb.
Install and configure mongodb
````
apt install -y gnupg wget
wget -qO - https://www.mongodb.org/static/pgp/server-4.4.asc | sudo apt-key add -
echo "deb http://repo.mongodb.org/apt/debian buster/mongodb-org/4.4 main" | sudo tee /etc/apt/sources.list.d/mongodb-org-4.4.list
apt update
apt install -y mongodb-org

systemctl daemon-reload
systemctl enable mongod
systemctl start mongod
````

Create your default users, using mongo CLI as follow:
````
use admin
db.createUser(
  {
    user: "admin",
    pwd: "thatpassword"
    roles: [ { role: "userAdminAnyDatabase", db: "admin" }, "readWriteAnyDatabase" ]
  }
)

use unicms
db.createUser(
  {
    user: "unicms",
    pwd:  "thatpassword",
    roles: [{ role: "readWrite", db: "unicms" }]
  }
)

db.createUser(
  {
    user: "unicms_search",
    pwd:  "thatpassword",
    roles: [{ role: "read", db: "unicms" }]
  }
)

exit
````
Configure connection and default settings in settings.py
````
MONGO_URL = 'mongodb://10.0.3.217:27017'
MONGO_CONNECTION_PARAMS = dict(username='admin',
                               password='thatpassword',
                               connectTimeoutMS=5000,
                               socketTimeoutMS=5000,
                               serverSelectionTimeoutMS=5000)
MONGO_DB_NAME = 'unicms'
MONGO_COLLECTION_NAME = 'search'
MODEL_TO_MONGO_MAP = {
    'cms.pages.Page': 'cms.search.models.page_to_entry',
    'cms.publications.Publication': 'cms.search.models.publication_to_entry'
}

SEARCH_ELEMENTS_IN_PAGE = 25
````


Create your fulltext indexes with the help of **cms.search** CLI.
Remember that default_language is set to italian. Do the following to set your own language:
````
./manage.py cms_search_create_mongo_index -default_language english
````
