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
# Author: Xabier Larrakoetxea <xabier.larrakoetxea@deusto.es>
# Author: Pablo Orduña <pablo.orduna@deusto.es>
#
# These authors would like to acknowledge the Spanish Ministry of science
# and innovation, for the support in the project IPT-2011-1558-430000
# "mCloud: http://innovacion.grupogesfor.com/web/mcloud"
#

import subprocess
import os

from weblabDeployer import deploymentsettings

print("Deploying weblab instances:")
with open(os.path.join(deploymentsettings.DIR_BASE,
    'instances.txt'), 'a+') as f:
    
    for line in f:
        # Start now the new weblab instance
        line = line.replace('\n', '').strip()
        print("Deploying task: %s..." % line)
        process = subprocess.Popen(['nohup','weblab-admin','start', line])
        print("Finished deploying")