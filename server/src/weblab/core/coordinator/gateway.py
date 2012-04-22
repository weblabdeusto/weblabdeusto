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

from weblab.core.coordinator.confirmer import ReservationConfirmer

SQLALCHEMY = 'sqlalchemy'


def create(name, locator, cfg_manager, ConfirmerClass = ReservationConfirmer):
    if name == SQLALCHEMY:
        from weblab.core.coordinator.sql.coordinator import Coordinator as Coordinator_sql
        return Coordinator_sql(locator, cfg_manager, ConfirmerClass)
    else:
        raise Exception("Coordinator %s not found" % name)
        
