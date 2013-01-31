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

#Flask configuration
DEBUG = True
SECRET_KEY = 'development key'

# DB configuration
#Connection String postgresql://DB_USERNAME:DB_PASSWORD@DB_HOST:DB_PORT/DB_NAME'


DB_NAME = 'weblab'
DB_HOST = '127.0.0.1'
DB_PORT = 5432
DB_USERNAME = 'postgres'
DB_PASSWORD = 'postgres'

