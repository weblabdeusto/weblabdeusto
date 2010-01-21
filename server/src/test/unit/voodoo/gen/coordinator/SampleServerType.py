#!/usr/bin/python
# -*- coding: utf-8 -*-
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
#Strong-typed enumeration of server types. Just a sample

values = [
    'Login',
    'Coordinator',
    'YetAnother'
]
name='SampleServerType'

import voodoo.abstraction.enumeration as enumeration
import sys

enumeration.gen(sys.modules[__name__],values,name,True)
