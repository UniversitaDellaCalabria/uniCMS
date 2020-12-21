Common Tasks
------------

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


#### Urls

All the urls that matches the namespace configured in the `urls.py` of the master project
will be handled by uniCMS. uniCMS can match two kind of resources:

1. WebPath (Context) corresponsing at a single Page (Home page and its childs)
2. Application Handlers, an example would be Pubblication List and Views resources

for these latter uniCMS uses some reserved words, as prefix, to deal with specialized url routings.
in the settings file we would configure these. See [Handlers](#handlers) for example.

See `cms.contexts.settings` as example.
See `cms.contexts.views.cms_dispatcher` to see how an http request is intercepted and handled by uniCMS to know if use an Handler or a Standard Page as response.


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


#### Api

see `/openapi.json` and `/openapi` for OpenAPI v3 Schema.
