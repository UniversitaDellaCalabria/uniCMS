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
                 "content_id": str(page_object.pk)}
    doc = collection.find_one(doc_query)
    if doc:
        collection.delete_many(doc_query)
        logger.info(f'{page_object} removed from search engine')

    if page_object.is_publicable:
        doc = collection.insert_one(search_entry)

    logger.info(f'{page_object} succesfully indexed in search engine')


def publication_se_insert(pub_object, *args, **kwargs):
    collection = mongo_collection()
    doc_query = {"content_type": pub_object._meta.label,
                 "content_id": str(pub_object.pk)}
    # remove old if it exists
    doc = collection.find_one(doc_query)
    if doc:
        collection.delete_many(doc_query)
        logger.info(f'{pub_object} removed from search engine')

    # if publication isn't active, return
    if not pub_object.is_active: return

    # check if publication has active and publicable contexts
    now = timezone.localtime()
    contexts = pub_object.publicationcontext_set\
                         .filter(is_active=True,
                                 date_start__lte=now,
                                 date_end__gt=now)\
                         .order_by('date_start')

    if kwargs.get('exclude_context'):
        contexts = contexts.exclude(pk=kwargs['exclude_context'])

    # get data to entry
    search_entry = publication_to_entry(pub_object, contexts)
    if not search_entry: return

    # if pub_object.is_publicable:
    if contexts:
        doc = collection.insert_one(search_entry)

    logger.info(f'{pub_object} succesfully indexed in search engine')


def publication_context_se_insert(pubctx_object, *args, **kwargs):
    pub_object = pubctx_object.publication
    publication_se_insert(pub_object, *args, **kwargs)


def publication_context_se_delete(pubctx_object, *args, **kwargs):
    pub_object = pubctx_object.publication
    publication_se_insert(pub_object,
                          exclude_context=pubctx_object.pk,
                          *args, **kwargs)


def searchengine_entry_remove(obj):
    collection = mongo_collection()
    doc_query = {"content_type": obj._meta.label,
                 "content_id": str(obj.pk)}
    collection.delete_many(doc_query)
    logger.info(f'{obj} removed from search engine')
