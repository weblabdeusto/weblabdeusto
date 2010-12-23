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

def introspect():
    import gc
    objects = gc.get_objects()
    names = {}
    for obj in objects:
        if hasattr(obj, '__class__'):
            obj_name = obj.__class__.__name__
        else:
            obj_name = 'memory_introspector_other_objs'
        names[obj_name] = names.get(obj_name, 0) + 1
    ordered = [ (obj_name, names[obj_name], 100.0 * names[obj_name] / len(objects)) for obj_name in names ]
    ordered.sort(lambda (name1, number1, percent1), (name2, number2, percent2): cmp(number2, number1))
    open('introspection.dump','w').write(str(ordered))

if __name__ == '__main__':
    introspect()
