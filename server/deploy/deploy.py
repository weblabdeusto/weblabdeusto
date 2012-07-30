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

@deployer(10)
def check_installed_python_modules(error_handler):
    """
    Check for installed Python modules first:

        * python-mysqldb or (python-pymysql with pymysql_sa)
        * python-sqlalchemy
        * python-simplejson [not required in Python >= 2.6]
        * python-soappy  [optional]
        * python-zsi     [optional]
        * python-ldap    [optional]
        * python-lxml    [optional]
        * python-serial  [optional]
        * mocker         [optional]
    """
    REQUIRED_MODULES = ['sqlalchemy'] # + (MySQLdb or (pymysql + pymysql_sa))
    OPTIONAL_MODULES = ('ZSI','SOAPpy','lxml','mocker','serial','ldap')

    not_installed_modules = []

    def try_module(module_name, level):
        try:
            __import__(module_name)
        except ImportError:
            not_installed_modules.append((module_name, level))
    
    Required = 'Required'
    Optional = 'Optional'

    try_module('MySQLdb', Required)
    if not_installed_modules:
        not_installed_modules = []
        try_module('pymysql', Required)
        try_module('pymysql_sa', Required)
        if not_installed_modules: # Add it again so as to document it
            try_module('MySQLdb', Required)
            

    for i in REQUIRED_MODULES:
        try_module(i, Required)
    for i in OPTIONAL_MODULES:
        try_module(i, Optional)
    
    failed = False
    for i in not_installed_modules:
        if i[1] == Required:
            failed = True
            error_handler.write_error("Required module %s not installed" % i[0])
        else:
            error_handler.write_warning("Optional module %s not installed" % i[0])

    return failed

def _wait_process(pr, error_handler):
    result = pr.wait()
    if result != 0:
        for i in pr.stdout.read().split('\n'):
            error_handler.write_msg('stdout::%s' % i)
        for i in pr.stderr.read().split('\n'):
            error_handler.write_error('stderr::%s' % i)
        error_handler.write_error("database script failed")
        return True
    if VERY_VERBOSE:
        for i in pr.stdout.read().split('\n'):
            error_handler.write_msg('stdout::%s' % i)
        for i in pr.stderr.read().split('\n'):
            error_handler.write_warning('stderr::%s' % i)
    return False


@deployer(20)
def create_databases(error_handler):
    cwd = os.getcwd()
    os.chdir('../deploy')
    pr = subprocess.Popen(sys.executable + " create_databases.py", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    result = _wait_process(pr, error_handler)
    os.chdir(cwd)
    return result


def _deploy_stubs(error_handler, folder, wsdl_file, filename):
    try:
        import ZSI
    except ImportError:
        error_handler.write_error("Skipping stubs and skeletons deployment; ZSI not installed")
        return False
        
    bin_path      = os.path.abspath('../lib/common/bin/')
    cur_dir_full  = os.path.abspath(os.path.curdir)
    if bin_path.find(cur_dir_full) == 0:
        bin_path = '.' + bin_path[len(cur_dir_full):]
    wsdl2py       = '"%s"' % os.sep.join((bin_path,'wsdl2py.py'))
    wsdl2dispatch = '"%s"' % os.sep.join((bin_path,'wsdl2dispatch.py'))

    for i in glob.glob("%s/%s_*.py" % (folder, filename)):
        os.remove(i)
    cwd = os.getcwd()
    os.chdir(folder)

    pr = subprocess.Popen(sys.executable + " " + wsdl2py + " -e -f ../%s --simple-naming" % wsdl_file, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    result = pr.wait()
    if result != 0:
        for i in pr.stdout.read().split('\n'):
            if i.strip() != '':
                error_handler.write_msg('stdout::%s' % i)
        for i in pr.stderr.read().split('\n'):
            if i.strip() != '':
                error_handler.write_error('stderr::%s' % i)
        error_handler.write_error("wsdl2py script failed")
        os.chdir(cwd)
        return True
    if VERY_VERBOSE:
        for i in pr.stdout.read().split('\n'):
            if i.strip() != '':
                error_handler.write_msg('stdout::%s' % i)
        for i in pr.stderr.read().split('\n'):
            if i.strip() != '' and i.find("DeprecationWarning: the multifile module has been deprecated") < 0 and i.find("import multifile, mimetools") < 0:
                error_handler.write_warning('stderr::%s' % i)

    # Little bug in the stubs generation :-)
    client_file = open('%s_client.py' % filename,'a')
    client_file.write('\n\nfrom %s_messages import *\n\n' % filename)
    client_file.close()

    # By default, ZSI strips the strings in the SOAP request. We don't want this, so we change this behaviour
    services_types_content = open('%s_services_types.py' % filename).read()
    services_types_content = services_types_content.replace("ZSI.TC.String(","ZSI.TC.String(strip=False,")
    open('%s_services_types.py' % filename,'w').write(services_types_content)

    pr = subprocess.Popen(sys.executable + " " + wsdl2dispatch + " -e -f ../%s --simple-naming" % wsdl_file, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    result = pr.wait()
    os.chdir(cwd)
    if result != 0:
        for i in pr.stdout.read().split('\n'):
            if i.strip() != '':
                error_handler.write_msg('stdout::%s' % i)
        for i in pr.stderr.read().split('\n'):
            if i.strip() != '':
                error_handler.write_error('stderr::%s' % i)
        error_handler.write_error("wsdl2dispatch script failed")
        return True
    if VERY_VERBOSE:
        for i in pr.stdout.read().split('\n'):
            if i.strip() != '':
                error_handler.write_msg('stdout::%s' % i)
        for i in pr.stderr.read().split('\n'):
            if i.strip() != '' and i.find("DeprecationWarning: the multifile module has been deprecated") < 0 and i.find("import multifile, mimetools") < 0:
                error_handler.write_warning('stderr::%s' % i)
    
    return False

@deployer(30)
def deploy_login_stubs(error_handler):
    return _deploy_stubs(error_handler, 'weblab/login/comm/generated/', 'LoginWebLabDeusto.wsdl', 'loginweblabdeusto')

@deployer(30)
def deploy_core_stubs(error_handler):
    return _deploy_stubs(error_handler, 'weblab/core/comm/generated/', 'UserProcessingWebLabDeusto.wsdl', 'weblabdeusto')

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
