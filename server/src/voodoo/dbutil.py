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

import os

def generate_getconn(engine, user, password, host, dbname):

    kwargs = {}

    if engine == 'mysql':
        # If using mysql, choose among MySQLdb or pymysql,
        # Trying to load MySQLdb, and if it fails, trying
        # to load and register pymysql
        try:
            import MySQLdb
            assert MySQLdb is not None # It can never be: just avoid pyflakes warnings
        except ImportError:
            import pymysql_sa
            pymysql_sa.make_default_mysql_dialect()

        # In the case of MySQL, we need to activate this flag
        kwargs['client_flag'] = 2
    elif engine == 'sqlite':
        # By default, sqlite uses a timeout of 5 seconds. Given the 
        # concurrency levels that WebLab-Deusto might achieve with
        # multiple users in a queue, this might not be enough. We
        # increase it to a minute and a half to avoid problems with
        # multiple concurrent users
        kwargs['timeout'] = 90 

    # Then load the sqlalchemy dialect. In order to do the 
    # equivalent to:
    # 
    #   from sqlalchemy.dialects.mysql import base 
    #   dbi = base.dialect.dbapi()
    # 
    # We import the module itself (sqlalchemy.dialects.mysql)

    import sqlalchemy.dialects as dialects
    __import__('sqlalchemy.dialects.%s' % engine)

    # And once imported, we take the base.dialect.dbapi
    dbi = getattr(dialects, engine).base.dialect.dbapi()        

    if engine == 'sqlite':
        def getconn_sqlite():
            return dbi.connect(database = get_sqlite_dbname(dbname), **kwargs)
        getconn = getconn_sqlite
    else:
        def getconn_else():
            return dbi.connect(user = user, passwd = password, host = host, db = dbname, **kwargs)
        getconn = getconn_else

    return getconn

def get_sqlite_dbname(dbname):
    upper_dir = os.sep.join(('..', 'db', '%s.db' % dbname))
    if os.path.exists(upper_dir):
        return upper_dir
    upper_upper_dir = os.sep.join(('..', upper_dir))
    if os.path.exists(upper_upper_dir):
        return upper_upper_dir
    raise Exception("Could not find %s. Did you run deploy.py?" % dbname)

def get_table_kwargs():
    return {'mysql_engine' : 'InnoDB'}

