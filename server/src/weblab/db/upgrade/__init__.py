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

import os

from alembic.script import ScriptDirectory
from alembic.config import Config
from alembic.migration import MigrationContext
from alembic.environment import EnvironmentContext
from alembic import command

from sqlalchemy import create_engine

ALEMBIC_PATH = os.path.abspath(os.path.dirname(__file__))

class DbUpgrader(object):
    def __init__(self, url):
        self.url = url
        self.config = Config(os.path.join(ALEMBIC_PATH, "alembic.ini"))
        self.config.set_main_option("script_location", ALEMBIC_PATH)
        self.config.set_main_option("url", self.url)
        self.config.set_main_option("sqlalchemy.url", self.url)

    def check(self):
        engine = create_engine(self.url)

        script = ScriptDirectory.from_config(self.config)
        current_head = script.get_current_head()

        context = MigrationContext.configure(engine)
        current_rev = context.get_current_revision()

        return current_head == current_rev

    def upgrade(self):
        command.upgrade(self.config, "head")

if __name__ == '__main__':
    import sqlite3
    sqlite3.connect('foo.db').close()
    dbu = DbUpgrader("sqlite:///foo.db")
    print dbu.check()
    print dbu.upgrade()
