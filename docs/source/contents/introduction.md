Introduction
------------

uniCMS have few base components

- **Web Sites**, fully qualified doman name to answer for
- **Contexts**, WebPaths like `/offices` and `/offices/employees` 
- **Page templates**, with a selectable html template though UI
- **Block templates**, elements that renders things whitin to one or many pages
- **Navigation Bars**, menu, footers, lists of things that can optionally fetch elements from Publications
- **Carousels**, image sliders ... Yes, they are a basic component of the modern web
- **Pages**, each webpath loads a page and this is a container of blocks
- **Publications**, what we use to say __posts__
- **Handlers**, a way to intercept http requests and show a different behaviour from a Page. 
Think about the **List** and **View** resources of News pertaining to a context (WebPath)


#### How to think in uniCMS

The fastest answer to our questions would be to list the steps to take to create a site:

1. Choose the template you want to use, see Templates section of this guide 
2. Define your blocks and Page templates to be inherited by your Website's pages
3. Create a WebSite Domain name
4. Fill contents, Categories, Publications, Menus ...
5. Create a webpath, '/'
6. Create a Page with many blocks as we like

... Handlers will show the history of your Publications (**List**) and will 
let the user read them (**View**).


#### Example project

Probably the quickest way to get started is to run a platform 
demonstration starting with a project with few basic pages.

This project aims to exemplify the design of a common University Web Portal.
You'll find a simplified generalization of all
the entities that usually make up a Content Management System (CMS).

[uniCMS Example Project](https://github.com/UniversitaDellaCalabria/Portale-PoC)
