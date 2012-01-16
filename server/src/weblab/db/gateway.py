#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2005-2009 University of Deusto
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

import weblab.db.exc as DbExceptions
import voodoo.configuration as CfgExceptions

DB_HOST = 'db_host'
DEFAULT_DB_HOST = 'localhost'

DB_DATABASE = 'db_database'
DEFAULT_DB_DATABASE = 'WebLab'

DB_ENGINE = 'db_engine'
DEFAULT_DB_ENGINE = 'mysql'


class AbstractDatabaseGateway(object):
    def __init__(self, cfg_manager):

        try:
            self.host          = cfg_manager.get_value(DB_HOST, DEFAULT_DB_HOST)
            self.database_name = cfg_manager.get_value(DB_DATABASE, DEFAULT_DB_DATABASE)
            self.engine_name   = cfg_manager.get_value(DB_ENGINE, DEFAULT_DB_ENGINE)
        except CfgExceptions.KeyNotFoundException as knfe:
            raise DbExceptions.DbMisconfiguredException(
                    "Configuration manager didn't provide values for at least one parameter: %s" % knfe,
                    knfe
                )

