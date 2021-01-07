import logging


logger = logging.getLogger(__name__)

# as documentation reference or default
CMS_PUBLICATION_VIEW_PREFIX_PATH = 'contents/news/view/'
CMS_PUBLICATION_LIST_PREFIX_PATH = 'contents/news/list'
CMS_PUBLICATION_URL_LIST_REGEXP = f'^(?P<webpath>[\/a-zA-Z0-9\.\-\_]*)({CMS_PUBLICATION_LIST_PREFIX_PATH})/?$' # noqa
CMS_PUBLICATION_URL_VIEW_REGEXP = f'^(?P<webpath>[\/a-zA-Z0-9\.\-\_]*)({CMS_PUBLICATION_VIEW_PREFIX_PATH})(?P<slug>[a-z0-9\-]*)' # noqa

CMS_HANDLERS_PATHS = [CMS_PUBLICATION_VIEW_PREFIX_PATH,
                      CMS_PUBLICATION_LIST_PREFIX_PATH]
CMS_APP_REGEXP_URLPATHS = {
    'cms.handlers.PublicationViewHandler' : CMS_PUBLICATION_URL_VIEW_REGEXP,
    'cms.handlers.PublicationListHandler' : CMS_PUBLICATION_URL_LIST_REGEXP,
}

# re.match(CMS_PUBLICATION_URL_REGEXP, '/content/posts/content/post/yessa-man-again-20')

# .groups()
# Out[29]: ('content/post/', 'yessa-man-again-20')

# .groupdict()
# {'slug': 'yessa-man-again-20'}


CMS_PAGE_SIZE = 3
