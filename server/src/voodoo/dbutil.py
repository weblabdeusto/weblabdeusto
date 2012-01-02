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
    from sqlalchemy.dialects.mysql import base as mysql_base
    dbi = mysql_base.dialect.dbapi()
    def getconn():
        return dbi.connect(user = user, passwd = password, host = host, db = dbname, client_flag = 2)
    return getconn

def get_table_kwargs():
    return {'mysql_engine' : 'InnoDB'}
