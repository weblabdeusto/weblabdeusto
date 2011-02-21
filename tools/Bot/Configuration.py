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
#         Pablo Orduña <pablo@ordunya.com>
#

import sys, os, socket
sys.path.append(os.sep.join(('..','..','server','src')))

import libraries

from weblab.admin.bot.User import StandardBotUser, DisconnectedBotUser, NotRespondingBotUser

WEBLAB_PATH         = ('..','..','server','src')        # WebLab's source root path from this folder

LAUNCH_FILE         = "sample/launch_sample.py"                # Name of the file that launches a WebLab process

HOST                = "localhost"                       # WebLab's hostname
USERNAME            = "student1"                        # WebLab's username to login
PASSWORD            = "password"                        # WebLab user's password do login
EXPERIMENT_NAME     = "ud-dummy"                        # Experiment name to interact with
CATEGORY_NAME       = "Dummy experiments"               # Experiment category name to interact with
PROGRAM_FILE        = "this is the content of the file" # Program file to send

ITERATIONS          = 3                                # Times to repeat each launch

URL_MAPS            = {
                        "SOAP" : ("http://%s/weblab/soap/" % HOST, "http://%s/weblab/login/soap/" % HOST),
                        "JSON" : ("http://%s/weblab/json/" % HOST, "http://%s/weblab/login/json/" % HOST),
                        "XMLRPC" : ("http://%s/weblab/xmlrpc/" % HOST, "http://%s/weblab/login/xmlrpc/" % HOST)
                    }

GENERATE_GRAPHICS   = True
MATPLOTLIB_BACKEND  = 'cairo.pdf'
STEP_DELAY          = 0.05
REVISION            = 1372
REVISION            = 1530

SYSTEMS = {
            "blood"         : "Intel(R) Core(TM)2 Duo CPU T7250@2.00GHz reduced to 1.60 GHz; 3.5 GB RAM (32 bit); Ubuntu 9.04 Desktop. Python 2.6.2. Linux 2.6.28-14-generic",
            "nctrun-laptop" : "Intel(R) Pentium(R) 4 CPU 3.40GHz with Hyperthreading (2); 2.0 GB RAM (32 bit); Ubuntu 9.04 Desktop. Python 2.6.2. Linux 2.6.28-15-generic",
            "hook"          : "Intel(R) Pentium(R) 4 CPU 2.8GHz; 1.0 GB RAM (32 bit); Ubuntu 9.10 Desktop. Python 2.6.4. Linux 2.6.31-16-generic",
            "ord3p"         : "Intel(R) Core(TM)2 Duo CPU T7250  @ 2.00GHz; 3.5 GB RAM (32 bit); Ubuntu 9.10 Desktop. Python 2.6.4. Linux 2.6.31-17-generic"
        }

try:
    hostname = socket.gethostname()
except:
    SYSTEM = "Unknown system"
    print >> sys.stderr, "Couldn't retrieve host name"
else:
    if hostname in SYSTEMS:
        SYSTEM = SYSTEMS[hostname]
    else:
        SYSTEM = "Unknown system"
        print >> sys.stderr, "Couldn't retrieve machine information in SYSTEMS dictionary for hostname %s" % hostname

# SOAP, JSON, XMLRPC
PROTOCOL_USED       = "JSON"

def new_standard_bot_user(initial_delay, protocol = PROTOCOL_USED):
    return lambda : StandardBotUser(
                        URL_MAPS,
                        protocol,
                        username = USERNAME,
                        password = PASSWORD,
                        experiment_name = EXPERIMENT_NAME,
                        category_name   = CATEGORY_NAME,
                        program         = PROGRAM_FILE,
                        initial_delay   = initial_delay
                    )

def new_disconnected_bot_user(initial_delay, protocol = PROTOCOL_USED):
    return lambda : DisconnectedBotUser(
                        URL_MAPS,
                        protocol,
                        username = USERNAME,
                        password = PASSWORD,
                        experiment_name = EXPERIMENT_NAME,
                        category_name   = CATEGORY_NAME,
                        program         = PROGRAM_FILE,
                        initial_delay   = initial_delay
                    )

