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
# Author: Jaime Irurzun <jaime.irurzun@gmail.com>
# 

if __name__ == '__main__':
    import sys
    if sys.argv[2].find("show error") >= 0:
        print "ERROR: bla bla bla"
    elif sys.argv[2].find("show stderr") >= 0:
        print >> sys.stderr, "bla bla bla"
    elif sys.argv[2].find("return -1") >= 0:
        sys.exit(-1)