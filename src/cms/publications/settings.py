import logging


logger = logging.getLogger(__name__)

# as documentation reference or default
CMS_PUBLICATION_VIEW_PREFIX_PATH = 'contents/news/view'
CMS_PUBLICATION_LIST_PREFIX_PATH = 'contents/news/list'
CMS_PUBLICATION_RSS_PREFIX_PATH = 'contents/news/rss'
CMS_PUBLICATION_URL_LIST_REGEXP = f'^(?P<webpath>[\/a-zA-Z0-9\.\-\_]*)({CMS_PUBLICATION_LIST_PREFIX_PATH})/?$' # noqa
CMS_PUBLICATION_URL_RSS_REGEXP = f'^(?P<webpath>[\/a-zA-Z0-9\.\-\_]*)({CMS_PUBLICATION_RSS_PREFIX_PATH})/?$' # noqa
CMS_PUBLICATION_URL_VIEW_REGEXP = f'^(?P<webpath>[\/a-zA-Z0-9\.\-\_]*)({CMS_PUBLICATION_VIEW_PREFIX_PATH})/(?P<id>[0-9]*)-(?P<slug>[a-zA-Z0-9\-\_]*)' # noqa

CMS_HANDLERS_PATHS = [CMS_PUBLICATION_VIEW_PREFIX_PATH,
                      CMS_PUBLICATION_LIST_PREFIX_PATH,
                      CMS_PUBLICATION_RSS_PREFIX_PATH]
CMS_APP_REGEXP_URLPATHS = {
    'cms.handlers.PublicationViewHandler' : CMS_PUBLICATION_URL_VIEW_REGEXP,
    'cms.handlers.PublicationListHandler' : CMS_PUBLICATION_URL_LIST_REGEXP,
    'cms.handlers.PublicationRssHandler' : CMS_PUBLICATION_URL_RSS_REGEXP,
}

# re.match(CMS_PUBLICATION_URL_REGEXP, '/content/posts/content/post/yessa-man-again-20')

# .groups()
# Out[29]: ('content/post/', 'yessa-man-again-20')

# .groupdict()
# {'slug': 'yessa-man-again-20'}


CMS_PAGE_SIZE = 3

# HTML sanitization of publication content (nh3)
# allowed elements cover the HTML produced by CKEditor 5 plugins
# (images with caption/resize, code blocks, todo lists, tables, list styles)
# and by markdown conversion
CMS_PUBLICATION_ALLOWED_TAGS = {
    'a', 'b', 'blockquote', 'br', 'caption', 'code', 'div', 'em',
    'figcaption', 'figure', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'hr',
    'i', 'img', 'input', 'label', 'li', 'ol', 'p', 'pre', 's', 'span',
    'strong', 'table', 'tbody', 'td', 'tfoot', 'th', 'thead', 'tr',
    'u', 'ul',
}
CMS_PUBLICATION_ALLOWED_ATTRIBUTES = {
    '*': {'class', 'style'},
    'a': {'href', 'title', 'target'},
    'img': {'src', 'alt', 'title', 'width', 'height'},
    'input': {'type', 'checked', 'disabled'},
    'td': {'colspan', 'rowspan'},
    'th': {'colspan', 'rowspan'},
}
CMS_PUBLICATION_ALLOWED_STYLE_PROPERTIES = {'list-style-type', 'margin-left',
                                            'text-align', 'width'}
CMS_PUBLICATION_ALLOWED_URL_SCHEMES = {'http', 'https', 'mailto', 'tel'}
