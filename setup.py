import os
import re
import sys

from glob import glob
from setuptools import setup, find_packages


with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()


_src_folder = 'src'
_pkg_name = 'cms'


def get_requirements(fname='requirements.txt'):
    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    fopen = open(fname, 'r')
    install_requirements = []
    dependency_links=[]
    packages = fopen.read().splitlines()
    for ir in packages:
        url = re.findall(regex, ir)
        install_requirements.append(ir) if not url \
        else dependency_links.append(url[0][0])
    return [install_requirements, dependency_links]

setup(
    name="unicms",
    version='1.0.0',
    description="uniCMS is a Django Web Content Management System",
    long_description=README,
    long_description_content_type='text/markdown',
    author='Giuseppe De Marco, Francesco Filicetti',
    author_email='giuseppe.demarco@unical.it, francesco.filicetti@unical.it',
    license="AGPL-3.0-or-later",
    url='https://github.com/UniversitaDellaCalabria/uniCMS',

    packages=[f"{_pkg_name}"],
    package_dir={f"{_pkg_name}": f"{_src_folder}/{_pkg_name}"},

    package_data={f"{_pkg_name}": [i.replace(f'{_src_folder}/{_pkg_name}/', '')
                                   for i in glob(f'{_src_folder}/{_pkg_name}/**',
                                                 recursive=True)]
    },

    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules"],
    install_requires=get_requirements()[0],
    dependency_links=get_requirements()[1],
    zip_safe=False,
    )
