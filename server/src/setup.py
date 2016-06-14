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
import json
import time
import shlex
import shutil
import subprocess
from setuptools import setup, find_packages
from setuptools.command.build_py import build_py as _build_py


def _build_requirements():
    generate_version()

    ##########################################################
    #
    # 
    #       C L I E N T 
    # 
    # 

    CLIENT_LOCATION = os.path.abspath(os.path.join('..','..','client'))
    WAR_LOCATION = os.path.join(CLIENT_LOCATION,'war')

    # In any case, the client was compiled in the past or just now. Let's copy it here.
    print "Copying...",
    shutil.rmtree(os.path.join('weblabdeusto_data', 'war'), True)
    shutil.copytree(WAR_LOCATION, os.path.join('weblabdeusto_data', 'war'))
    shutil.rmtree(os.path.join('weblabdeusto_data', 'war', 'WEB-INF'), True)
    print "[done]"

class WebLabBuild(_build_py):
    def run(self):
        if not self.dry_run:
            if os.path.exists('build'):
                shutil.rmtree('build')
            # If the  WEBLAB_OPT_NOCLIENT option is specified then we will skip the client compilation.
            if os.environ.get("WEBLAB_OPT_NOCLIENT") is None:
                _build_requirements()
                lib_war = os.path.join(self.build_lib, 'weblabdeusto_data', 'war')
                if os.path.exists(lib_war):
                    shutil.rmtree(lib_war)
                shutil.copytree(os.path.join('weblabdeusto_data', 'war'), lib_war)
            else:
                print "Skipping client compilation."

        _build_py.run(self)


##########################################################
#
# 
#       P A C K A G E S    A N D     F I L E S
# 
# 

if not os.path.exists('weblabdeusto_data'):
    os.mkdir('weblabdeusto_data')

data_files   = []

for dirpath, dirnames, filenames in os.walk('weblabdeusto_data'):
    # Ignore dirnames that start with '.'   
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): 
            del dirnames[i]
    
    # In the war directory, don't take into account whatever we have now, but whatever has been
    # compiled and will be copied. Otherwise, there will be problems when a compilation has been
    # made.
    if dirpath.startswith(os.path.join('weblabdeusto_data','war')):
        newdir = dirpath.replace(os.path.join('weblabdeusto_data','war'), os.path.join('..','..','client','war'))
        if os.path.exists(newdir):
            filenames = [ f for f in os.listdir(newdir) if os.path.isfile(os.path.join(newdir, f)) ]
            data_files.append([dirpath, [os.path.join(dirpath, f) for f in filenames ]])
    else:
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

def generate_version():
    try:
        subprocess.check_output(shlex.split('git --help'))
    except:
        try:
            subprocess.check_output(shlex.split('git.cmd --help'))
        except:
            print >> sys.stderr, "git command could not be run! Check your PATH"
            git_command = None
        else:
            git_command = 'git.cmd'
    else:
        git_command = 'git'

    json_contents = {}

    if git_command is not None:
        try:
            output = subprocess.check_output([git_command,'--no-pager','show'])
            version = output.split('\n')[0].split()[1].strip()

            cmd = shlex.split('%s --no-pager log %s --format="%%at"' % (git_command, version))
            output = subprocess.check_output(cmd)
            lines = [ line for line in output.split('\n') ]
            timestamp = int(lines[0].strip().replace('"','').replace("'",''))
            date_str = time.strftime('%A, %B %d, %Y', time.localtime(timestamp))
            number_of_versions = len(lines)
            json_contents = {
                'version' : version,
                'version_number' : number_of_versions,
                'date' : date_str,
            }
        except:
            pass
    
    open('weblab/version.json','w').write(json.dumps(json_contents, indent = 4))

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

scripts = []

entry_points={'console_scripts': [
    'weblab-admin = weblab.admin.script:weblab',
    'weblab-admin.py = weblab.admin.script:weblab',
    'weblab-bot = weblab.admin.bot.bot:main',
    'weblab-bot.py = weblab.admin.bot.bot:main',
]}

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
      cmdclass = { 'build_py' : WebLabBuild },
      author='WebLab-Deusto Team',
      author_email='weblab@deusto.es',
      url='http://code.google.com/p/weblabdeusto/',
      packages=find_packages(exclude=['test.*','test']),
      include_package_data=True,
      data_files=data_files,
      license=cp_license,
      scripts=scripts,
      entry_points=entry_points,
      install_requires=install_requires,
      tests_require=tests_require,
      test_suite="develop.suite",
      zip_safe=False,
     )
