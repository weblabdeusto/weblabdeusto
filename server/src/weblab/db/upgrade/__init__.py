#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 onwards University of Deusto
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

import os

from alembic.script import ScriptDirectory
from alembic.config import Config
from alembic.migration import MigrationContext
from alembic import command

from sqlalchemy import create_engine

REGULAR_ALEMBIC_PATH    = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'regular')
SCHEDULING_ALEMBIC_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'scheduling')

DEBUG = False

class DbUpgrader(object):
    def __init__(self, regular_url, scheduling_url):
        self.regular_upgrader    = DbRegularUpgrader(regular_url)
        if scheduling_url is not None:
            self.scheduling_upgrader = DbSchedulingUpgrader(scheduling_url)
        else:
            self.scheduling_upgrader = DbNullUpgrader()

    @property
    def regular_head(self):
        return self.regular_upgrader.head

    @property
    def scheduling_head(self):
        return self.scheduling_upgrader.head

    def check_updated(self):
        return self.regular_upgrader.check() and self.scheduling_upgrader.check()

    def upgrade(self):
        self.regular_upgrader.upgrade()
        self.scheduling_upgrader.upgrade()

class DbNullUpgrader(object):

    @property
    def head(self):
        return None

    def check(self):
        return True

    def upgrade(self):
        pass

class DbParticularUpgrader(object):
    alembic_path = None

    def __init__(self, url):
        if url.startswith('mysql://'):
            try:
                import MySQLdb
                assert MySQLdb is not None # avoid warnings
            except ImportError:
                import pymysql_sa
                pymysql_sa.make_default_mysql_dialect()

        self.url = url
        self.config = Config(os.path.join(self.alembic_path, "alembic.ini"))
        self.config.set_main_option("script_location", self.alembic_path)
        self.config.set_main_option("url", self.url)
        self.config.set_main_option("sqlalchemy.url", self.url)

    @property
    def head(self):
        script = ScriptDirectory.from_config(self.config)
        return script.get_current_head()

    def check(self):
        engine = create_engine(self.url)

        context = MigrationContext.configure(engine)
        current_rev = context.get_current_revision()
        
        if DEBUG:
            print("Migrating %s" % self.url)
            print("Head: %s" % self.head)
            print("Current rev: %s" % current_rev)
            print("Correct?", current_rev == self.head)
            print()
        return self.head == current_rev

    def upgrade(self):
        if not self.check():
            command.upgrade(self.config, "head")

class DbRegularUpgrader(DbParticularUpgrader):
    alembic_path = REGULAR_ALEMBIC_PATH

class DbSchedulingUpgrader(DbParticularUpgrader):
    alembic_path = SCHEDULING_ALEMBIC_PATH

