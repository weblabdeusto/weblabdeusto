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
class Server(object):
    def __init__(self, coord_address, locator, cfg_manager, *args, **kwargs):
        super(Server, self).__init__(*args, **kwargs)
    def do_method1(self,variable):
        return "Hello"+variable
    def do_method_name_1(self,variable):
        return "Hello"+variable
    def do_method_name_2(self,variable):
        return "Hello"+variable

