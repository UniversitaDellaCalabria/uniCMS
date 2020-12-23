Setup
-----

#### Environment

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

# install your templates in settings.INSTALLED_APPS and then create cms templates symbolic links
./manage.py unicms_collect_templates

# if you want to load some example datas
./manage.py loaddata ../dumps/cms.json

./manage.py createsuperuser
./manage.py runserver
````

Go to `/admin` and submit superuser credentials to start working in.

If you want to dump and share your example datas
````
./manage.py dumpdata --exclude auth.permission --exclude accounts --exclude contenttypes --exclude sessions --exclude admin --indent 2 > ../dumps/cms.json
````

#### Redis (Cache)

uniCMS can cache http responses, these are the relevant parameters:
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

Create your defaults users, using mongo CLI
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
Configure connection and defaults in settings.py
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
````


Create your fulltext indexes. Default_language is italian by default.
````
./manage.py cms_search_create_mongo_index -default_language english
````
