Introduction
------------

For a correct use of uniCMS we must familiarize 
ourselves with the following components:

- **Web Sites**, fully qualified doman name to answer for
- **Contexts**, WebPaths like `/offices` and `/offices/employees` 
- **Page templates**, with a selectable html template file through UI
- **Block templates**, elements that renders things whitin one or many pages. There are also the PlaceHolder Blocks that fill related contents, like publications (posts)
- **Navigation Bars**, menu, footers, lists of things that can optionally fetch elements from Publications (titles, body, images ...) to enrich its items
- **Carousels**, image sliders ... They are a basic components of the modern web so we desided to specialized them as well
- **Pages**, each webpath loads a page that's a modular container of page blocks
- **Publications**, what we use to say __posts__
- **Handlers**, they intercepts http requests showing to users a different behaviour from a standard Page., linked to a specific WebPath.
  Think about the **List** and **View** resources of News pertaining to a context (WebPath) or 
  a way to integrate a third party Django app in uniCMS.


#### How to think in uniCMS

The fastest answer to our questions would be to list the following 
steps, to create a site we would:

1. Choose the template we want to use, see **Templates** section of this guide 
2. Define your **blocks and Page templates** to be inherited by your Website's pages
3. **Create a WebSite** Domain name
4. Fill contents like Categories, Publications, Menus ...
5. **Create a WebPath**, a root node like '/' or a child of this latter
6. Create a Page with many blocks as we like.
   Dispose menus, carousels and things with regular blocks or 
   publications contents (or part of them) using placeholders blocks.


#### Example project

The quickest way to get started with uniCMS is to run a platform 
demo with few basic websites, pages and contents.

This project aims to exemplify the design of a common University Web Portal.
You'll find a simplified generalization of all
the entities that usually make up a Content Management System (CMS).

[uniCMS Example Project](https://github.com/UniversitaDellaCalabria/Portale-PoC)
