Why we develop another CMS?
---------------------------

#### The Goal

We're searching for a limitless experience.
When we choose a CMS platform we approach different products and solutions based on the functionalities they offer, with particular attention to what could then prove to be a limit of use. Starting from our use cases, here are some typical arguments that emerge when choosing a CMS.

1. **Alteration of the structure of a Page**.
In Wordpress you cannot modify the structure of a page but only its content, to modify the structure we should modify its templates in php code. Usually plugins are used to additionally include iframes or js scripts because in fact this is forbidden in the publication of a new post.

2. **Implementation of large-scale services**.
Wordpress does not scale, it was designed as a personal blog therefore it does not aim to manage large volumes of traffic.

3. **Graphic customization (templates and structure)**.
All platforms require highly specialized development efforts within their environment. There are (expensive) plugins that damage the users' impression of customizing graphics, but these only offer predefined assets of ordinary solutions. Even on Drupal and Joomla the market team cannot do any graphic customization without involving a development team.

4. **Reuse of images in different contexts**.
Drupal allows it only if combined with some plugins that modify the post structure and also the publication method.

5. **Moving content from one context to another**.
In normal CMS this requires access and alteration of the contents present on the database and on the filesystem. In Drupal for example both the path on the filesystem and the information contained in the DB must be changed. in UniCMS it is possible to do this simply by referring the content to one or more webpaths.

6. **Content Inheritance**.
Drupal and other CMSs cannot inherit the contents of a parent page within a child page.

7. **High availability**.
Drupal does not have native support for HA.


#### What about other Django's CMS?

Wonderfull, but:

- they still need develop skills to get a real product
- some of them oversized during the time, with extensions and components that have made the approach and thinking behind the product non-linear
- they outsource integration with templates too much, probably hindering the most important marketplace in the industry
