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
from alembic import command

from sqlalchemy import create_engine

REGULAR_ALEMBIC_PATH    = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'regular')
SCHEDULING_ALEMBIC_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'scheduling')

class DbUpgrader(object):
    def __init__(self, regular_url, scheduling_url):
        self.regular_upgrader    = DbParticularUpgrader(regular_url, REGULAR_ALEMBIC_PATH)
        if scheduling_url is not None:
            self.scheduling_upgrader = DbParticularUpgrader(scheduling_url, SCHEDULING_ALEMBIC_PATH)
        else:
            self.scheduling_upgrader = DbNullUpgrader()

    def check_updated(self):
        return self.regular_upgrader.check() and self.scheduling_upgrader.check()

    def upgrade(self):
        self.regular_upgrader.upgrade()
        self.scheduling_upgrader.upgrade()

class DbNullUpgrader(object):

    def check(self):
        return True

    def upgrade(self):
        pass

class DbParticularUpgrader(object):
    def __init__(self, url, alembic_path):
        self.url = url
        self.config = Config(os.path.join(alembic_path, "alembic.ini"))
        self.config.set_main_option("script_location", alembic_path)
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
        if not self.check():
            command.upgrade(self.config, "head")

