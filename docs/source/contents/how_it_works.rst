How it works
------------

This section describes which entities and relations composes uniCMS and 
how these latter handles the HTTP Requests.


.. image:: ../images/relations.png


HTTP Requests
*************

1. http requests are handled by **cms.contexts.views.cms_dispatch**
2. check if website exists
3. check if **request.get_full_path()** matches on of the Handlers loaded in **settings.py**. 
    - If Yes -> return **handler.as_view()**
    - Else: continue
4. check if **request.get_full_path()** matches to a published page
    - If Yes -> return **render(request, page.base_template.template_file, context)**
    - Else: `raise 404()`


Publications and Handlers
*************************

Publications or Posts are something that are added daily by an Editorial Board.
We would publish some news about a specific topic and we want each of following things as well:

- create a menu item that links to a specific post
- have a custom or a personalized template to show a pubblication
- have a breadcrumbs manager that represent a human readable, interactive, webpath
- have a page with a list of all the posts, and also filtered by category

If the concept of publication or post is clear to all those who have 
published at least once in their life in a WebBlog, an extra effort is 
to understand the fact that uniCMS allows us to:

- create a post and decide in which context (webpath) it would be published, one or many
- manage a block, called publication_preview for example, that represent 
  an automatic preview of all the publications that belongs to that webpath

Handlers will show the history of your Publications (**List**) and will 
let the user read them (**View**).


Pages, Blocks and Placeholders
******************************************************

Pages inherit Template Pages, these latter have a base html template file and 
a bunch of template blocks. Blocks can be of different kind, like the 
simplest one, called HTMLBlock that anything is that a Text Field that takes 
a Django compatible templates. This means that in a HTMLBlock we can load 
template tags and use Django Template filters and statements.

Furthermore, there are specialized blocks which are none other than 
HTMLBlock which load django template tags within their content.

A Page Template would be subdivided in section each of them where a Django 
templatetag called **load_blocks** will fill contents.

Placeholders are a different kind of blocks, each one for many kind of application.
We have, for example, PublicationPlaceholderBlock that's a block that will be filled 
by related publication to a page. Let's suppose to distribute 4 pub placeholder in a page, 
and then we configure 4 publication to belong to the same page. Then we'll have
that each publication will be rendered in the Handler Blocks in this way:


+------------+-----------------+------------------------------+
| index      | block type      | publication                  |
+============+=================+==============================+
| 0          | pub placeholder | the first ordered by "order" |
+------------+-----------------+------------------------------+
| 1          | pub placeholder | the second ordered by "order"| 
+------------+-----------------+------------------------------+
| 2          | pub placeholder | the third ordered by "order" |
+------------+-----------------+------------------------------+


.. image:: ../images/page_blocks.png
