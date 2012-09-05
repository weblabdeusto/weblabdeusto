#!/usr/bin/env python
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

"""
setup.py is a setuptools script that installs WebLab-Deusto in your system.
Running "python setup.py install" will install it, and then you can run the
"weblab-admin" command to create and manage instances. It is highly 
recommended to use virtualenv first to create a user-level environment.
"""

import os
import shutil
from setuptools import setup

# TODO: in the weblab-admin script, choose between the absolute directory
# to the source code and sys.prefix

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

##########################################################
# 
# 
#       S O A P     S T U B S  ( O P T I O N A L )
# 
# 

import weblab.comm.util as comm_util
comm_util.deploy_stubs()

##########################################################
#
# 
#       C L I E N T 
# 
# 

CLIENT_LOCATION = os.path.abspath(os.path.join('..','..','client'))
WAR_LOCATION = os.path.join(CLIENT_LOCATION,'war')
from weblab.admin.client_deploy import compile_client
compile_client(WAR_LOCATION, CLIENT_LOCATION)

# In any case, the client was compiled in the past or just now. Let's copy it here.
print "Copying...",
shutil.rmtree(os.path.join('weblabdeusto_data', 'war'), True)
shutil.copytree(WAR_LOCATION, os.path.join('weblabdeusto_data', 'war'))
shutil.rmtree(os.path.join('weblabdeusto_data', 'war', 'WEB-INF'), True)
print "[done]"

##########################################################
#
# 
#       P A C K A G E S    A N D     F I L E S
# 
# 

if not os.path.exists('weblabdeusto_data'):
    os.mkdir('weblabdeusto_data')

packages     = []
data_files   = []

for weblab_dir in ['voodoo','weblab','experiments','webserver']:
    for dirpath, dirnames, filenames in os.walk(weblab_dir):
        # Ignore dirnames that start with '.'   
        for i, dirname in enumerate(dirnames):
            if dirname.startswith('.'): 
                del dirnames[i]

        if '__init__.py' in filenames:
            packages.append('.'.join(fullsplit(dirpath)))

        non_python_files = [ filename for filename in filenames if not filename.endswith(('.py','.pyc','.pyo')) ]
        if non_python_files:
            new_path = os.path.join('weblabdeusto_data', dirpath)
            try:
                os.makedirs(new_path)
            except:
                pass
            
            for f in non_python_files:
                if os.path.exists(os.path.join(new_path, f)):
                    os.remove(os.path.join(new_path, f))
                shutil.copy2(os.path.join(dirpath, f), os.path.join(new_path, f))


for dirpath, dirnames, filenames in os.walk('weblabdeusto_data'):
    # Ignore dirnames that start with '.'   
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): 
            del dirnames[i]

    if len(filenames) > 0:
        data_files.append([dirpath, [os.path.join(dirpath, f) for f in filenames]])

##########################################################
#
# 
#       R E Q U I R E M E N T S
# 
# 
def load_requires(dest, filename):
    for line in open(filename):
        if line.find('#') >= 0:
            package_name = line[:line.find('#')]
        else:
            package_name = line
        if package_name.strip() != '':
            dest.append(package_name)

install_requires = []
tests_require    = []

load_requires(install_requires, 'requirements.txt')
load_requires(install_requires, 'requirements_recommended.txt')
load_requires(tests_require,    'requirements_testing.txt')

##########################################################
#
# 
#       G E N E R A L
# 
# 

scripts = [ 'weblab/admin/weblab-admin', 'weblab/admin/weblab-bot' ]

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

setup(name='weblabdeusto',
      version='5.0',
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
      tests_require=tests_require,
      test_suite="develop.suite",
      zip_safe=False,
     )
