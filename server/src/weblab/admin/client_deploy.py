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
from __future__ import print_function, unicode_literals

import glob
import shutil
import sys
import os
import subprocess
import stat
import urllib2
import StringIO
import zipfile

def compile_client(war_location, client_location):

    GWT_VERSION_NUMBER = '2.6.1'

    external_location = os.path.join(client_location, 'external')
    gwt_location = os.path.join(external_location,'gwt')

    if 'GWT_HOME' in os.environ and os.path.exists(os.environ['GWT_HOME']):
        gwt_location = os.environ['GWT_HOME']
    else:
        gwt_location = gwt_location
    
    about_txt = os.path.join(gwt_location, 'about.txt')
    if os.path.exists(about_txt):
        first_line = open(about_txt).readlines()[0]
        if GWT_VERSION_NUMBER in first_line:
            # Correct version
            
            if len(glob.glob(war_location + "/*/*.cache.html")) > 5:
                print(file=sys.stderr)
                print("A compiled version of the WebLab-Deusto client was found, and it will ", file=sys.stderr)
                print("be used. If you have not recently compiled it and you have upgraded or", file=sys.stderr)
                print("modified anything in the client, you should compile it before doing", file=sys.stderr)
                print("this. So as to compile it, run:", file=sys.stderr)
                print("", file=sys.stderr)
                curpath = os.path.abspath('.')
                if sys.platform.find('win') == 0:
                    print("   %s> cd %s" % (curpath, client_location), file=sys.stderr)
                    print("   %s> gwtc" % client_location, file=sys.stderr)
                else:
                    print("   user@machine:%s$ cd %s" % (curpath, client_location), file=sys.stderr)
                    print("   user@machine:%s$ ./gwtc.sh" % client_location, file=sys.stderr)
                print(file=sys.stderr)
                print("And then run the setup.py again.", file=sys.stderr)
                print(file=sys.stderr)
                return

            else:
                print("", file=sys.stderr)
                print("No WebLab-Deusto compiled client found. Trying to compile it...", file=sys.stderr)
        else:
            print("", file=sys.stderr)
            print("Old GWT version found (required: %s). Trying to compile the client..." % GWT_VERSION_NUMBER, file=sys.stderr)
    else:
        print("", file=sys.stderr)
        print("No GWT version found. Trying to compile the client...", file=sys.stderr)

    try:
        subprocess.Popen(["javac", "--help"], shell=False, stdout = subprocess.PIPE, stderr = subprocess.PIPE).wait()
    except:
        print("", file=sys.stderr)
        print("Java compiler not found. Please, install the Java Development Kit (JDK).", file=sys.stderr)
        print("", file=sys.stderr)
        print("In Windows, you may need to download it from:", file=sys.stderr)
        print("", file=sys.stderr)
        print("    http://java.oracle.com/ ", file=sys.stderr)
        print("", file=sys.stderr)
        print("And install it. Once installed, you should add the jdk directory to PATH.", file=sys.stderr)
        print("This depends on the particular version of Windows, but you can follow ", file=sys.stderr)
        print("the following instructions to edit the PATH environment variable and add", file=sys.stderr)
        print("something like C:\\Program Files\\Oracle\\Java\\jdk6\\bin to PATH:", file=sys.stderr)
        print("", file=sys.stderr)
        print("    http://docs.oracle.com/javase/tutorial/essential/environment/paths.html", file=sys.stderr)
        print("", file=sys.stderr)
        print("In Linux systems, you may install openjdk from your repository and ", file=sys.stderr)
        print("will be configured.", file=sys.stderr)
        sys.exit(-1)

    # 
    # Check that GWT is downloaded. Download it otherwise.
    # 
    
    GWT_VERSION = 'gwt-%s' % GWT_VERSION_NUMBER
    GWT_URL = "http://storage.googleapis.com/gwt-releases/%s.zip" % GWT_VERSION
    external_location = os.path.join(client_location, 'external')
    gwt_location = os.path.join(external_location,'gwt')

    must_download = False

    if os.path.exists(about_txt):
        first_line = open(about_txt).readlines()[0]
        if GWT_VERSION_NUMBER not in first_line:
            must_download = True
    else:
        must_download = True

    if must_download:
        print("", file=sys.stderr)
        print("WebLab-Deusto relies on Google Web Toolkit (GWT). In order to compile ", file=sys.stderr)
        print("the client, we need to download it. If you had already downloaded it, ", file=sys.stderr)
        print("place it in: ", file=sys.stderr)
        print("", file=sys.stderr)
        print("     %s" % gwt_location, file=sys.stderr)
        print("", file=sys.stderr)
        print("or somewhere else and create an environment variable called GWT_HOME pointing", file=sys.stderr)
        print("to it. Anyway, I will attempt to download it and place it there.", file=sys.stderr)
        print("", file=sys.stderr)
        print("Downloading %s..." % GWT_URL, file=sys.stderr)
        print("(please wait a few minutes; GWT is ~100 MB)", file=sys.stderr)
        try:
            os.mkdir(external_location)
        except (OSError, IOError):
            pass # Could be already created
        try:
            shutil.rmtree(gwt_location)
        except:
            pass

        # TODO: this places in memory the whole file (~100 MB). urllib.urlretrieve?
        gwt_content = urllib2.urlopen(GWT_URL).read()
        gwt_fileobj = StringIO.StringIO(gwt_content)
        del gwt_content
        print("Downloaded. Extracting...", file=sys.stderr)
        zf = zipfile.ZipFile(gwt_fileobj)
        zf.extractall(external_location)
        del gwt_fileobj, zf

        shutil.move(os.path.join(external_location, GWT_VERSION), gwt_location)
        print("Extracted at %s" % gwt_location, file=sys.stderr)

        # These two directories are amost 200MB, so it's better to remove them
        try:
            shutil.rmtree(os.path.join(gwt_location, 'doc'))
            shutil.rmtree(os.path.join(gwt_location, 'samples'))
        except (OSError, IOError) as e:
            print("WARNING: Error trying to remove GWT doc and samples directories: %s" % e, file=sys.stderr)

    libclient_location = os.path.join(external_location,  'lib-client')

    VERSION = "3.8.2"
    JUNIT_URL = "http://downloads.sourceforge.net/project/junit/junit/3.8.2/junit3.8.2.zip"
    junit_location = os.path.join(libclient_location, 'junit.jar')
    if not os.path.exists(junit_location):
        print("", file=sys.stderr)
        print("WebLab-Deusto relies on JUnit. In order to test the client, we", file=sys.stderr)
        print("need to download it. If you already downloaded it, place the", file=sys.stderr)
        print(".jar of the %s version in: " % VERSION, file=sys.stderr)
        print("", file=sys.stderr)
        print("     %s" % junit_location, file=sys.stderr)
        print("", file=sys.stderr)
        print("I will attempt to download it and place it there.", file=sys.stderr)
        print("", file=sys.stderr)
        print("Downloading %s..." % JUNIT_URL, file=sys.stderr)
        print("(plase wait a few seconds; junit is ~400 KB)", file=sys.stderr)

        try:
            os.mkdir(libclient_location)
        except (OSError, IOError):
            pass # Could be already created

        junit_content = urllib2.urlopen(JUNIT_URL).read()
        junit_fileobj = StringIO.StringIO(junit_content)
        del junit_content
        print("Downloaded. Extracting...", file=sys.stderr)
        zf = zipfile.ZipFile(junit_fileobj)
        jar_in_zip_name = 'junit%s/junit.jar' % VERSION
        zf.extract(jar_in_zip_name, libclient_location)
        del zf
        shutil.move(os.path.join(libclient_location, jar_in_zip_name.replace('/', os.sep)), junit_location)
        print("Extracted to %s." % junit_location)
       

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
        print("", file=sys.stderr)
        print("Ant not found. In order to compile the client, Apache Ant is required.", file=sys.stderr)
        print("You can download and install Apache Ant from its official site:", file=sys.stderr)
        print("", file=sys.stderr)
        print("    http://ant.apache.org/", file=sys.stderr)
        print("", file=sys.stderr)
        print("And put it in the PATH environment variable so the 'ant' command works.", file=sys.stderr)
        print("Anyway, I will download it and use the downloaded version.", file=sys.stderr)
        print("", file=sys.stderr)
        print("Downloading... (please wait for a few minutes; ant is ~8 MB)", file=sys.stderr)

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
        print("Downloaded. Extracting...", file=sys.stderr)
        zf = zipfile.ZipFile(ant_fileobj)
        zf.extractall(external_location)
        del ant_fileobj, zf
        shutil.move(os.path.join(external_location, ANT_DIRNAME), ant_location)
        print("Extracted at %s" % ant_location, file=sys.stderr)

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
            print("ERROR: Could not compile the client!!!", file=sys.stderr)
            sys.exit(-1)
    finally:
        os.chdir(curpath)

