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
from __future__ import print_function, unicode_literals

import re

##########################################################
#
#            R A T I O N A L E
#
# There is a set of issues with external libraries
# that have an impact in the project. Some of these
# might be considered bugs, other just version issues.
#
# Since we can fix all these issues dynamically, we
# do it. This is easier to manage than changing the
# code of the libraries.
#

patches = []

def patch(func):
    patches.append(func)

def apply():
    for patch in patches:
        patch()

@patch
def add_braces_to_openid_regex():
    try:
        import openid.urinorm as urinorm
    except ImportError:
        return

    if hasattr(urinorm, 'uri_illegal_char_re'):
        if urinorm.uri_illegal_char_re.search("{"):
            # Invalid regexp for RedIRIS. Try to avoid it.
            urinorm.uri_illegal_char_re = re.compile(urinorm.uri_illegal_char_re.pattern.replace('A-Z', 'A-Z{}'))

