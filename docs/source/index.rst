.. uniCMS documentation master file, created by
   sphinx-quickstart on Sat Dec 19 15:42:17 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to uniCMS's Documentation
==================================

uniCMS is a Web Content Management System built on top of **Django Framework**, wrote by 
young IT guys that think that a nowadays CMS should be:

- Loaded with a ready to use Template:
    - Mobile ready
    - SEO convenient
    - Bootstrap compliant
    - Pluggable as a Django application
- Highly oriented to a logic of content reuse, entries can be reused - or only in pieces - in different contexts, as you like and with many strategies
- **OpenAPIv3** (OAS3)
- Able to use many RDBMS engines, agile schema migrations ops as Django wonderfully does
- **Multi Web Site** management
- **MongoDB FullText Search** engine with management commands
- Able to **Localize in many languages** its entries, by default
- Able to handle Editorial Board workflows (WiP) and permissions by contexts
- Able to handle huge loads, Cached approach based on Redis TTL
- Secure by default
- Scalable

unlike other Django's CMS, uniCMS is intended for both end users 
and smart developers, creating a website with uniCMS does not require any development skills.

uniCMS was born as a result of the need to renew the web portal of the 
University of Calabria, after taking a look at the offer of free and open CMS 
and strong of our experience, we decided to develop it with Django and equip it **with batteries** as well.

If you agree with us feel free to participate in its development or simply use it and 
give us your feedbacks, we are people who like to share!


.. toctree::
   :maxdepth: 2
   :caption: Introduction

   contents/introduction.md
   contents/why.md
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


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
