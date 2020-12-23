How it works
------------

This section describes which entities and relations composes uniCMS and 
how these latter handles HTTP Requests.


.. image:: ../images/relations_2.png


HTTP Requests
*************

HTTP Requests are handled by a pure Django view called **cms.contexts.views.cms_dispatch**.
It will:

1. check if a website exists
2. check if **request.get_full_path()** matches one of the Handlers loaded in **settings.py**. 
    - If Yes -> return **handler.as_view()**
    - Else: continue
3. check if **request.get_full_path()** matches a published page
    - If Yes -> return **render(request, page.base_template.template_file, context)**
    - Else: `raise 404()`


WebPaths
********

[WiP]

In this section is described how the WebPath works and how they can be configured.

- path value matching
- child path behaviour
- the role of **.get_full_path()**
- some use cases and strategies: third-party url, webpath aliases, intheritance by webpath childs


NavigationBars and Menus
************************

[WiP]

In this section is described how the Menu can be built.

- Menu object
- MenuItem objects
- How a MenuItem can inherit contents from a publication
- Render an Interactive Menu in a HTML template, references to uniCMS's' Teamplates documentation


Publications and Handlers
*************************

Publications or Posts are something that are added daily by an Editorial Board.

.. image:: ../images/publication_admin_backend.png
    :align: center

We would publish some news about a specific topic, as it would be a 
simple Web Blog, achieving following things as well:

- standard or custom template to represent a pubblication on the screen
- breadcrumbs manager that represent a human readable, interactive, webpath
- page with a list of all the posts, also filtered by category

If the concept of publication or post is clear to all those who have 
published at least once in their life in a WebBlog, an extra effort is 
to understand the fact that uniCMS allows us to:

- create a post and decide in which context (WebPath) it would be published, in one or many places (Contexts)
- manage a block, called *publication_preview* for example, that represent 
  an fancy list of all the publications that belongs to that webpath

Handlers will show the history of your Publications (**List**) and will 
let the user read them (**View**).


Pages, Blocks and Placeholders
******************************************************

Pages inherit Template Pages, these latter have a base html template file and optionally
a bunch of template blocks. Blocks can be of different type, like the 
simplest one called HTMLBlock that's a Text Field that takes 
a raw html with django's template statements. This means that in a HTMLBlock we can load 
template tags and use Django Template filters and statements, as we use to do 
following the Official Django Documentation.

Furthermore, there are specialized blocks which are none other than 
HTMLBlock with django *templatetags* as content. Example:

.. code-block:: html

    {% load unicms_blocks %}
    <div class="row negative-mt-5 mb-3" >
        <div class="col-12 col-md-3">
            <div class="section-title-label px-3 py-1">
                <h3>Unical <span class="super-bold">world</span></h3>
            </div>
        </div>
    </div>

    <div class="row">
        <div class="col-12 col-lg-9">
            {% load_publications_preview template="publications_preview_v3.html" %}
        </div>
        <div class="col-12 col-lg-3">
            {% include "unical_portale_agenda.html" %}
        </div>
    </div>


A Page Template html file would be subdivided in several sections, each of them where a Django 
templatetag called **load_blocks** will fill contents. Example:

.. code-block:: html

    <!-- Breadcrumbs -->
    {% block breadcrumbs %}
        {% load_blocks section="breadcrumbs" %}
    {% endblock breadcrumbs %}
    <!-- end Breadcrumbs -->


Placeholders are a different type of block.
We have, for example, **PublicationPlaceholderBlock** that's a block that will be filled 
by a related publication to the page it belongs to. Let's suppose to distribute 
four publication placeholders in a page, then we link 4 publications to the same page.
We'll have that each publication will be rendered in the Handler Block, 
respecting order and positioning (section).

+------------+-----------------+------------------------------+
| index      | block type      | publication                  |
+============+=================+==============================+
| 0          | pub placeholder | the first ordered by "order" |
+------------+-----------------+------------------------------+
| 1          | pub placeholder | the second ordered by "order"| 
+------------+-----------------+------------------------------+
| 2          | pub placeholder | the third ordered by "order" |
+------------+-----------------+------------------------------+

A PublicationPlaceHolder would take also a specialized template, this
permit to users to adopt their own style, their way to specialize the representation 
of contents taken from a publication. For example a template that takes 
a publication object that decide how and what render from it: 
the title, subheading, main body content, related objects ...

Finally the first placeholder 
will render the first content, the second the second one and so on. 
This approach allows a one-page template designer to arrange placeholders 
without worrying about what content will be represented there. 
The page that will inherit this uniCMS template will then define which 
publications to import, which web link to handle and so on. 
Think about the management of a 
Home Page, where each content is selectively chosen by publishers.

A page can have the following child elements:

- PAGE NAVIGATION BARS 
- PAGE CAROUSELS
- PAGE BLOCKS, extends or disable those inherited from the Page Template
- PUBLICATION CONTENTS
- RELATED PAGES
- RELATED LINKS

This is a simplified page subdivided by sections that would show to us 
how the contents can be distribuited in a Page Template.


.. image:: ../images/page_blocks_2.png
    :align: center
