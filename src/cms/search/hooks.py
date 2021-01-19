import logging

from django.conf import settings as global_settings
from django.utils import timezone

from . import mongo_collection
from . models import page_to_entry, publication_to_entry

logger = logging.getLogger(__name__)


MONGO_DB_NAME = getattr(global_settings, 'MONGO_DB_NAME')
MONGO_COLLECTION_NAME = getattr(global_settings, 'MONGO_COLLECTION_NAME')


def page_se_insert(page_object):
    collection = mongo_collection()
    search_entry = page_to_entry(page_object)
    # check if it doesn't exists or remove it and recreate
    doc_query = {"content_type": page_object._meta.label,
                 "content_id": search_entry['content_id']}
    doc = collection.find_one(doc_query)
    if doc:
        collection.delete_many(doc_query)
        logger.info(f'{page_object} removed from search engine')

    if page_object.is_publicable:
        doc = collection.insert_one(search_entry)

    logger.info(f'{page_object} succesfully indexed in search engine')


def publication_se_insert(pub_object):
    collection = mongo_collection()

    contexts = pub_object.publicationcontext_set.filter(is_active=True).\
        order_by('date_start')

    search_entry = publication_to_entry(pub_object, contexts)
    if search_entry:
        search_entry = search_entry
    else:
        return
    # check if it doesn't exists or remove it and recreate
    doc_query = {"content_type": pub_object._meta.label,
                 "content_id": search_entry['content_id']}
    doc = collection.find_one(doc_query)
    if doc:
        collection.delete_many(doc_query)
        logger.info(f'{pub_object} removed from search engine')

    now = timezone.localtime()
    publicable_context = contexts.filter(date_start__lte=now,
                                         date_end__gt=now)

    # if pub_object.is_publicable:
    if publicable_context:
        doc = collection.insert_one(search_entry)

    logger.info(f'{pub_object} succesfully indexed in search engine')


def searchengine_entry_remove(obj):
    collection = mongo_collection()
    doc_query = {"content_type": obj._meta.label,
                 "content_id": obj.pk}
    collection.delete_many(doc_query)
    logger.info(f'{obj} removed from search engine')
