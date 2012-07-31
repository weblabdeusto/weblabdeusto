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
import glob
import shutil
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

if not os.path.exists('weblabdeusto_data'):
    os.mkdir('weblabdeusto_data')

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
            new_path = os.path.join('weblabdeusto_data', dirpath)
            try:
                os.makedirs(new_path)
            except:
                pass
            
            for f in filenames:
                if os.path.exists(os.path.join(new_path, f)):
                    os.remove(os.path.join(new_path, f))
                shutil.copy2(os.path.join(dirpath, f), os.path.join(new_path, f))

if len(glob.glob("../../client/war/weblabclient/*.html")) > 0:
    # The client has been compiled. Let's copy it here.
    shutil.rmtree("weblabdeusto_data/war", True)
    shutil.copytree("../../client/war/","weblabdeusto_data/war")
else:
    print "Client was not compiled"
    # TODO: try to compile it. If it fails, show the reason and download it
    # TODO: in the weblab-admin script, choose between the absolute directory
    # to the source code and sys.prefix

for dirpath, dirnames, filenames in os.walk('weblabdeusto_data'):
    # Ignore dirnames that start with '.'   
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): 
            del dirnames[i]

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

install_requires = []
for line in open('requirements.txt'):
    if line.find('#') >= 0:
        package_name = line[:line.find('#')]
    else:
        package_name = line
    if package_name.strip() != '':
        install_requires.append(package_name)

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
