#!/usr/bin/env python
#-*-*- encoding: utf-8 -*-*-
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

import os, glob
from weblab.admin.bot.misc import show_time, flush

import cPickle as pickle

FILE_NAME_TEMPLATE = "logs" + os.sep + "botclient_%s__SCEN_%s_CONFIG_0.pickle"
FILL_NUMBER = 2
RANGES = [
        lambda : xrange(1, 5),
        lambda : xrange(5, 151, 5)
    ]

def get_raw_information(date, verbose = True):
    file_name = FILE_NAME_TEMPLATE % (date, '%s')
    raw_information_filename = 'raw_information_%s.dump' % date
    if os.path.exists(raw_information_filename):
        if verbose:
            print("Retrieving cache", show_time())
            flush()
        raw_information = pickle.load(open(raw_information_filename))
        if verbose:
            print("Retrieved cached raw_information", show_time())
            flush()
        return raw_information

    if verbose:
        print("Generating new raw_information", show_time())
        flush()
    # else generate this information file
    def calculate_positions(initial):
        data = {}
        for r in RANGES:
            for i in r():
                data[i] = str(initial).zfill(FILL_NUMBER)
                initial += 1
        return data, initial

    def calculate_protocols():
        # returns 
        # { "JSON" : { 1 : "01", 2 : "02", 5 : "03" ... } ...}
        # being each "01", "02" the name of the file for 
        # that protocol and for that number of users
        protocols = {
                "JSON"   : {},
            }

        protocols = {}
        data, initial = calculate_positions(0)
        protocols["JSON"] = data
        return protocols

    protocols = calculate_protocols()

    def get_results(protocol, number):
        # 
        # Given a protocol and a number of users (1,2,3,4,5,10,15...),
        # it returns the results stored in that scenario
        #
        found_resources = sorted(glob.glob(file_name % "*"), lambda x,y: len(x) - len(y))
        if len(found_resources) == 0:
            raise Exception("No similar file found: %s" % file_name)

        regular_length = len(found_resources[len(found_resources)/2]) # Take the one in the middle
        number_length  = regular_length - len(file_name % '')

        filename = file_name % str(int(protocols[protocol][number])).zfill(number_length)
        results = pickle.load(open(filename))
        return results

    def generate_data(protocol):
        # Given a protocol, it returns the following tuple
        # 
        # x = [1,2,3,4,5,10,15,20,25]
        # y = [results_of_1, results_of_2 ...]
        # 
        x = []
        y = []
        for r in RANGES:
            for n in r():
                x.append(n)
                results = get_results(protocol, n)
                y.append(results)
        return x,y

    raw_information = {}
    for protocol in protocols.keys():
        x, y = generate_data(protocol)
        raw_information[protocol] = (x,y)

    # raw_information stores:
    # { "JSON" : ([1,2,3,4,5,10...], [results_of_1, results_of_2, results_of_3 ...]) }

    # Save as a cache
    pickle.dump(raw_information, open(raw_information_filename,'w'))

    if verbose:
        print("Raw_information generated", show_time())
        flush()

    return raw_information

