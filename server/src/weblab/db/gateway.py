#!/usr/bin/python
# -*- coding: utf-8 -*-
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

import weblab.configuration_doc as configuration_doc
import weblab.db.exc as DbErrors
import voodoo.configuration as CfgErrors

class AbstractDatabaseGateway(object):
    def __init__(self, cfg_manager):
        self.cfg_manager = cfg_manager
        try:
            self.host          = cfg_manager.get_doc_value(configuration_doc.DB_HOST)
            self.database_name = cfg_manager.get_doc_value(configuration_doc.DB_DATABASE)
            self.engine_name   = cfg_manager.get_doc_value(configuration_doc.DB_ENGINE)
        except CfgErrors.KeyNotFoundError as knfe:
            raise DbErrors.DbMisconfiguredError(
                    "Configuration manager didn't provide values for at least one parameter: %s" % knfe,
                    knfe
                )

