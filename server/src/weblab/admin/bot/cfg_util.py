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
from __future__ import print_function, unicode_literals

import sys
import socket
import traceback
import subprocess

from weblab.admin.bot.user import StandardBotUser, DisconnectedBotUser, NotRespondingBotUser

def generate_url_maps(base_url):
    return {
                        "JSON" :   ("%s/weblab/json/" % base_url, "%s/weblab/login/json/" % base_url),
                    }

def get_supported_protocols():
    return generate_url_maps("http://localhost").keys()

def generate_new_standard_bot_user(base_url, username, password, experiment_name, category_name, program_file):
    def new_standard_bot_user(initial_delay, protocol):
        return lambda : StandardBotUser(
                            generate_url_maps(base_url),
                            protocol,
                            username = username,
                            password = password,
                            experiment_name = experiment_name,
                            category_name   = category_name,
                            program         = program_file,
                            initial_delay   = initial_delay
                        )
    return new_standard_bot_user

def generate_new_disconnected_bot_user(base_url, username, password, experiment_name, category_name, program_file):
    def new_disconnected_bot_user(initial_delay, protocol):
        return lambda : DisconnectedBotUser(
                            generate_url_maps(base_url),
                            protocol,
                            username = username,
                            password = password,
                            experiment_name = experiment_name,
                            category_name   = category_name,
                            program         = program_file,
                            initial_delay   = initial_delay
                        )
    return new_disconnected_bot_user

def generate_new_notresponding_bot_user(base_url, username, password, experiment_name, category_name, program_file):
    def new_notresponding_bot_user(initial_delay, protocol):
        return lambda : NotRespondingBotUser(
                            generate_url_maps(base_url),
                            protocol,
                            username = username,
                            password = password,
                            experiment_name = experiment_name,
                            category_name   = category_name,
                            program         = program_file,
                            initial_delay   = initial_delay
                        )
    return generate_new_notresponding_bot_user

def new_bot_users(number, func, initial_delay, delay_step, *args, **kwargs):
    def delayer(initial_delay):
        delay = initial_delay
        while True:
            yield delay
            delay += delay_step
    delayer_it = delayer(initial_delay)
    return [ (func.func_name + '_' + str(args) + '_' + str(kwargs), func(delayer_it.next(), *args, **kwargs)) for _ in xrange(number) ]

def generate_revision():
    try:
        p = subprocess.Popen("git show",shell=True,stdout=subprocess.PIPE)
        p.wait()
        return p.stdout.read().split('\n')[0].split()[1]
    except Exception, e:
        print("Could not gather revision:",e)
        traceback.print_exc()
        return "(unknown)"

def retrieve_system(SYSTEMS):
    try:
        hostname = socket.gethostname()
    except:
        print("Couldn't retrieve host name", file=sys.stderr)
        return "Unknown system"
    else:
        if hostname in SYSTEMS:
            return SYSTEMS[hostname]
        else:
            print("Couldn't retrieve machine information in SYSTEMS dictionary for hostname %s" % hostname, file=sys.stderr)
            return "Unknown system"

def create_new_scenario():
    class Scenario(object):
        categories = {}

        def __init__(self, users, category = "generic_category", identifier = None):
            self.category   = category
            if not category in self.categories:
                self.categories[category] = []
            if identifier is None:
                self.identifier = self.next_id(category)
            elif identifier in self.categories[category]:
                raise RuntimeError("Category %s already has an identifier %s" % (category, identifier))
            else:
                self.identifier = identifier
            self.categories[category].append(self.identifier)
            self.users      = users

        def next_id(self, category):
            n = 0
            while True:
                if not n in self.categories[category]:
                    return n
                n += 1

        def dispose(self):
            del self.users

        def __repr__(self):
            return '<Scenario category="%s" identifier="%s" />' % (self.category, self.identifier)

    return Scenario
