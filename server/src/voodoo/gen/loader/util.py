#!/usr/bin/env python
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

import traceback
import xml.dom.minidom as minidom
import voodoo.gen.exceptions.loader.LoaderErrors as LoaderErrors

def find_nodes(file_name, root_node, node_name):
    return [ child_node
        for child_node in root_node.childNodes
        if isinstance(child_node, minidom.Element) and child_node.tagName == node_name
    ]

def find_nodes_at_least_one(file_name, root_node, node_name):
    nodes = find_nodes(file_name, root_node, node_name)
    if len(nodes) == 0:
        raise LoaderErrors.InvalidSyntaxFileConfigurationError(
            "Couldn't find %s node in %s" % (file_name, node_name),
            file_name
        )
    return nodes

def find_node(file_name, root_node, node_name):
    nodes = find_nodes_at_least_one(file_name, root_node, node_name)
    if len(nodes) > 1:
        raise LoaderErrors.InvalidSyntaxFileConfigurationError(
            "Too many %s nodes in %s" % (file_name, node_name),
            file_name
        )
    return nodes[0]

# XXX DEPRECATED FOR obtain_text_safe!!!
def obtain_text(text_node):
    text = [ i for i in text_node.childNodes if isinstance(i,minidom.Text) ]
    if len(text) == 0:
        return None
    else:
        return text[0].nodeValue

def obtain_text_safe(text_node):
    text = [ i for i in text_node.childNodes if isinstance(i,minidom.Text) ]
    if len(text) == 0:
        raise LoaderErrors.InvalidConfigurationError(
                    "Empty Text Node"
                )
    else:
        return text[0].nodeValue

def last_point(name):
    """ last_point(name) -> str
    Given a str like "os.path.sep" in str form, this function will return a str like "os.path"
    """
    return '.'.join(name.split('.')[:-1])

def obtain_module(name):
    """ obtain_module(name) -> module
    Given a name like "os.path.sep" in str form, this function will return the module os.path (or os, if __import__ provides os)
    or None if no module is found.
    """
    the_module = None
    while len(name) > 0 and the_module == None:
        name = last_point(name)
        try:
            if len(name) > 0:
                the_module = __import__(name,globals(),locals())
        except ImportError:
            pass
    return the_module

def obtain_from_python_path(name):
    """ obtain_from_python_path(name) -> whatever :-)

    Given a full str name like 'os.path.sep', this function returns whatever
    it is in that path (for example, os.path.sep is a str, so this function
    will return "the value of that variable").
    """
    the_module = obtain_module(name)
    #If the_module is still None, the path is wrong
    if the_module == None:
        raise LoaderErrors.InvalidConfigurationError(
                    """I can't import any module from "%s" """ % name
                )

    sequence_name_without = name[len(str(the_module).split("'")[1]) + 1:]
    current_block = the_module
    last_exc = "(No exception raised)"
    for i in sequence_name_without.split('.'):
        module_name = current_block.__name__ + '.' + i

        try:
            __import__(module_name, globals(), locals())
        except ImportError:
            # foo.bar.MyClass will fail, but foo.bar will work
            last_exc = traceback.format_exc()

        try:
            current_block = getattr(current_block,i)
        except AttributeError:
            raise LoaderErrors.InvalidConfigurationError( """Couldn't find %s in module: %s. Last error: %s""" % (i, name, last_exc))

    return current_block

