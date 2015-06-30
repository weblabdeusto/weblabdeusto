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
# 
from __future__ import print_function, unicode_literals

import sys
import os
import gzip
import requests
import argparse

from voodoo.configuration import ConfigurationManager
from weblab.core.db import DatabaseGateway
from weblab.admin.script.utils import run_with_config

def weblab_locations(directory):
    def on_dir(directory, configuration_files, configuration_values):
        parser = argparse.ArgumentParser(usage='%(prog)s locations DIR [options]')
        parser.add_argument('--redownload', action='store_true', help='Force redownload of databases')
        parser.add_argument('--reset-database', action='store_true', help='Reset the database, forcing the server to download all the data again')
        parser.add_argument('--reset-cache', action='store_true', help='Reset the database, forcing the server to download all the data again')
        args = parser.parse_args(sys.argv[3:])

        config = ConfigurationManager.create(directory, configuration_files, configuration_values)

        for filename in 'GeoLite2-Country.mmdb', 'GeoLite2-City.mmdb':
            if os.path.exists(filename):
                print("Found %s" % filename)
                if args.redownload:
                    print("Redownloading...")
            else:
                print("%s not found. Downloading..." % filename)

            if args.redownload or not os.path.exists(filename):
                r = requests.get("http://geolite.maxmind.com/download/geoip/database/%s.gz" % filename)
                open('%s.gz' % filename,'w').write(r.content)
                uncompressed = gzip.open('%s.gz' % filename).read()
                open(filename, 'w').write(uncompressed)
                print("Downloaded")

        db = DatabaseGateway(config)

        if args.reset_database:
            print("Resetting database")
            db.reset_locations_database()

        if args.reset_cache:
            print("Resetting cache")
            db.reset_locations_cache()

    run_with_config(directory, on_dir)

