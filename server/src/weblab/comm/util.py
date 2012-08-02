#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2005 onwards University of Deusto
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
import glob
import subprocess

VERY_VERBOSE = False

def _deploy_stubs(folder, wsdl_file, filename):        
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

def deploy_stubs():
    try:
        import ZSI
    except ImportError:
        print >> sys.stderr, "Skipping stubs and skeletons deployment; ZSI not installed"
    else:
        _deploy_stubs(os.path.join('weblab', 'login', 'comm', 'generated'), os.path.join('..', 'LoginWebLabDeusto.wsdl'), 'loginweblabdeusto')
        _deploy_stubs(os.path.join('weblab','core','comm','generated'), os.path.join('..', 'UserProcessingWebLabDeusto.wsdl'), 'weblabdeusto')

