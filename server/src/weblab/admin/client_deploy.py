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

import glob
import sys
import os
import subprocess
import stat
import urllib2
import StringIO
import zipfile
import shutil

def compile_client(war_location, client_location):
    if len(glob.glob(war_location + "/*/*.cache.html")) > 5:
        print >> sys.stderr
        print >> sys.stderr, "A compiled version of the WebLab-Deusto client was found, and it will "
        print >> sys.stderr, "be used. If you have not recently compiled it and you have upgraded or"
        print >> sys.stderr, "modified anything in the client, you should compile it before doing"
        print >> sys.stderr, "this. So as to compile it, run:"
        print >> sys.stderr
        curpath = os.path.abspath('.')
        if sys.platform.find('win') == 0:
            print >> sys.stderr, "   %s> cd %s" % (curpath, client_location)
            print >> sys.stderr, "   %s> gwtc" % client_location
        else:
            print >> sys.stderr, "   user@machine:%s$ cd %s" % (curpath, client_location)
            print >> sys.stderr, "   user@machine:%s$ ./gwtc.sh" % client_location
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
        external_location = os.path.join(client_location, 'external')
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

        VERSION = "3.8.2"
        JUNIT_URL = "http://downloads.sourceforge.net/project/junit/junit/3.8.2/junit3.8.2.zip"
        junit_location = os.path.join(libclient_location, 'junit.jar')
        if not os.path.exists(junit_location):
            print >> sys.stderr, ""
            print >> sys.stderr, "WebLab-Deusto relies on JUnit. In order to test the client, we"
            print >> sys.stderr, "need to download it. If you already downloaded it, place the"
            print >> sys.stderr, ".jar of the %s version in: " % VERSION
            print >> sys.stderr, ""
            print >> sys.stderr, "     %s" % junit_location
            print >> sys.stderr, ""
            print >> sys.stderr, "I will attempt to download it and place it there."
            print >> sys.stderr, ""
            print >> sys.stderr, "Downloading... (plase wait a few seconds; junit is ~400 KB)"

            try:
                os.mkdir(libclient_location)
            except OSError, IOError:
                pass # Could be already created

            junit_content = urllib2.urlopen(JUNIT_URL).read()
            junit_fileobj = StringIO.StringIO(junit_content)
            del junit_content
            print >> sys.stderr, "Downloaded. Extracting..."
            zf = zipfile.ZipFile(junit_fileobj)
            jar_in_zip_name = 'junit%s/junit.jar' % VERSION
            zf.extract(jar_in_zip_name, libclient_location)
            del zf
            shutil.move(os.path.join(libclient_location, jar_in_zip_name.replace('/', os.sep)), junit_location)
            print "Extracted to %s." % junit_location
           

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
        os.chdir(client_location)
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

