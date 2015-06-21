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

import os
import time
import socket
import threading
import traceback

from geoip2.errors import GeoIP2Error
from geoip2.database import Reader as GeoIP2Reader

from voodoo.resources_manager import is_testing
import weblab.configuration_doc as configuration_doc

class AddressLocator(object):
    def __init__(self, config):
        self.config = config

    def locate(self, ip_address):
        if ip_address.startswith("<unknown client. retrieved from ") and ip_address.endswith(">"):
            ip_address = ip_address[len("<unknown client. retrieved from "):-1]

        if ip_address == '<address not found>':
            return {
                'hostname' : ip_address,
                'city': None,
                'country': None,
                'most_specific_subdivision' : None
            }


        try:
            resolved = socket.gethostbyaddr(ip_address)[0]
        except Exception as e:
            if ip_address.startswith("127.") or ip_address.startswith("192.168") or ip_address.startswith('172.16.99'):
                resolved = "local"
            else:
                resolved = ip_address

        city = country = most_specific_subdivision = None

        geoip2_city_filepath = self.config[configuration_doc.CORE_GEOIP2_CITY_FILEPATH]
        if geoip2_city_filepath and os.path.exists(geoip2_city_filepath):
            try:
                reader = GeoIP2Reader(geoip2_city_filepath)
                city_results = reader.city(ip_address)
                if city_results:
                    if city_results.country and city_results.country.iso_code:
                        country = city_results.country.iso_code

                    if city_results.city and city_results.city.name:
                        city = city_results.city.name

                    if city_results.subdivisions and city_results.subdivisions.most_specific and city_results.subdivisions.most_specific.name:
                        most_specific_subdivision = city_results.subdivisions.most_specific.name
            except GeoIP2Error:
                pass

        if country is None:
            geoip2_country_filepath = self.config[configuration_doc.CORE_GEOIP2_COUNTRY_FILEPATH]
            if geoip2_country_filepath and os.path.exists(geoip2_country_filepath):
                try:
                    reader = GeoIP2Reader(geoip2_country_filepath)
                    country_results = reader.country(ip_address)
                    if country_results:
                        if country_results.country and country_results.country.iso_code:
                            country = city_results.country.iso_code
                except GeoIP2Error:
                    pass


        return {
            'hostname' : resolved,
            'city': city,
            'country': country,
            'most_specific_subdivision' : most_specific_subdivision
        }


class LocationRetriever(threading.Thread):
    SECONDS = 15

    def __init__(self, config, db):
        threading.Thread.__init__(self)
        self.config = config
        self.db = db
        self.setDaemon(True)
        self.stopping = False
        self.locator = AddressLocator(config)
        geoip2_city_filepath = self.config[configuration_doc.CORE_GEOIP2_CITY_FILEPATH]
        if not os.path.exists(geoip2_city_filepath or 'not_found_file'):
            if not is_testing():
                print "%s not found. Run weblab-admin update-locations" % geoip2_city_filepath

    def stop(self):
        self.stopping = True


    def sleepStep(self):
        # Sleep in little steps checking self.stopping
        STEP = 0.1 
        for _ in xrange(int(self.SECONDS / STEP)):
            if self.stopping:
                break
            time.sleep(STEP)

    def run(self):
        while not self.stopping:
            try:
                changes = self.db.update_locations(self.locator.locate)
            except Exception as e:
                traceback.print_exc()
                changes = 0

            if changes == 0:
                self.sleepStep()
            # if there were 1 change, call without sleeping to check 
            # if there was any new change while locating the existing 
            # ones

