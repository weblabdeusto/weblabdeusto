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
import stat
import subprocess
import glob
import zipfile
import shutil
import urllib2
import StringIO
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

if len(glob.glob(WAR_LOCATION + "/*/*.cache.html")) > 5:
    print >> sys.stderr
    print >> sys.stderr, "A compiled version of the WebLab-Deusto client was found, and it will "
    print >> sys.stderr, "be used. If you have not recently compiled it and you have upgraded or"
    print >> sys.stderr, "modified anything in the client, you should compile it before doing"
    print >> sys.stderr, "this. So as to compile it, run:"
    print >> sys.stderr
    curpath = os.path.abspath('.')
    if sys.platform.find('win') == 0:
        print >> sys.stderr, "   %s> cd %s" % (curpath, CLIENT_LOCATION)
        print >> sys.stderr, "   %s> gwtc" % CLIENT_LOCATION
    else:
        print >> sys.stderr, "   user@machine:%s$ cd %s" % (curpath, CLIENT_LOCATION)
        print >> sys.stderr, "   user@machine:%s$ ./gwtc.sh" % CLIENT_LOCATION
    print >> sys.stderr
    print >> sys.stderr, "And then run the setup.py again."
    print >> sys.stderr
else:
    print >> sys.stderr, ""
    print >> sys.stderr, "No WebLab-Deusto compiled client found. Trying to compile it..."

    try:
        subprocess.Popen(["javac", "--help"], shell=False, stdout = subprocess.PIPE, stderr = subprocess.PIPE).wait()
    except:
        print >> sys.stderr, ""
        print >> sys.stderr, "Java compiler not found. Please, install the Java Development Kit (JDK)."
        print >> sys.stderr, ""
        print >> sys.stderr, "In Windows, you may need to download it from:"
        print >> sys.stderr, ""
        print >> sys.stderr, "    http://java.oracle.com/ "
        print >> sys.stderr, ""
        print >> sys.stderr, "And install it. Once installed, you should add the jdk directory to PATH."
        print >> sys.stderr, "This depends on the particular version of Windows, but you can follow "
        print >> sys.stderr, "the following instructions to edit the PATH environment variable and add"
        print >> sys.stderr, "something like C:\\Program Files\\Oracle\\Java\\jdk6\\bin to PATH:"
        print >> sys.stderr, ""
        print >> sys.stderr, "    http://docs.oracle.com/javase/tutorial/essential/environment/paths.html"
        print >> sys.stderr, ""
        print >> sys.stderr, "In Linux systems, you may install openjdk from your repository and "
        print >> sys.stderr, "will be configured."
        sys.exit(-1)

    # 
    # Check that GWT is downloaded. Download it otherwise.
    # 
    
    GWT_VERSION = 'gwt-2.4.0'
    GWT_URL = "http://google-web-toolkit.googlecode.com/files/%s.zip" % GWT_VERSION
    external_location = os.path.join(CLIENT_LOCATION, 'external')
    gwt_location = os.path.join(external_location,'gwt')

    if 'GWT_HOME' not in os.environ and not os.path.exists(gwt_location):
        print >> sys.stderr, ""
        print >> sys.stderr, "WebLab-Deusto relies on Google Web Toolkit (GWT). In order to compile "
        print >> sys.stderr, "the client, we need to download it. If you had already downloaded it, "
        print >> sys.stderr, "place it in: "
        print >> sys.stderr, ""
        print >> sys.stderr, "     %s" % gwt_location
        print >> sys.stderr, ""
        print >> sys.stderr, "or somewhere else and create an environment variable called GWT_HOME pointing"
        print >> sys.stderr, "to it. Anyway, I will attempt to download it and place it there."
        print >> sys.stderr, ""
        print >> sys.stderr, "Downloading... (please wait a few minutes; GWT is ~90 MB)"
        try:
            os.mkdir(external_location)
        except OSError, IOError:
            pass # Could be already created

        # TODO: this places in memory the whole file (~90 MB). urllib.urlretrieve?
        gwt_content = urllib2.urlopen(GWT_URL).read()
        gwt_fileobj = StringIO.StringIO(gwt_content)
        del gwt_content
        print >> sys.stderr, "Downloaded. Extracting..."
        zf = zipfile.ZipFile(gwt_fileobj)
        zf.extractall(external_location)
        del gwt_fileobj, zf
        shutil.move(os.path.join(external_location, GWT_VERSION), gwt_location)
        print >> sys.stderr, "Extracted at %s" % gwt_location
       
    # 
    # Check that smartgwt is downloaded. Download it otherwise.
    # 
    VERSION = '2.2'
    SMARTGWT_URL = "http://smartgwt.googlecode.com/files/smartgwt-%s.zip" % VERSION
    libclient_location = os.path.join(external_location,  'lib-client')
    smartgwt_location  = os.path.join(libclient_location, 'smartgwt.jar')

    if not os.path.exists(smartgwt_location):
        print >> sys.stderr, ""
        print >> sys.stderr, "WebLab-Deusto relies on a GWT library called smartgwt. In order to compile"
        print >> sys.stderr, "the client, we need to download it. If you already downloaded it, place the"
        print >> sys.stderr, ".jar of the %s version in: " % VERSION
        print >> sys.stderr, ""
        print >> sys.stderr, "     %s" % smartgwt_location
        print >> sys.stderr, ""
        print >> sys.stderr, "I will attempt to download it and place it there."
        print >> sys.stderr, ""
        print >> sys.stderr, "Downloading... (plase wait a few minutes; smartgwt is ~24 MB)"

        try:
            os.mkdir(libclient_location)
        except OSError, IOError:
            pass # Could be already created

        # TODO: this places in memory the whole file (~24 MB). urllib.urlretrieve?
        smartgwt_content = urllib2.urlopen(SMARTGWT_URL).read()
        smartgwt_fileobj = StringIO.StringIO(smartgwt_content)
        del smartgwt_content
        print >> sys.stderr, "Downloaded. Extracting..."
        zf = zipfile.ZipFile(smartgwt_fileobj)
        jar_in_zip_name = 'smartgwt-%s/smartgwt.jar' % VERSION
        zf.extract(jar_in_zip_name, libclient_location)
        del zf
        shutil.move(os.path.join(libclient_location, jar_in_zip_name.replace('/', os.sep)), smartgwt_location)
        print "Extracted to %s." % smartgwt_location

    #
    # Check that ant is installed. Download it otherwise.
    #
    try:
        subprocess.Popen(["ant","--help"], shell=False, stdout = subprocess.PIPE, stderr = subprocess.PIPE).wait()
    except:
        ant_installed = False
    else:
        ant_installed = True

    ant_location = os.path.join(external_location,  'ant')

    if not ant_installed and not os.path.exists(ant_location):
        print >> sys.stderr, ""
        print >> sys.stderr, "Ant not found. In order to compile the client, Apache Ant is required."
        print >> sys.stderr, "You can download and install Apache Ant from its official site:"
        print >> sys.stderr, ""
        print >> sys.stderr, "    http://ant.apache.org/"
        print >> sys.stderr, ""
        print >> sys.stderr, "And put it in the PATH environment variable so the 'ant' command works."
        print >> sys.stderr, "Anyway, I will download it and use the downloaded version."
        print >> sys.stderr, ""
        print >> sys.stderr, "Downloading... (please wait for a few minutes; ant is ~8 MB)"

        # 
        # Ant does not maintain all the versions in the main repository, but only the last one. First
        # we need to retrieve the latest version.
        content = urllib2.urlopen("http://www.apache.org/dist/ant/binaries/").read()
        version = content.split('-bin.zip')[0].split('ant-')[-1]

        ANT_FILENAME = 'apache-ant-%s-bin.zip' % version
        ANT_DIRNAME  = 'apache-ant-%s' % version
        ANT_URL      = "http://www.apache.org/dist/ant/binaries/%s" % ANT_FILENAME

        # TODO: this places in memory the whole file (~24 MB). urllib.urlretrieve?
        ant_content = urllib2.urlopen(ANT_URL).read()
        ant_fileobj = StringIO.StringIO(ant_content)
        del ant_content
        print >> sys.stderr, "Downloaded. Extracting..."
        zf = zipfile.ZipFile(ant_fileobj)
        zf.extractall(external_location)
        del ant_fileobj, zf
        shutil.move(os.path.join(external_location, ANT_DIRNAME), ant_location)
        print >> sys.stderr, "Extracted at %s" % ant_location

    curpath = os.path.abspath(os.getcwd())
    os.chdir(CLIENT_LOCATION)
    try:
        if ant_installed:
            ant_name = 'ant'
        else:
            ant_name = os.path.join('external','ant','bin','ant')
            # Required in UNIX, ignored in Linux
            os.chmod(ant_name, stat.S_IREAD |stat.S_IWRITE | stat.S_IEXEC | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH )
        if os.system(ant_name + ' gwtc') != 0:
            print >> sys.stderr, "ERROR: Could not compile the client!!!"
            sys.exit(-1)
    finally:
        os.chdir(curpath)

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

scripts = [ 'weblab/admin/weblab-admin' ]

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
      test_suite="launch_tests.suite",
      zip_safe=False,
     )
