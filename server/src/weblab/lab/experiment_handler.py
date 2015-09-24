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
#         Jaime Irurzun <jaime.irurzun@gmail.com>
#
from __future__ import print_function, unicode_literals

class ExperimentHandler(object):
    def __init__(self, experiment_coord_address, is_up_and_running_handlers):
        super(ExperimentHandler, self).__init__()
        self._experiment_coord_address   = experiment_coord_address
        self._is_up_and_running_handlers = is_up_and_running_handlers
        self._busy                       = False
        self._lab_session_id             = None
        self.api                         = None
        self.manages_polling             = False

    def reserve(self, lab_session_id):
        if self._busy:
            return False
        self._busy = True
        self._lab_session_id = lab_session_id
        return True

    def free(self):
        if not self._busy:
            return False
        self._busy = False
        return True

    @property
    def busy(self):
        return self._busy

    @property
    def lab_session_id(self):
        return self._lab_session_id

    @property
    def experiment_coord_address(self):
        return self._experiment_coord_address

    @property
    def is_up_and_running_handlers(self):
        return self._is_up_and_running_handlers
