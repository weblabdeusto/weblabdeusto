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
    assert len(sys.argv) == 11, "Linker example: ilink32 -Tpe -c whatever.obj c0x32, whatever.exe, , visa32 import32 cw32 bidsf \n\
Got %s arguments; \"%s\"" % ( len(sys.argv), ' '.join(sys.argv) )

    # assert sys.argv[0] == 'ilink32' #Not in the fake version
    assert sys.argv[1]  == '-Tpe'
    assert sys.argv[2]  == '-c'
    assert sys.argv[3][-4:].lower() == '.obj'
    assert sys.argv[4]  == 'c0x32,'
    assert sys.argv[5][-5:].lower() == '.exe,'
    assert sys.argv[6]  == ','
    assert sys.argv[7]  == 'visa32'
    assert sys.argv[8]  == 'import32'
    assert sys.argv[9]  == 'cw32'
    assert sys.argv[10] =='bidsf'

    received = sys.argv[3][:-4]

    if received.find("show error") >= 0:
        print("ERROR: bla bla bla")
    elif received.find("show stderr") >= 0:
        print("bla bla bla", file=sys.stderr)
    elif received.find("return -1") >= 0:
        sys.exit(-1)
