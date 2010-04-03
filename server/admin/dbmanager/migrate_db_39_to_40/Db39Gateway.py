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
# Author: Jaime Irurzun <jaime.irurzun@gmail.com>

import MySQLdb

import weblab.database.Model as Model


class DbGateway(object):

    def __init__(self):
        super(DbGateway, self).__init__()
        self.connection = MySQLdb.connect("localhost", "weblab", "weblab", "RealWebLab")

    def get(self, query):
        c = self.connection.cursor()
        c.execute(query)
        return c.fetchall()