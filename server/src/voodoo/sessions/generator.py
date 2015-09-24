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
import random

class SessionGenerator(object):
    def __init__(self):
        object.__init__(self)

        self.alphabet = [ str(i) for i in range(10) ]
        self.alphabet += [ chr(i + ord('a')) for i in range(26) ]
        self.alphabet += [ chr(i + ord('A')) for i in range(26) ]
        # It can't be:
        # ".": problems with apache checking the session affinity. "foo.bar.route1" is interpreted as "bar.route1"
        # ",": problems with cookies (considered a different cookie)
        # "+": problems with GWT (considering "foo+bar" as "foo bar")
        self.alphabet += '_-' # So as to get an alphabet of 64 (6 bits)

    def generate_id(self, number_of_chars = 16):
        # Generates IDs of 16 chars of an alphabet of 64 possible chars
        # ( 115792089237316195423570985008687907853269984665640564039457584007913129639936 possibilities )
        bits = random.getrandbits(6 * number_of_chars)
        id = ''
        for _ in xrange(number_of_chars):
            id += self.alphabet[ bits % 64 ]
            bits /= 64
        return id
