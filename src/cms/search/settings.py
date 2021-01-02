MONGO_URL = 'mongodb://localhost:27017'
MONGO_DB_PARAMS = dict(connectTimeoutMS=5000,
                       socketTimeoutMS=5000,
                       serverSelectionTimeoutMS=5000)
MONGO_DB_NAME = 'unicms'
MONGO_COLLECTION_NAME = 'search'

MODEL_TO_MONGO_MAP = {
    'cmspages.Page': 'cms.search.models.page_to_entry',
    'cmspublications.Publication': 'cms.search.models.publication_to_entry'
}

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

SEARCH_ELEMENTS_IN_PAGE = 25
