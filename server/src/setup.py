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
import sys
import subprocess
import glob
import shutil
from setuptools import setup

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

def deploy_stubs(folder, wsdl_file, filename):        
    wsdl2py       = 'wsdl2py'
    wsdl2dispatch = 'wsdl2dispatch'

    for i in glob.glob("%s/%s_*.py" % (folder, filename)):
        os.remove(i)
    cwd = os.getcwd()
    os.chdir(folder)

    pr = subprocess.Popen(wsdl2py + " -e -f %s --simple-naming" % wsdl_file, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    result = pr.wait()
    if result != 0:
        for i in pr.stdout.read().split('\n'):
            if i.strip() != '':
                print 'INFO: stdout::%s' % i
        for i in pr.stderr.read().split('\n'):
            if i.strip() != '':
                print >> sys.stderr, 'ERR: stderr::%s' % i
        print >> sys.stderr, "ERR: wsdl2py script failed"
        os.chdir(cwd)
        return True
    if VERY_VERBOSE:
        for i in pr.stdout.read().split('\n'):
            if i.strip() != '':
                print 'INFO: stdout::%s' % i
        for i in pr.stderr.read().split('\n'):
            if i.strip() != '' and i.find("DeprecationWarning: the multifile module has been deprecated") < 0 and i.find("import multifile, mimetools") < 0:
                print >> sys.stderr, 'WARN: stderr::%s' % i

    # Little bug in the stubs generation :-)
    client_file = open('%s_client.py' % filename,'a')
    client_file.write('\n\nfrom %s_messages import *\n\n' % filename)
    client_file.close()

    # By default, ZSI strips the strings in the SOAP request. We don't want this, so we change this behaviour
    services_types_content = open('%s_services_types.py' % filename).read()
    services_types_content = services_types_content.replace("ZSI.TC.String(","ZSI.TC.String(strip=False,")
    open('%s_services_types.py' % filename,'w').write(services_types_content)

    pr = subprocess.Popen(wsdl2dispatch + " -e -f %s --simple-naming" % wsdl_file, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    result = pr.wait()
    os.chdir(cwd)
    if result != 0:
        for i in pr.stdout.read().split('\n'):
            if i.strip() != '':
                print 'INFO: stdout::%s' % i
        for i in pr.stderr.read().split('\n'):
            if i.strip() != '':
                print >> sys.stderr, 'ERR: stderr::%s' % i
        print >> sys.stderr, "ERR: wsdl2dispatch script failed"
        return True
    if VERY_VERBOSE:
        for i in pr.stdout.read().split('\n'):
            if i.strip() != '':
                print 'INFO: stdout::%s' % i
        for i in pr.stderr.read().split('\n'):
            if i.strip() != '' and i.find("DeprecationWarning: the multifile module has been deprecated") < 0 and i.find("import multifile, mimetools") < 0:
                print 'WARN: stderr::%s' % i
    
    return False

try:
    import ZSI
except ImportError:
    print >> sys.stderr, "Skipping stubs and skeletons deployment; ZSI not installed"
else:
    deploy_stubs(os.path.join('weblab', 'login', 'comm', 'generated'), os.path.join('..', 'LoginWebLabDeusto.wsdl'), 'loginweblabdeusto')
    deploy_stubs(os.path.join('weblab','core','comm','generated'), os.path.join('..', 'UserProcessingWebLabDeusto.wsdl'), 'weblabdeusto')


##########################################################
#
# 
#       P A C K A G E S 
# 
# 

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

##########################################################
#
# 
#       C L I E N T 
# 
# 

if len(glob.glob("../../client/war/weblabclientlab/*.html")) > 0:
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

scripts = [ 'weblab/admin/weblab-admin.py' ]

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
      tests_require=tests_require,
      test_suite="launch_tests.suite",
     )
