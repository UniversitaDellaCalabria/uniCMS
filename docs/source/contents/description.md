Description
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


#### Models

This project is composed by the following applications:
- **cms.contexts**, where websites, webpaths and EditorialBoard Users and Permissions can be defined
- **cms.templates**, where multiple page templates and page blocks can be managed
- **cms.medias**, specialized app for management, upload and navigation of media files.
- **cms.menus**, specialized app for navigation bar creation and management.
- **cms.carousels**, specialized app for Carousel and Slider creation and management.
- **cms.pages**, where Editorial boards can create Pages.
- **cms.publications**, where Editorial boards publish contents in one or more WebPath.
- **cms.search**, MongoDB Search Engine and management commands.

The module `cms.contexts` defines the multiple website management (multi contexts) we have adopted.
Each context mail ches a Path and a web page, it's nothing more than a
webpath. Each context has users (Editorial Board Editors) with one or more
of the following permissions (see `cms.contexts.settings.CMS_CONTEXT_PERMISSIONS`):

`cms.page` and `cms.publications` are the models where we've defined how we build a Page or a Publication.
For us, a Page, is anything else than a composition of blocks, rendered in a
HTML base template. This means that a page is a block container, in which we can
define many blocks with different order. For every page we must define
to which context (webpath) it belong to and also the template that we want to adopt for HTML rendering.
Nothing prevents us from using something other than HTML, it's just python, you know.

#### Permissions

````
CMS_CONTEXT_PERMISSIONS = (('1', _('can edit created by him/her in his/her context')),
                           ('2', _('can edit all pages in his/her context')),
                           ('3', _('can edit all pages in his/her context and descendants')),
                           ('4', _('can translate all pages in his/her context')),
                           ('5', _('can translate all pages in his/her context and descendants')),
                           ('6', _('can publish created by him/her in his/her context')),
                           ('7', _('can publish all pages in his/her context')),
                           ('8', _('can publish all pages in his/her context and descendants')),
                           )
````

#### i18n

*Menus*, *Carousels*, *Publications* and *Categories* can also be localized in one or many languages via Web 
Backend, if a client browser have a Spanish localization the rendering system will render all the spanish
localized block, if they occour, otherwise it will switch to default
language.

All the gettext values defined in our static html template will be handled as django localization use to do.
