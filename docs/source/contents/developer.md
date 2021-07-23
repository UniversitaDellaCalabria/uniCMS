Developer's
-----------

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

#### WebPaths

[WiP]

This section describes how WebPath works and how it can be configured.

- path value match
- child path behavior
- the role of **.get_full_path()**
- some use cases and strategies: third-party url, webpath aliases, intheritance by webpath childs


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

The HTML template and/or an HTML page block can also adopt some of the template tags that shipped with uniCMS and Django.
UniCMS template context by default comes with the following two objects:

````
    'webpath': Context object (cms.contexts.models.WebPath)
    'page': Page object (cms.pages.models.Page)
````

Based on informations taken from these objects as input uniCMS adopts some additionale custom templatetags as outlined below.
These templatetags will also work in Page Blocks that would take, optionally, the HTML template as parameter.

###### cms_carousels

* **load_carousel**<br>
renders in the template the first active carousel in section or the identified one,
with translated items.<br>
*arguments*: context, section, template, carousel_id<br>
*example*:
````
    {% load_carousel section="template-section" template="template.html" %}
    {% load_carousel carousel_id="1" %}
````

###### cms_contexts

* **breadcrumbs**<br>
builds webpath breadcrumbs. If leaf, appends leaf breadcrumbs.<br>
*arguments*: webpath, template (opt, default=breadcrumbs.html), leaf (opt)<br>
*example*: `{% breadcrumbs webpath=webpath template="breadcrumbs.html" %}`

* **call**<br>
calls any object method and also pass to it whatever `**kwargs`.<br>
*arguments*: obj, method, kwargs<br>
*example*: `{% call obj=publication method="get_url_list" category_name=cat %}`

* **language_menu**<br>
builds a data dict with {url:language} pairs.
If a template is present, passes it data.<br>
*arguments*: teamplate (opt)<br>
*example*:
````
   {% language_menu as language_urls %}
   {% for lang,url in language_urls.items %}
   <li><a class="list-item" href="{{ url }}"><span>{{ lang }}</span></a></li>
   {% endfor %}
````

###### cms_menus

* **load_menu**<br>
renders in the template the first active menu in section or the identified one,
with translated items.<br>
*arguments*: context, section, template, menu_id<br>
*example*:
````
    {% load_menu section="template-section" template="menu.html" %}
    {% load_menu menu_id="1" %}
````

###### cms_pages

* **cms_categories**<br>
returns all CMS content categories.<br>
*example*: `{% cms_categories %}`

* **load_blocks**<br>
it would be configured in the base templates and defines where the blocks would be rendered.
it takes `section` as argument, to query/filter only active blocks that belongs to that section.<br>
*arguments*: section (opt)<br>
*example*: `{% load_blocks section="banner" %}`

* **load_link**<br>
gets a URL as parameter and pass it to a template.<br>
*arguments*: template, url<br>
*example*: `{% load_link url="https://myvideo.it" template="iframe-video.html" %}`

* **load_page_title**<br>
returns a translated page title.<br>
*arguments*: page<br>
*example*: `{% load_page_title page=page %}`

###### cms_publication

* **load_publication**<br>
pass a single active publication to a template.<br>
*arguments*: template, publication_id<br>
*example*: `{% load_publication publication_id="1" template="publication-layout.html" %}`

* **load_publications_preview**<br>
returns all published publications in a context and passes them to a template.<br>
*arguments*: template, section (opt), number (opt, default=6),
in_evidence (opt, default=False), categories_csv (opt),
exclude_categories (opt, default=False), tags_csv (opt)<br>
*example*:
````
    {% load_publications_preview template="publ.html" number="3" %}
    {% load_publications_preview template="publ.html" categories="Research, Study" %}
    {% load_publications_preview template="publ.html" categories="Research" exclude_categories=True %}
    {% load_publications_preview template="publ.html" tags_csv="read, sport" %}
    {% load_publications_preview template="publ.html" in_evidence=True %}
````

###### cms_templates

* **blocks_in_position**<br>
returns True if there are active blocks in passed position or its childs, else False.<br>
*arguments*: position<br>
*example*: `{% blocks_in_position position="section-1" %}`

* **supported_languages**<br>
returns settings.LANGUAGES<br>
*example*: `{% supported_languages %}`












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

#### Example data

If you want to dump and share your example data:
````
./manage.py dumpdata --exclude auth.permission --exclude accounts --exclude contenttypes --exclude sessions --exclude admin --indent 2 > ../dumps/cms.json
````
