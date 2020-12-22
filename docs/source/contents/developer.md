Developer's
-----------

#### Urls

uniCMS urls are managed with `cms.context` entirely through admin interface. 
We can even load third-party django applications, it's necessary to take into account that you should your django urls
paths before defining uniCMS ones, otherwise uniCMS will intercept them and with a good chance will 
return to the user a page of 404. You can even set `CMS_PATH_PREFIX` to a desidered value, eg: `portale/`, to 
restrict uniCMS url matching to a specified namespace.

This is and example of your project urls.py 
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

All the urls that matches the namespace configured in the `urls.py` of the master project
will be handled by uniCMS. uniCMS can match two kind of resources:

1. WebPath (Context) corresponsing at a single Page (Home page and its childs)
2. Application Handlers, an example would be Pubblication List and View resources

for these latter uniCMS uses some reserved words, as prefix, to deal with specialized url routings.
in the settings file we would configure these. See [Handlers](#handlers) for example.

See `cms.contexts.settings` as example.
See `cms.contexts.views.cms_dispatcher` to see how an http request is intercepted and 
handled by uniCMS to know if use an Handler or a Standard Page as response.


#### Post Pre Save Hooks

By default Pages and Publications call pre and post save hooks.
Django signals are registered in `cms.contexts.signals`.
In `settings.py` we can register as many as desidered hooks to one or more 
models, Django signals will load them on each pre/post save/delete event.

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
    }
}
```` 


#### Template tags

A cms template or a HTML page block can also adopt some of the template tags that come with uniCMS.
UniCMS template context takes at least the following objects:

````
    'website': WebSite object (cms.context.models.Website)
    'path': request.get_full_path(), eg: "/that/resource/slug-or-whatever"
    'webpath': Context object (cms.contexts.models.WebPath)
    'page': Page object (cms.pages.models.Page)
````

Standing on the informations taken from these objects uniCMS also adopts some other custom templatetags, as follow.
These templatetags will also work in Page Blocks that would take, optionally, a html template as argument.

`cms_templates`
- supported_languages: get settings.LANGUAGES_CODE to templates

`cms_menus`
- `load_menu`: eg, `{% load_menu section='menu-1' template="main_menu.html" %}`

`cms_carousels`
- `load_carousel`: similar to `load_menu`

`cms_contexts`
- `language_menu`: an usage example here:
   ````
       {% language_menu as language_urls %}
       {% for lang,url in language_urls.items %}
       <li><a class="list-item" href="{{ url }}"><span>{{ lang }}</span></a></li>
       {% endfor %}
   ````
- `breadcrumbs`: `{% breadcrumbs template="breadcrumbs.html" %}`
   if template argument will be absent it will rely on `breadcrumbs.html` template.
- `call`: `{% call obj=pub method='get_url_list' category_name=cat %}`
    Call any object method and also pass to it whatever `**kwargs`.

`cms_page`
- `load_blocks`: `{% load_blocks section='slider' %}`
  it would be configured in the base templates and defines where the blocks would be rendered.
  it takes `section` as argument, to query/filter only the blocks that belongs to that section.

`cms_publication`
- `load_publications_preview`: `{% load_publications_preview template="publications_preview.html" %}`
    - additional paramenters:
        template,
        section
        number=5
        in_evidence=False
        categories_csv="Didattica,Ricerca"
        tags_csv="eventi,ricerca"
- `load_publication_content_placeholder`: `{% load_publication_content_placeholder template="publication_that.html" %}`
    - additional paramenters:
        template,
        section
        publication_id # optional
    This templatetags maps "page place holder blocks" with page 
    publications and show a publication content, according to
    the choosed template, where the "page place holder will be rendered.


#### Handlers

There are cases in which it is necessary to create specialized applications, 
with templates and templatetags, detached from the pages configured within the CMS. 
Think, for example, to `cms.publications.handlers` which manages the pages for navigating 
publications (List) and opening a publication (View).

In this case the handlers have to be registered in `settings.py`, as follow:

````
CMS_PUBLICATION_VIEW_PREFIX_PATH = 'contents/news/view/'
CMS_PUBLICATION_LIST_PREFIX_PATH = 'contents/news/list'
CMS_PUBLICATION_URL_LIST_REGEXP = f'^(?P<context>[\/a-zA-Z0-9\.\-\_]*)({CMS_PUBLICATION_LIST_PREFIX_PATH})/?$'
CMS_PUBLICATION_URL_VIEW_REGEXP = f'^(?P<context>[\/a-zA-Z0-9\.\-\_]*)({CMS_PUBLICATION_VIEW_PREFIX_PATH})(?P<slug>[a-z0-9\-]*)'

CMS_HANDLERS_PATHS = [CMS_PUBLICATION_VIEW_PREFIX_PATH,
                      CMS_PUBLICATION_LIST_PREFIX_PATH]
CMS_APP_REGEXP_URLPATHS = {
    'cms.publications.handlers.PublicationViewHandler' : CMS_PUBLICATION_URL_VIEW_REGEXP,
    'cms.publications.handlers.PublicationListHandler' : CMS_PUBLICATION_URL_LIST_REGEXP,
}
````

The paths defined in `CMS_HANDLERS_PATHS`  make up the list of 
reserved words, to be considered during validation on save, in `cms.contexts.models.WebPath`. 
They compose a list of reserved words that cannot be used 
as path value in `cms.contexts.models.WebPath`.


#### Middlewares

`cms.contexts.middleware.detect_language_middleware`:
   detects the browser user language checking both `?lang=` request arg 
   and the web browser default language. It's needed to 
   handle Menu, Carousel and Publication localizations.

`cms.contexts.middleware.show_template_blocks_sections`:
   toggles, for staff users, the display of block sections in pages.

`cms.contexts.middleware.show_cms_draft_mode`:
   toggles, for staff users, the draft view mode in pages.
