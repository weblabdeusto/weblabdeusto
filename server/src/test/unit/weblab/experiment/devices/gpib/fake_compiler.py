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
from __future__ import print_function, unicode_literals

if __name__ == '__main__':
    import sys
    received = sys.argv[1]
    if received.find("show error") >= 0:
        print("ERROR: bla bla bla")
    elif received.find("show stderr") >= 0:
        print("bla bla bla", file=sys.stderr)
    elif received.find("return -1") >= 0:
        sys.exit(-1)
