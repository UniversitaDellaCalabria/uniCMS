How it works
------------

This section is dividend in the two other sections, the first is intended for advanced 
users (admin and editorial board users) and the second for developers or 
advanced users that are cuoriuos about how the things are done internally.


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
