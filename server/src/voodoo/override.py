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

def Override(classes):
    """ Override(classes) -> decorator

    Decorator which emulates the same behaviour as the
    Overrides annotation in Java >= 1.5
    """
    def wrapped(func):
        try:
            real_classes = tuple(( i for i in classes ))
        except TypeError:
            real_classes = ( classes, )

        found = False
        for i in real_classes:
            if hasattr(i, func.__name__):
                found = True
                break
        if not found:
            raise TypeError("Method %s is not present in classes: %s" % (func.__name__, real_classes))
        else:
            return func
    return wrapped

