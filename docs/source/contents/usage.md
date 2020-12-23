uniCMS Components
-----------------

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

#### Page Blocks

A configurable object that would be rendered in a specified section of the page (as defined in its base template).
It can take a long Text as content, a json objects or whatever, it dependes by Block Type.
Examples:

- A pure HTML renderer
- A Specialized Block element that take a json object in its object constructor

The following descriptions covers some HTML blocks.
As we can see the HTML blocks in uniCMS have a full support of Django templatetags and template context.


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
it widely use the load_publications_preview templatetag, this 
template tags loads all the pubblication related to the WebPath (CMS Context) 
of the Page.

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

A WebPath (context) can have multiple Menus and Navigation bars, but also Footers.
Menu can be fetched through Rest API `/api/menu/<menu_id:int>` and also updated/created through this resources.

Each menu items can have three kinds of links: url, page, publication.
Each menu items can get additional contents (`inherited_contents`) from a publication, this means that
a presentation url, or a subheading or whatever belonging to a publication can be made accessible during a 
menu items representation. Think about presentati in images, additional links ...


#### Api

see `/openapi.json` and `/openapi` for OpenAPI v3 Schema.
