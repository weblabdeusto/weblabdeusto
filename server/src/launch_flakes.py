#!/usr/bin/env python
#-*-*- encoding: utf-8 -*-*-
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

import sys
import StringIO

sys_out = sys.stdout
sys_err = sys.stderr

sys.stdout = StringIO.StringIO()
sys.stderr = StringIO.StringIO()

import launch_tests

sys.stdout = sys_out
sys.stderr = sys_err

launch_tests.check_flakes()
