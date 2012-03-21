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

from voodoo.dbutil import generate_getconn, get_sqlite_dbname

import weblab.core.coordinator.model as coord_model

import sqlalchemy
from sqlalchemy.orm import sessionmaker

from weblab.db.properties import WEBLAB_DB_FORCE_ENGINE_RECREATION, DEFAULT_WEBLAB_DB_FORCE_ENGINE_RECREATION

COORDINATOR_DB_USERNAME   = 'core_coordinator_db_username'
COORDINATOR_DB_PASSWORD   = 'core_coordinator_db_password'
COORDINATOR_DB_HOST       = 'core_coordinator_db_host'
COORDINATOR_DB_NAME       = 'core_coordinator_db_name'
COORDINATOR_DB_ENGINE     = 'core_coordinator_db_engine'

DEFAULT_COORDINATOR_DB_HOST   = 'localhost'
DEFAULT_COORDINATOR_DB_NAME   = 'WebLabCoordination'
DEFAULT_COORDINATOR_DB_ENGINE = 'mysql' # The only one tested at the moment


class CoordinationDatabaseManager(object):

    engine = None

    def __init__(self, cfg_manager):
        engine   = cfg_manager.get_value(COORDINATOR_DB_ENGINE,  DEFAULT_COORDINATOR_DB_ENGINE)
        username = CoordinationDatabaseManager.username = cfg_manager.get_value(COORDINATOR_DB_USERNAME) # REQUIRED!
        password = CoordinationDatabaseManager.password = cfg_manager.get_value(COORDINATOR_DB_PASSWORD) # REQUIRED!
        host     = CoordinationDatabaseManager.host     = cfg_manager.get_value(COORDINATOR_DB_HOST,    DEFAULT_COORDINATOR_DB_HOST)
        dbname   = CoordinationDatabaseManager.dbname   = cfg_manager.get_value(COORDINATOR_DB_NAME,    DEFAULT_COORDINATOR_DB_NAME)

        if CoordinationDatabaseManager.engine is None or cfg_manager.get_value(WEBLAB_DB_FORCE_ENGINE_RECREATION, DEFAULT_WEBLAB_DB_FORCE_ENGINE_RECREATION):
            getconn = generate_getconn(engine, username, password, host, dbname)

            connect_args = {}

            if engine == 'sqlite':
                sqlalchemy_engine_str = 'sqlite:///%s' % get_sqlite_dbname(dbname)
                if dbname == ':memory:':
                    connect_args['check_same_thread'] = False
                    pool = sqlalchemy.pool.StaticPool(getconn)
                else:
                    pool = sqlalchemy.pool.NullPool(getconn)
            else:
                sqlalchemy_engine_str = "%s://%s:%s@%s/%s" % (engine, username, password, host, dbname)

                pool = sqlalchemy.pool.QueuePool(getconn, pool_size=15, max_overflow=20, recycle=3600)

            CoordinationDatabaseManager.engine = sqlalchemy.create_engine(sqlalchemy_engine_str, convert_unicode=True, echo=False, connect_args = connect_args, pool = pool)

            if engine == 'sqlite' and dbname == ':memory:':
                coord_model.load()
                metadata = coord_model.Base.metadata
                metadata.drop_all(self.engine)
                metadata.create_all(self.engine)


        self.session_maker = sessionmaker(bind=self.engine, autoflush = True, autocommit = False)