def new_notresponding_bot_user(initial_delay, protocol = PROTOCOL_USED):
    return lambda : NotRespondingBotUser(
                        URL_MAPS,
                        protocol,
                        username = USERNAME,
                        password = PASSWORD,
                        experiment_name = EXPERIMENT_NAME,
                        category_name   = CATEGORY_NAME,
                        program         = PROGRAM_FILE,
                        initial_delay   = initial_delay
                    )

def new_bot_users(number, func, initial_delay, delay_step, *args, **kwargs):
    def delayer(initial_delay):
        delay = initial_delay
        while True:
            yield delay
            delay += delay_step
    delayer_it = delayer(initial_delay)
    return [ (func.func_name + '_' + str(args) + '_' + str(kwargs), func(delayer_it.next(), *args, **kwargs)) for _ in xrange(number) ]

class Scenario(object):
    categories = {}

    def __init__(self, users, category = "generic_category", identifier = None):
        self.category   = category
        if not category in self.categories:
            self.categories[category] = []
        if identifier is None:
            self.identifier = self.next_id(category)
        elif identifier in self.categories[category]:
            raise RuntimeException("Category %s already has an identifier %s" % (category, identifier))
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

    def __repr__(self):
        return '<Scenario category="%s" identifier="%s" />' % (self.category, self.identifier)

SCENARIOS           = [ 
#            # Scenario 1: 5 StandardBotUsers
#                    Scenario(new_bot_users(30, new_standard_bot_user))
#            ,
#            # Scenario 2: 2 StandardBotUsers
#                    Scenario(new_bot_users(2, new_standard_bot_user))
#            ,
#            # Scenario 3:
#                    Scenario(
#                       new_bot_users(3, new_standard_bot_user)
#                       + 
#                       new_bot_users(2, new_disconnected_bot_user)
#                       + 
#                       new_bot_users(6, new_notresponding_bot_user)
#                    )
        ]

for protocol in URL_MAPS.keys():
    for number in range(1, 5):
        SCENARIOS.append(
                Scenario(
                    new_bot_users(number, new_standard_bot_user, 0, STEP_DELAY, protocol),
                    protocol,
                    number
                )
            )
    break
    for number in range(5, 101, 5):
        SCENARIOS.append(
                Scenario(
                    new_bot_users(number, new_standard_bot_user, STEP_DELAY * (5 -1), STEP_DELAY, protocol),
                    protocol,
                    number
                )
            )

CONFIGURATIONS      = [
                        "sample/launch_sample.py"
#                        "sample_xmlrpc/launch_sample_xmlrpc_machine.py"
#                        "sample_internetsocket/launch_sample_internetsocket_machine.py"
#                        "sample_unixsocket/launch_sample_unixsocket_machine.py"
#                        "sample_balanced1/launch_sample_balanced1_machine.py"
#                        "sample_balanced2/launch_sample_balanced2_machine.py"
                      ]

_default_ports = {
                'soap'         : (10123,),
                'json'         : (18345,),
                'xmlrpc'       : (19345,),
                'soap_login'   : (10623,),
                'json_login'   : (18645,),
                'xmlrpc_login' : (19645,)
            }

_two_facades_ports = {
                'soap'         : (10123,20123),
                'json'         : (18345,28345),
                'xmlrpc'       : (19345,29345),
                'soap_login'   : (10623,20623),
                'json_login'   : (18645,28645),
                'xmlrpc_login' : (19645,29645)
            }

_three_facades_ports = {
                'soap'         : (10123,20123,30123),
                'json'         : (18345,28345,38345),
                'xmlrpc'       : (19345,29345,39345),
                'soap_login'   : (10623,20623,30623),
                'json_login'   : (18645,28645,38645),
                'xmlrpc_login' : (19645,29645,39645)
            }

PORTS = {
        "sample/launch_sample.py" : _default_ports,
        "sample_xmlrpc/launch_sample_xmlrpc_machine.py" : _default_ports,
        "sample_internetsocket/launch_sample_internetsocket_machine.py" : _default_ports,
        "sample_unixsocket/launch_sample_unixsocket_machine.py" : _default_ports,
        "sample_balanced1/launch_sample_balanced1_machine.py" : _two_facades_ports,
        "sample_balanced2/launch_sample_balanced2_machine.py" : _three_facades_ports,
    }

RUNNING_CONFIGURATION = "r%s. %s iterations; step_delay: %s seconds; %s" % (REVISION, ITERATIONS, STEP_DELAY, CONFIGURATIONS)

