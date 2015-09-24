#!/usr/bin/env python
#-*-*- encoding: utf-8 -*-*-
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

from voodoo.dbutil import generate_getconn, get_sqlite_dbname

import weblab.core.coordinator.sql.model as coord_model

import sqlalchemy
from sqlalchemy.orm import sessionmaker

import weblab.configuration_doc as configuration_doc

DEFAULT_COORDINATOR_DB_HOST   = 'localhost'
DEFAULT_COORDINATOR_DB_NAME   = 'WebLabCoordination'
DEFAULT_COORDINATOR_DB_ENGINE = 'mysql' # The only one tested at the moment


class CoordinationDatabaseManager(object):

    engine = None

    def __init__(self, cfg_manager):
        engine   = cfg_manager.get_doc_value(configuration_doc.COORDINATOR_DB_ENGINE)
        username = CoordinationDatabaseManager.username = cfg_manager.get_doc_value(configuration_doc.COORDINATOR_DB_USERNAME)
        password = CoordinationDatabaseManager.password = cfg_manager.get_doc_value(configuration_doc.COORDINATOR_DB_PASSWORD)
        host     = CoordinationDatabaseManager.host     = cfg_manager.get_doc_value(configuration_doc.COORDINATOR_DB_HOST)
        port     = CoordinationDatabaseManager.port     = cfg_manager.get_doc_value(configuration_doc.COORDINATOR_DB_PORT)
        dbname   = CoordinationDatabaseManager.dbname   = cfg_manager.get_doc_value(configuration_doc.COORDINATOR_DB_NAME)

        if CoordinationDatabaseManager.engine is None or cfg_manager.get_doc_value(configuration_doc.DB_FORCE_ENGINE_CREATION):
            getconn = generate_getconn(engine, username, password, host, port, dbname)

            connect_args = {}

            if engine == 'sqlite':
                sqlalchemy_engine_str = 'sqlite:///%s' % get_sqlite_dbname(dbname)
                if dbname == ':memory:':
                    connect_args['check_same_thread'] = False
                    pool = sqlalchemy.pool.StaticPool(getconn)
                else:
                    pool = sqlalchemy.pool.NullPool(getconn)
            else:
                if port is None:
                    port_str = ''
                else:
                    port_str = ':%s' % port
                sqlalchemy_engine_str = "%s://%s:%s@%s%s/%s" % (engine, username, password, host, port_str, dbname)

                pool = sqlalchemy.pool.QueuePool(getconn, pool_size=15, max_overflow=20, recycle=3600)

            CoordinationDatabaseManager.engine = sqlalchemy.create_engine(sqlalchemy_engine_str, convert_unicode=True, echo=False, connect_args = connect_args, pool = pool)

            if engine == 'sqlite' and dbname == ':memory:':
                coord_model.load()
                metadata = coord_model.Base.metadata
                metadata.drop_all(self.engine)
                metadata.create_all(self.engine)


        self.session_maker = sessionmaker(bind=self.engine, autoflush = True, autocommit = False)


