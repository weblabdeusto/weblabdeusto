#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2005-2009 University of Deusto
# All rights reserved.
#
# This software is licensed as described in the cmd_params COPYING, which
# you should have received as part of this distribution.
#
# This software consists of contributions made by many individuals, 
# listed below:
#
# Author: Jaime Irurzun <jaime.irurzun@gmail.com>
# 

if __name__ == '__main__':
    import sys
    for param in sys.argv:
        if param.find("error") >= 0:
            print "ERROR: bla bla bla"
            break
        elif param.find("return-1") >= 0:
            sys.exit(-1)