uniCMS Components
-----------------

#### Permissions

````
CMS_CONTEXT_PERMISSIONS = (
                           (1, _('can translate content in their own context')),
                           (2, _('can translate content in their own context and descendants')),

                           (3, _('can edit content created by them in their own context')),
                           (4, _('can edit content in their own context')),
                           (5, _('can edit content in their own context and descendants')),

                           (6, _('can publish content created by them in their own context')),
                           (7, _('can publish content in their own context')),
                           (8, _('can publish content in their own context and descendants')),
                          )
````

#### i18n

*Menus*, *Carousels*, *Publications* and *Categories* can also be localized in a single or multiple languages via Web Backend. If for instance a client browser have a Spanish localization the rendering system will render all the spanish localized block, if it is present otherwise it will switch to default language.

All the gettext values defined in our static HTML template will be handled the same way django localization does.

#### Page Blocks

A configurable object that would be rendered in a specified section of the page (as defined in the base template).
It can take a long Text input as content, a json object or whatever given in input depending the Block Type.
Examples:

- Native HTML renderer
- Customized Block element that take a json object in input for its object constructor

The following description covers some of HTML blocks.
As we can see the HTML blocks in uniCMS is fully supported by Django templatetags and the native Django template context.


*Load Image slider (Carousel) configured for the Page*
````
{% load unicms_carousels %}
{% load_carousel section='slider' template="unical_portale_hero.html" %}

<script>
$(document).ready(function() {
  $("#my-slider").owlCarousel({
      navigation : true, // Show next and prev buttons
      loop: true,
      slideSpeed : 300,
      paginationSpeed : 400,
      autoplay: true,
      items : 1,
      itemsDesktop : false,
      itemsDesktopSmall : false,
      itemsTablet: false,
      itemsMobile : false,
      dots: false
  });
});
</script>
````

*Load Publication preview in a Page*
The load_publications_preview templatetag is widely used. This template tag loads all of the pubblication and associated stuff to its WebPath (CMS Context) of the Page.

````
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
````

*Youtube iframes*
As simple as possibile, that bunch of HTML lines.
````
<div class="row">
<div class="col-12 col-md-6">
<iframe width="100%" height="315" src="https://www.youtube.com/embed/ArpMSujC8mM" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
</div>
 <div class="col-12 col-md-6">
<iframe width="100%" height="315" src="https://www.youtube.com/embed/xrjjJGqZpcU" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
</div>
 </div>
````


#### Menu

A WebPath can have multiple Menus and Navigation bars.
Menu can be fetched through a Rest API `/api/menu/<menu_id:int>` and also updated/created through the same.

Each menu item can have three types of links: raw url, page object or publication object.
Each menu item can get additional contents (`inherited_contents`) from the publication. This means that a presentation url, or a subheading or whatever belonging to a publication can be made accessible during the representation of the menu items. Think about images, additional links and things that would fill up a menu entry.


#### Api

see `/openapi.json` and `/openapi` for OpenAPI v3 Schema.
