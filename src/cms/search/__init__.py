import pymongo

from django.conf import settings as global_settings

default_app_config = 'cms.search.apps.CmsSearchConfig'


class MongoClientFactory(object):
    mongo_client = None

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls.mongo_client, cls) or \
           not cls.mongo_client.server_info():
            cls.mongo_client = pymongo.MongoClient(
                                global_settings.MONGO_URL,
                                **global_settings.MONGO_CONNECTION_PARAMS
            )
        return cls.mongo_client


def mongo_collection():
    client = MongoClientFactory()
    db = getattr(client, global_settings.MONGO_DB_NAME)
    return getattr(db, global_settings.MONGO_COLLECTION_NAME)
