Developer's
-----------

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


#### Models

The models are implemented within the following applications:
- **cms.contexts**, where websites, webpaths and EditorialBoard Users and Permissions can be defined
- **cms.templates**, where multiple page templates and blocks can be managed
- **cms.medias**, specific app for management, upload and navigation of media files.
- **cms.menus**, specific app for navigation bar management.
- **cms.carousels**, specific app for Carousel and Slider management.
- **cms.pages**, where we can create a Page linked to a Webpath.
- **cms.publications**, where Editorial boards publish contents in one or more WebPaths.
- **cms.search**, MongoDB Search Engine and management commands i.e. CLI.

The module `cms.contexts` defines the multitenancy feature. Each WebPath would have a related web pages. Each context have users (Editorial Board Editors) with single or multiple permissions (see `cms.contexts.settings.CMS_CONTEXT_PERMISSIONS`)

The modules `cms.page` and `cms.publications` defines how a Page or a Publication is built. A Page is nothing but a composition of blocks, rendered in a HTML base template. This means that a page is just container block where multiple block can be defined in different order and fashion. For every page we must define to context (webpath) belonging as well as the template that we wish to adopt to be rendered by HTML.


#### Post Pre Save Hooks

By default Pages and Publication calls pre and post save hooks. Django signals are registered in `cms.contexts.signals`. In `settings.py` we can register as many as desidered hooks within single or multiple models. Django signals will load them in each pre/post save/delete events.

````
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
    },
    'Media': {
        'PRESAVE': ['cms.medias.hooks.set_file_meta',
                    'cms.medias.hooks.webp_image_optimizer'],
        'POSTSAVE': [],
        'PREDELETE': [],
        'POSTDELETE': ['cms.medias.hooks.remove_file']
    },
    'Category': {
        'PRESAVE': ['cms.medias.hooks.webp_image_optimizer'],
        'POSTSAVE': [],
        'PREDELETE': [],
        'POSTDELETE': ['cms.medias.hooks.remove_file']
    },
    'PublicationAttachment': {
        'PRESAVE': ['cms.medias.hooks.set_file_meta',],
        'POSTSAVE': [],
        'PREDELETE': [],
        'POSTDELETE': []
    }
}
```` 


#### Template tags

The HTML template and/or an HTML page block can also adopt some of the template tags that shipped with uniCMS and Django.UniCMS template context by default comes with the following two objects:

````
    'webpath': Context object (cms.contexts.models.WebPath)
    'page': Page object (cms.pages.models.Page)
````

Based on informations taken from these objects as input uniCMS adopts some additionale custom templatetags as outlined below. These templatetags will also work in Page Blocks that would take, optionally, the HTML template as parameter.

###### cms_templates
supported_languages: get settings.LANGUAGES_CODE to templates

###### cms_menus
`load_menu`: eg, `{% load_menu section='menu-1' template="main_menu.html" %}`

###### cms_carousels
`load_carousel`: similar to `load_menu`

###### cms_contexts
`language_menu`: an usage example here:
   ````
       {% language_menu as language_urls %}
       {% for lang,url in language_urls.items %}
       <li><a class="list-item" href="{{ url }}"><span>{{ lang }}</span></a></li>
       {% endfor %}
   ````
###### breadcrumbs
`{% breadcrumbs template="breadcrumbs.html" %}`
   if template argument will be absent it will rely on `breadcrumbs.html` template.
`call`: `{% call obj=pub method='get_url_list' category_name=cat %}`
    Call any object method and also pass to it whatever `**kwargs`.

###### cms_page
`{% load_blocks section='slider' %}`
  it would be configured in the base templates and defines where the blocks would be rendered.
  it takes `section` as argument, to query/filter only the blocks that belongs to that section.

###### cms_publication
`{% load_publications_preview template="publications_preview.html" %}`
    - additional paramenters:
        template,
        section
        number=5
        in_evidence=False
        categories_csv="Didattica,Ricerca"
        tags_csv="eventi,ricerca"
`{% load_publication_content_placeholder template="publication_that.html" %}`
    - additional paramenters:
        template,
        section
        publication_id # optional
    This templatetags maps "page place holder blocks" with page 
    publications and show a publication content, according to
    the choosed template, where the "page place holder will be rendered.


#### Handlers

There are circumstances and scenarios where is necessary to create specific applications with templates and templatetags, detached from the pages that are configured within the CMS. 
The `cms.publications.handlers` for instance, it manages the pages for navigation of publications (List) and opening a publication (View).

In such scenario the handlers have to be registered in `settings.py` as follow:

````
CMS_PUBLICATION_VIEW_PREFIX_PATH = 'contents/news/view/'
CMS_PUBLICATION_LIST_PREFIX_PATH = 'contents/news/list'

CMS_PUBLICATION_URL_LIST_REGEXP = f'^(?P<context>[\/a-zA-Z0-9\.\-\_]*)({CMS_PUBLICATION_LIST_PREFIX_PATH})/?$'
CMS_PUBLICATION_URL_VIEW_REGEXP = f'^(?P<context>[\/a-zA-Z0-9\.\-\_]*)({CMS_PUBLICATION_VIEW_PREFIX_PATH})(?P<slug>[a-z0-9\-]*)'

CMS_APP_REGEXP_URLPATHS = {
    'cms.publications.handlers.PublicationViewHandler' : CMS_PUBLICATION_URL_VIEW_REGEXP,
    'cms.publications.handlers.PublicationListHandler' : CMS_PUBLICATION_URL_LIST_REGEXP,
}

CMS_HANDLERS_PATHS = [CMS_PUBLICATION_VIEW_PREFIX_PATH,
                      CMS_PUBLICATION_LIST_PREFIX_PATH]
````

The paths defined in `CMS_HANDLERS_PATHS` generates the list of reserved words to be considered during validation in `cms.contexts.models.WebPath`. Therefore, they create the list of reserved words that cannot be used as path value in `cms.contexts.models.WebPath`.


#### Middlewares

`cms.contexts.middleware.detect_language_middleware`:
   detects the browser user language checking both `?lang=` request arg 
   and the web browser default language. This required to 
   handle the Menu, Carousel and localized Publication.

`cms.contexts.middleware.show_template_blocks_sections`:
   toggles, for staff users, the display of block sections in pages.

`cms.contexts.middleware.show_cms_draft_mode`:
   toggles, for staff users, the draft view mode in pages.
