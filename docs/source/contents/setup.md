Setup
-----

#### Prepare Environment

````
apt install python3-pip
pip3 install virtualenv
mkdir unicms_project && cd "$_"
virtualenv -ppython3 env
source env/bin/activate

pip install unicms
````

You can even start the project / example available in the official uniCMS repository.

To complete the installation remeber to load unicms' app to your project settings file.
````
INSTALLED_APPS = [
    'accounts',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'sass_processor',
    'bootstrap_italia_template',

    'taggit',
    'nested_admin',

    'cms.templates',
    'cms.contexts',
    'cms.carousels',
    'cms.menus',
    'cms.medias',
    'cms.pages',
    'cms.publications',
    'cms.api',
    'cms.search',

    'unicms_template_italia', # for example
    'unicms_template_unical', # for example
    
    'rest_framework' # api
]
````

#### URLs

uniCMS URLs are fully managed with `cms.context` via admin interface. 
It enables user to load/import third-party django applications. It's important to keep in mind that the user should configures django application URLs
before defining uniCMS's own URLs. Otherwise uniCMS will intercept those parameters and there is a good chance that the user will hit 404 page. The user can set the environment variable `CMS_PATH_PREFIX` to a desidered path, eg: `portale/`, to restrict uniCMS URL matching to specified root path.

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
See `cms.contexts.views.cms_dispatcher` to figure how an HTTP request is intercepted and handled by uniCMS in order to establish if either to use a Handler or a Standard Page as response.


#### Settings

uniCMS by default have standard settings for its applications, in their settings.py file,
as for example `cms/pages/settings.py` or `cms/contexts/settings.py`.
Each of the parameters declared in them can be overloaded in your project 
general `settings.py` file.

uniCMS parameters are the followings.

###### Editorial Board Permissions

````
CMS_CONTEXT_PERMISSIONS = (('1', _('edit created by them in their own context')),
                           ('2', _('edit all pages in their own context')),
                           ('3', _('edit all pages in their own context and descendants')),
                           ('4', _('translate all pages in their own context')),
                           ('5', _('translate all pages in their own context and descendants')),
                           ('6', _('publish created by them in their own context')),
                           ('7', _('publish all pages in their own context')),
                           ('8', _('publish all pages in their own context and descendants')),
                           )
````

###### Medias

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
# as documentation reference or default
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


#### Getting Started

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

If you want to dump and share your example data:
````
./manage.py dumpdata --exclude auth.permission --exclude accounts --exclude contenttypes --exclude sessions --exclude admin --indent 2 > ../dumps/cms.json
````

###### Redis (Cache)

uniCMS can cache HTTP responses based on relevant parameters outlined below:
````
################
# Django related
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
# Redis uniCMS related
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
Remember that default_language is set to italian by default.
````
./manage.py cms_search_create_mongo_index -default_language english
````
