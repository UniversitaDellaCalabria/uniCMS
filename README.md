# uniCMS

uniCMS is a Web Application Content Management System developed using  **Django Framework**. The project is created by a group of passionate developers who introduces bespoke design and architecture for a next generation CMS.

Setup
-----

#### Requirements

````
apt install python3-pip
pip3 install virtualenv
mkdir Portale-PoC && cd "$_"
git clone https://github.com/UniversitaDellaCalabria/Portale-PoC.git
virtualenv -ppython3 env
source env/bin/activate
pip3 install -r requirements.txt
cd Portale-PoC
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

#### Redis (Cache)

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
CMS_MAX_ENTRIES = 0
# request.get_raw_uri() that matches the following would be ignored by cache ...
CMS_CACHE_EXCLUDED_MATCHES =  ['/search?',]
````

#### MongoDB (Search Engine)
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
    pwd: "yourpasswd"
    roles: [ { role: "userAdminAnyDatabase", db: "admin" }, "readWriteAnyDatabase" ]
  }
)

use unicms
db.createUser(
  {
    user: "unicms",
    pwd:  "yourpassword",
    roles: [{ role: "readWrite", db: "unicms" }]
  }
)

db.createUser(
  {
    user: "unicms_search",
    pwd:  "yourpassword",
    roles: [{ role: "read", db: "unicms" }]
  }
)

exit
````
Configure connection and default settings in settings.py
````
MONGO_URL = 'mongodb://10.0.3.217:27017'
MONGO_CONNECTION_PARAMS = dict(username='admin',
                               password='yourpassword',
                               connectTimeoutMS=5000,
                               socketTimeoutMS=5000,
                               serverSelectionTimeoutMS=5000)
MONGO_DB_NAME = 'unicms'
MONGO_COLLECTION_NAME = 'search'
MODEL_TO_MONGO_MAP = {
    'cms.pages.Page': 'cms.search.models.page_to_entry',
    'cms.publications.Publication': 'cms.search.models.publication_to_entry'
}
````


Create your fulltext indexes. Default_language is set to italian by default.
````
./manage.py cms_search_create_mongo_index -default_language english
````

For the installation steps with examples please consult the documentation at **/docs/source/contents/how_it_works.rst**

#### Getting started with uniCMS

The simpler and easier way to create a web site in uniCMS consist of the following steps:

1. Select the template to be used. Refer to **Templates** section of this guide 
2. Define your **blocks and Page templates** to be inherited by your Website's pages
3. **Create a WebSite** Domain name
4. Fill contents like Categories, Publications, Menus ...
5. **Create a WebPath**, a root node like '/' or a subdirectory
6. Create a Page with as much as blocks you'd like.
   Dispose menus, carousels and things with regular blocks or publication contents (or part of them) using placeholder blocks.


Features and specs of uniCMS:

- The default template shipped with:
    - Compatibility and interoperability in mobile platforms
    - SEO optimized
    - Bootstrap like design and structure
    - Plugin mode and compatibility for Django applications
- Agile and adaptive design and logic (ah-hoc and easy customization)
- **OpenAPIv3** (OAS3) compliant
- Compatible with the major RDBMS engines with agile schema migrations capabilities
- **Multitenancy - create and manage multple web applications within single platform** 
- **Query and search capabilities - `MongoDB FullText Search`** via CLI
- Extensive localization with **multiple languages**
- Ability to handle Editorial Board workflows (WiP) and permissions by contexts
- High performance thanks to its cached model based on Redis TTL
- Security by design - security by default
- Robust enterprise and scalable
- Plugin model and rich interoperability with multiple frameworks and technologies

uniCMS is designed for both end users and developers where the developers can create their own customzied web applications (CMS) without starting one from scratch and end users without any development skills can setup a professional CMS platform without difficulty.

uniCMS was created due to necessity of creation and design of a new protal for the University of Calabria. After evaluation of several options, University of Calabria having a strong in-house competitive and highly skilled technical team it was decided to opt for the development of a brand new CMS solution based on Django framework. 

The entire uniCMS project code is open sourced and therefore licensed under the [Apache 2.0 (https://en.wikipedia.org/wiki/Apache_License)].


For any other information please consult the [Official Documentation](https://unicms.readthedocs.io/) and feel free to contribute the project or open issues.




