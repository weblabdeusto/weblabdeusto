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
from __future__ import print_function, unicode_literals

"""
Database model. There are two ways to access it:

from weblab.db import db

session = db.Session()
# whatever

It must be previously initialized:

from weblab.db import db
db.initialize(cfg_manager)
"""

import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import weblab.configuration_doc as configuration_doc
from weblab.core.exc import DbMisconfiguredError
import voodoo.configuration as CfgErrors
from voodoo.dbutil import generate_getconn, get_sqlite_dbname

class DatabaseConnection(object):
    def __init__(self):
        self.engine = None

    def initialize(self, cfg_manager):
        try:
            host          = cfg_manager.get_doc_value(configuration_doc.DB_HOST)
            port          = cfg_manager.get_doc_value(configuration_doc.DB_PORT)
            dbname        = cfg_manager.get_doc_value(configuration_doc.DB_DATABASE)
            engine        = cfg_manager.get_doc_value(configuration_doc.DB_ENGINE)
            pool_size     = cfg_manager.get_doc_value(configuration_doc.DB_POOL_SIZE)
            max_overflow  = cfg_manager.get_doc_value(configuration_doc.DB_MAX_OVERFLOW)
            user          = cfg_manager.get_doc_value(configuration_doc.DB_USERNAME)
            password      = cfg_manager.get_doc_value(configuration_doc.DB_PASSWORD)
        except CfgErrors.KeyNotFoundError as knfe:
            raise DbMisconfiguredError(
                    "Configuration manager didn't provide values for at least one parameter: %s" % knfe,
                    knfe
                )

        if self.engine is None or cfg_manager.get_doc_value(configuration_doc.DB_FORCE_ENGINE_CREATION):
            getconn = generate_getconn(engine, user, password, host, port, dbname)

            if engine == 'sqlite':
                connection_url = 'sqlite:///%s' % get_sqlite_dbname(dbname)
                pool = sqlalchemy.pool.NullPool(getconn)
            else:
                if port is None:
                    port_str = ''
                else:
                    port_str = ':%s' % port
                connection_url = "%(ENGINE)s://%(USER)s:%(PASSWORD)s@%(HOST)s%(PORT)s/%(DATABASE)s" % \
                                { "ENGINE":   engine, 'PORT' : port_str,
                                  "USER":     user, "PASSWORD": password,
                                  "HOST":     host, "DATABASE": dbname  }

                pool = sqlalchemy.pool.QueuePool(getconn, pool_size=pool_size, max_overflow=max_overflow, recycle=3600)

            self.engine = create_engine(connection_url, echo=False, convert_unicode=True, pool = pool)

        self.Session = sessionmaker(bind=self.engine)
        return self.Session, self.engine

db = DatabaseConnection()
