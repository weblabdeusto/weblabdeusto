#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2012 onwards University of Deusto
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#
# This software consists of contributions made by many individuals,
# listed below:
#
# Author: Pablo Orduña <pablo@ordunya.com>
#

import os
from distutils.core import setup

# Taken from django setup.py :-)
def fullsplit(path, result=None):
    """
    Split a pathname into components (the opposite of os.path.join) in a
    platform-neutral way.
    """
    if result is None:
        result = []
    head, tail = os.path.split(path)
    if head == '':
        return [tail] + result
    if head == path:
        return result
    return fullsplit(head, [tail] + result)

packages   = []
data_files = []

for weblab_dir in ['voodoo','weblab','experiments']:
    for dirpath, dirnames, filenames in os.walk(weblab_dir):
        # Ignore dirnames that start with '.'   
        for i, dirname in enumerate(dirnames):
            if dirname.startswith('.'): 
                del dirnames[i]

        if '__init__.py' in filenames:
            packages.append('.'.join(fullsplit(dirpath)))
        elif filenames:
            data_files.append([dirpath, [os.path.join(dirpath, f) for f in filenames]])

scripts = [ '../admin/scripts/weblab-admin.py' ]

classifiers=[
    "Development Status :: 5 - Production/Stable",
    "Environment :: Web Environment",
    "Intended Audience :: Developers",
    "License :: Freely Distributable",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Programming Language :: Python :: 2",
    "Topic :: Internet :: WWW/HTTP",
    "Topic :: Software Development :: Libraries :: Application Frameworks",
]

cp_license="BSD"

install_requires = [ 
    'sqlalchemy>=0.7',
    'SOAPpy',
    'ZSI',
    'pyflakes',
    'mocker',
    'mock',
    'python-openid<2.3',
    'ciutils',
    'redis',
    'hiredis',
]

setup(name='weblabdeusto',
      version='4.0',
      description="WebLab-Deusto Remote Laboratory Management System",
      classifiers=classifiers,
      author='WebLab-Deusto Team',
      author_email='weblab@deusto.es',
      url='http://code.google.com/p/weblabdeusto/',
      packages=packages,
      data_files=data_files,
      license=cp_license,
      scripts=scripts,
      install_requires=install_requires,
     )
