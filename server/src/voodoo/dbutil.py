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

def generate_getconn(engine, user, password, host, dbname):

    kwargs = {}

    if engine == 'mysql':
        # If using mysql, choose among MySQLdb or pymysql,
        # Trying to load MySQLdb, and if it fails, trying
        # to load and register pymysql
        try:
            import MySQLdb
        except ImportError:
            import pymysql_sa
            pymysql_sa.make_default_mysql_dialect()

        # In the case of MySQL, we need to activate this flag
        kwargs['client_flag'] = 2

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

    def getconn():
        return dbi.connect(user = user, passwd = password, host = host, db = dbname, **kwargs)

    return getconn

def get_table_kwargs():
    return {'mysql_engine' : 'InnoDB'}

