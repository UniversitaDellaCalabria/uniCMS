# uniCMS

![CI build](https://github.com/UniversitadellaCalabria/uniCMS/workflows/uniCMS/badge.svg)
![Python version](https://img.shields.io/badge/license-Apache%202-blue.svg)
[![codecov](https://codecov.io/gh/UniversitadellaCalabria/uniCMS/branch/main/graph/badge.svg)](https://codecov.io/gh/UniversitadellaCalabria/uniCMS)
![License](https://img.shields.io/badge/python-3.6%20%7C%203.7%20%7C%203.8%20%7C%203.9-blue.svg)

uniCMS is a Web Application Content Management System developed using  **Django Framework**. 
The project is created by a group of passionate developers who introduces bespoke 
design and architecture for a next generation CMS.


Setup
-----

For the installation steps please consult the 
[documentation](https://unicms.readthedocs.io/en/main/contents/setup.html#prepare-environment-and-install-requirements)


Demo project
------------

The quickest way to get started with uniCMS is to run a demo platform with a few basic websites, pages and contents.

[uniCMS Example Project](https://github.com/UniversitaDellaCalabria/uniCMS/tree/main/example)


Getting started
---------------

The simpler and easier way to create a web site in uniCMS consist of the following steps:

1. Select the template to be used. Refer to **Templates** section of this guide 
2. Define your **blocks and Page templates** to be inherited by your Website's pages
3. **Create a WebSite** Domain name
4. Fill contents like Categories, Publications, Menus ...
5. **Create a WebPath**, a root node like '/' or a subdirectory
6. Create a Page with as much as blocks you'd like.
   Dispose menus, carousels and things with regular blocks or publication contents (or part of them) using placeholder blocks.


Features
--------

- The default template shipped with:
    - Compatibility and interoperability in mobile platforms
    - SEO optimized
    - Bootstrap like design and structure
    - Plugin mode and compatibility for Django applications
- Agile and adaptive design and logic (ah-hoc and easy customization)
- **OpenAPIv3** (OAS3) compliant
- Compatible with the major RDBMS engines with agile schema migrations capabilities
- **Multitenancy - create and manage multple web applications within single platform** 
- **Query and search capabilities - `MongoDB FullText Search`** via CLI
- Extensive localization with **multiple languages**
- Ability to handle Editorial Board workflows (WiP) and permissions by contexts
- High performance thanks to its cached model based on Redis TTL
- Security by design - security by default
- Robust enterprise and scalable
- Plugin model and rich interoperability with multiple frameworks and technologies

uniCMS is designed for both end users and developers where the developers can create their 
own customzied web applications (CMS) without starting one from scratch and end users 
without any development skills can setup a professional CMS platform without difficulty.

uniCMS was created due to necessity of creation and design of a new protal for the 
University of Calabria. After evaluation of several options, University of Calabria 
having a strong in-house competitive and highly skilled technical team it was decided 
to opt for the development of a brand new CMS solution based on Django framework. 

The entire uniCMS project code is open sourced and therefore licensed under 
the [Apache 2.0](https://en.wikipedia.org/wiki/Apache_License).


For any other information please consult the 
[Official Documentation](https://unicms.readthedocs.io/) and feel free 
to contribute the project or open issues.


Tests
-----

````
# activate your virtualenv first, then
cd example
coverage erase ; coverage run ./manage.py test cms; coverage report -m
````

###### Hints for developers

Please run these before doing new commits
````
pip install -r requirements-dev.txt

autopep8 -r --in-place   ../src/cms/
flake8 ../src/cms --count --exit-zero --statistics 

# auto flake0
autoflake -r --in-place  --remove-unused-variables --expand-star-imports --remove-all-unused-imports ../src/cms/
````



