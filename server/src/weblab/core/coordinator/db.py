#!/usr/bin/env python
#-*-*- encoding: utf-8 -*-*-
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

import sqlalchemy
from sqlalchemy.orm import sessionmaker 

COORDINATOR_DB_USERNAME   = 'core_coordinator_db_username'
COORDINATOR_DB_PASSWORD   = 'core_coordinator_db_password'
COORDINATOR_DB_HOST       = 'core_coordinator_db_host'
COORDINATOR_DB_NAME       = 'core_coordinator_db_name'
COORDINATOR_DB_ENGINE     = 'core_coordinator_db_engine'

DEFAULT_COORDINATOR_DB_HOST   = 'localhost'
DEFAULT_COORDINATOR_DB_NAME   = 'WebLabCoordination'
DEFAULT_COORDINATOR_DB_ENGINE = 'mysql' # The only one tested at the moment


def getconn():
    import MySQLdb as dbi
    return dbi.connect(user = CoordinationDatabaseManager.username, passwd = CoordinationDatabaseManager.password, 
                        host = CoordinationDatabaseManager.host, db = CoordinationDatabaseManager.dbname, client_flag = 2)

class CoordinationDatabaseManager(object):

    username = None
    password = None
    host     = None
    db       = None

    pool = sqlalchemy.pool.QueuePool(getconn, pool_size=15, max_overflow=20, recycle=3600)
    engine = None


    def __init__(self, cfg_manager):
        engine   = cfg_manager.get_value(COORDINATOR_DB_ENGINE,  DEFAULT_COORDINATOR_DB_ENGINE)
        username = CoordinationDatabaseManager.username = cfg_manager.get_value(COORDINATOR_DB_USERNAME) # REQUIRED!
        password = CoordinationDatabaseManager.password = cfg_manager.get_value(COORDINATOR_DB_PASSWORD) # REQUIRED!
        host     = CoordinationDatabaseManager.host     = cfg_manager.get_value(COORDINATOR_DB_HOST,    DEFAULT_COORDINATOR_DB_HOST)
        dbname   = CoordinationDatabaseManager.dbname   = cfg_manager.get_value(COORDINATOR_DB_NAME,    DEFAULT_COORDINATOR_DB_NAME)

        sqlalchemy_engine_str = "%s://%s:%s@%s/%s" % (engine, username, password, host, dbname)

        if CoordinationDatabaseManager.engine is None:
            CoordinationDatabaseManager.engine = sqlalchemy.create_engine(sqlalchemy_engine_str, convert_unicode=True, echo=False, pool = self.pool)

        self.session_maker = sessionmaker(bind=self.engine, autoflush = True, autocommit = False)


