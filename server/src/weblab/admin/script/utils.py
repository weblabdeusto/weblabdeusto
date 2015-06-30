#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2012 onwards University of Deusto
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#
# This software consists of contributions made by many individuals,
# listed below:
#
# Author: Pablo Orduña <pablo@ordunya.com>
#         Luis Rodriguez <luis.rodriguez@opendeusto.es>
#
from __future__ import print_function, unicode_literals

from __future__ import print_function

import os
import sys
from collections import OrderedDict

import yaml

from voodoo.gen.legacy import LegacyParser
from voodoo.gen import load_dir

def ordered_dump(data, stream=None, Dumper=yaml.Dumper, **kwds):
    class OrderedDumper(yaml.Dumper):
        pass
    def _dict_representer(dumper, data):
        return dumper.represent_mapping(
            yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
            data.items())
    OrderedDumper.add_representer(OrderedDict, _dict_representer)
    OrderedDumper.add_representer(unicode, lambda dumper, value: dumper.represent_scalar(u'tag:yaml.org,2002:str', value))
    return yaml.dump(data, stream, OrderedDumper, **kwds)

def check_dir_exists(directory, parser = None):
    if not os.path.exists(directory):
        if parser is not None:
            parser.error("ERROR: Directory %s does not exist" % directory)
        else:
            print("ERROR: Directory %s does not exist" % directory, file=sys.stderr)
        sys.exit(-1)
    if not os.path.isdir(directory):
        if parser is not None:
            parser.error("ERROR: File %s exists, but it is not a directory" % directory)
        else:
            print("ERROR: Directory %s does not exist" % directory, file=sys.stderr)
        sys.exit(-1)


def run_with_config(directory, func):
    check_dir_exists(directory)
    old_cwd = os.getcwd()
    os.chdir(directory)
    try:
        if os.path.exists(os.path.join('.', 'configuration.yml')):
            global_config = load_dir('.')
            configuration_files, configuration_values = global_config.get_all_config()
        elif os.path.exists(os.path.join('.', 'configuration.xml')):
            print("Loading old-style configuration...", file=sys.stderr)
            parser = LegacyParser()
            configuration_files = parser.get_config_files('.')
            configuration_values = []
        else:
            print("ERROR: not a valid configuration directory. Missing configuration.yml (or configuration.xml)", file=sys.stderr)
            sys.exit(-1)
        return func('.', configuration_files, configuration_values)
    finally:
        os.chdir(old_cwd)

