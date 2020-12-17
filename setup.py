import re
import sys

from glob import glob
from setuptools import setup, find_packages

_src_folder = 'src'
_pkg_name = 'cms'

setup(
    name="unicms",
    version='0.2.2',
    description="uniCMS is a Django Web Content Management System",
    author='Giuseppe De Marco, Francesco Filicetti',
    author_email='giuseppe.demarco@unical.it, francesco.filicetti@unical.it',
    license="Apache 2.0",
    url='https://github.com/UniversitaDellaCalabria/uniCMS',
    
    packages=[f"{_pkg_name}"],
    package_dir={f"{_pkg_name}": f"{_src_folder}/{_pkg_name}"},
    
    package_data={f"{_pkg_name}": [i.replace(f'{_src_folder}/{_pkg_name}/', '') 
                                   for i in glob(f'{_src_folder}/{_pkg_name}/**', 
                                                 recursive=True)]
    },
    
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Libraries :: Python Modules"],
    install_requires=[
        'django>=2.0,<4.0',
        'django-nested-admin>=3.3.2',
        'django-taggit',
        'pillow>=7.2.0',
        'python-magic>=0.4.18',
        'pymongo>=3.11.0',
        'django-rest-framework',
        'uritemplate',
        'pyyaml',
        'pydantic',
        'django-htmlmin>=0.11.0',
        'django-redis>=4.12.1'
        ],
    zip_safe=False,
    )
