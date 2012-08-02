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
#         Jaime Irurzun <jaime.irurzun@gmail.com>
# 

import sys, os
sys.path.append( os.sep.join(('..','src')) )

import stat
import glob
import subprocess
import shutil
import math
import datetime

# Utility functions

VERBOSE = True
VERY_VERBOSE = VERBOSE & True

def show_msg(msg):
    print >> sys.stdout, "INFO: %s" % msg

def show_warning(msg):
    print >> sys.stderr, "WARN: %s" % msg

def show_error(msg):
    print >> sys.stderr, "ERR:  %s" % msg

class ErrorHandler(object):
    def __init__(self, func_name):
        super(ErrorHandler,self).__init__()
        self.func_name = func_name
        self.error_message = []
        self.warning_message = []
        self.messages = []

    def write_msg(self,msg):
        self.messages.append(msg)
    def write_error(self, msg):
        self.error_message.append(msg)
    def write_warning(self, msg):
        self.warning_message.append(msg)

    def get_messages(self):
        return self.messages
    def get_errors(self):
        return self.error_message
    def get_warnings(self):
        return self.warning_message

class Deployer(object):
    def __init__(self, func, activate, order):
        super(Deployer,self).__init__()
        self.func     = func
        self.name     = func.__name__
        self.activate = activate
        self.order    = order
        
    def __call__(self, *args, **kargs):
        if self.activate:
            if VERBOSE:
                show_msg("%s: started" % self.name)
            error_handler = ErrorHandler(self.name)
            failed = self.func(error_handler,*args,**kargs)
            if VERBOSE:
                if error_handler.get_messages() != ['stdout::']:
                    for i in error_handler.get_messages():
                        show_msg("%s: info: %s"  % (self.name, i))

                if error_handler.get_warnings() != ['stderr::']:
                    for i in error_handler.get_warnings():
                        show_warning("%s: warn: %s"  % (self.name, i))

                if failed:
                    for i in error_handler.get_errors():
                        show_error("%s: erro: %s"  % (self.name, i) )
                    show_error("%s: failed!" % self.name)
                else:
                    show_msg("%s: successfully finished" % self.name)
            return failed
        else:
            if VERBOSE:
                show_warning("%s: skipping" % self.name)
            return False #Not failed

def deployer(order, activate = True):
    def wrapped(func):
        d = Deployer(func, activate, order)
        d.__name__ = func.__name__
        d.__doc__ = func.__doc__
        return d
    return wrapped

# Deployment functions

#@deployer(20)
def create_databases(error_handler):
    cwd = os.getcwd()
    os.chdir('../deploy')
    pr = subprocess.Popen(sys.executable + " create_databases.py", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    result = pr.wait()
    if result != 0:
        for i in pr.stdout.read().split('\n'):
            error_handler.write_msg('stdout::%s' % i)
        for i in pr.stderr.read().split('\n'):
            error_handler.write_error('stderr::%s' % i)
        error_handler.write_error("database script failed")
        result = True
    else:
        if VERY_VERBOSE:
            for i in pr.stdout.read().split('\n'):
                error_handler.write_msg('stdout::%s' % i)
            for i in pr.stderr.read().split('\n'):
                error_handler.write_warning('stderr::%s' % i)
        result = False
    os.chdir(cwd)
    return result

@deployer(40)
def build_webserver(error_handler):
    webservers_libs = 'webserver' + os.sep + 'libs'
    if os.path.exists(webservers_libs):
        shutil.rmtree(webservers_libs)
    os.mkdir(webservers_libs)
    
    version = '.'.join((str(i) for i in sys.version_info[0:2]))
    bits    = int(math.log(sys.maxint + 1, 2) + 1) # TODO: is there any other way to find this out?

    native_libs = '..' + os.sep + 'lib' + os.sep + sys.platform + os.sep + version
    native_bits_libs = native_libs + os.sep + str(bits)

    def setpermissions(arg, dirname, fnames):
        for fname in fnames:
            filename = os.path.join(dirname, fname)
            os.chmod(filename, stat.S_IREAD |stat.S_IWRITE | stat.S_IEXEC | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH )

    os.path.walk(webservers_libs, setpermissions, None)

def check_all():
    failed_functions = []
    def try_function(func):
        if func():
            failed_functions.append(func.__name__)

    deployers = [ i for i in globals().values() if isinstance(i, Deployer) ]
    deployers.sort(lambda x,y: cmp(x.order,y.order))
    for i in deployers:
        try_function(i)

    return len(failed_functions) != 0, failed_functions

if __name__ == '__main__':
    os.chdir("../src")
    failed, failed_functions = check_all()
    if failed:
        for i in failed_functions:
            print "Failed: %s" % i
        sys.exit(-1)
    else:
        print "DEPLOYMENT SUCCEEDED"
