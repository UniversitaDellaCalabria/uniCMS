.. uniCMS documentation master file, created by
   sphinx-quickstart on Sat Dec 19 15:42:17 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to uniCMS's Documentation
==================================

uniCMS is a Web Application Content Management System developed using  **Django Framework**. The project is created by a group of passionate developers who introduces bespoke design and architecture for a next generation CMS.

Features and specs of uniCMS:

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
- Able to handle Editorial Board workflows (WiP) and permissions by contexts
- High performance thanks to its cached model based on Redis TTL
- Security by design - security by default
- Robust enterprise and scalable
- Plugin model and rich interoperability with multiple frameworks and technologies

uniCMS is designed for both end users and developers where the developers can create their 
own customzied web applications (CMS) without starting one from scratch and end users 
without any development skills can setup a professional CMS platform without difficulty.

uniCMS was created due to necessity of creation and design of a new protal for the 
University of Calabria. After evaluation of several options, University of Calabria 
having a strong in-house competitive and highly skilled technical team it was 
decided to opt for the development of a brand new CMS solution based on Django framework. 

The entire uniCMS project code is open sourced and therefore licensed under 
the [Apache 2.0](https://en.wikipedia.org/wiki/Apache_License).


For any other information please consult the 
[Official Documentation](https://unicms.readthedocs.io/) and feel free 
to contribute the project or open issues.


.. toctree::
   :maxdepth: 2
   :caption: Introduction

   contents/introduction.md
   contents/how_it_works.md
   
.. toctree::
   :maxdepth: 2
   :caption: Getting started

   contents/setup.md
   contents/templates.rst
   contents/search_engine.md
   
.. toctree::
   :maxdepth: 2
   :caption: Usage

   contents/usage.md

.. toctree::
   :maxdepth: 2
   :caption: Developer's

   contents/developer.md

.. toctree::
   :maxdepth: 2
   :caption: Miscellaneous
   
   contents/why.md


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
