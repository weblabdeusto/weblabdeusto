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

import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import weblab.configuration_doc as configuration_doc
from weblab.core.exc import DbMisconfiguredError
import voodoo.configuration as CfgErrors
from voodoo.dbutil import generate_getconn, get_sqlite_dbname

class AbstractDatabaseGateway(object):
    
    engine = None

    def __init__(self, cfg_manager):
        self.cfg_manager = cfg_manager
        try:
            host          = cfg_manager.get_doc_value(configuration_doc.DB_HOST)
            port          = cfg_manager.get_doc_value(configuration_doc.DB_PORT)
            dbname        = cfg_manager.get_doc_value(configuration_doc.DB_DATABASE)
            db_echo       = cfg_manager.get_doc_value(configuration_doc.DB_ECHO)
            engine        = cfg_manager.get_doc_value(configuration_doc.DB_ENGINE)
            user          = cfg_manager.get_doc_value(configuration_doc.WEBLAB_DB_USERNAME)
            password      = cfg_manager.get_doc_value(configuration_doc.WEBLAB_DB_PASSWORD)
        except CfgErrors.KeyNotFoundError as knfe:
            raise DbMisconfiguredError(
                    "Configuration manager didn't provide values for at least one parameter: %s" % knfe,
                    knfe
                )

        if AbstractDatabaseGateway.engine is None or cfg_manager.get_doc_value(configuration_doc.WEBLAB_DB_FORCE_ENGINE_CREATION):
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

                pool = sqlalchemy.pool.QueuePool(getconn, pool_size=15, max_overflow=20, recycle=3600)

            AbstractDatabaseGateway.engine = create_engine(connection_url, echo=db_echo, convert_unicode=True, pool = pool)

        self.Session = sessionmaker(bind=self.engine)

