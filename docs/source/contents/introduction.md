Introduction
------------

For the correct usage of uniCMS we must familiarize ourselves with the following components:

- **Web Sites**, fully qualified domain name
- **Contexts**, WebPaths like `/offices` and `/offices/employees` 
- **Page templates**, with a selectable html template file through UI
- **Block templates**, elements that render things within single or multiple pages
- **Navigation Bars**, menu, footers, lists of things that can optionally fetch elements from Publications (titles, body, images ...) to enrich its items
- **Carousels**, image sliders ... They are the basic components of the modern web so we decided to customize them as well
- **Pages**, each webpath loads a page that's modular container of the page blocks
- **Publications**, a typical __posts__
- **Handlers**, they intercept HTTP requests providing different perspective of a standard Page
  Immagine the **List** and **View** resources of a News pertaining to a context (WebPath) or a way to integrate a third party Django app in uniCMS.


#### How to start with uniCMS

The simpler and easier way to create a web site in uniCMS consist of the following steps:

1. Select the template to be used. Refer to **Templates** section of this guide 
2. Define your **blocks and Page templates** to be inherited by your Website's pages
3. **Create a WebSite** Domain name
4. Fill contents like Categories, Publications, Menus ...
5. **Create a WebPath**, a root node like '/' or a subdirectory
6. Create a Page with as much as blocks you'd like.
   Dispose menus, carousels and things with regular blocks or publication contents (or part of them) using placeholder blocks.


#### Simple Example

The quickest way to get started with uniCMS is to run a demo platform with a few basic websites, pages and contents.

This project aims to simplify the design and implementation of a typical web portals designed for Universities/Colleges/Academic world.
You'll find a simplified generalization of all entities aimed to build a common Content Management System (CMS).

[uniCMS Example Project](https://github.com/UniversitaDellaCalabria/Portale-PoC)
