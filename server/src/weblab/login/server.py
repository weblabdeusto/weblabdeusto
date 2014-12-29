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

# TODO list:
# - Remove this file completely


class LoginServer(object):
    def __init__(self, coord_address, locator, cfg_manager, dont_start = False, *args, **kwargs):
        super(LoginServer,self).__init__(*args, **kwargs)

    def stop(self):
        pass
