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

import json
import uuid
import hashlib
import datetime

import weblab.experiment.experiment as Experiment
import weblab.core.coordinator.coordinator as Coordinator

from voodoo.override import Override

def rc4(data, key):
    """
    Encrypts the data with key key using RC4. Based on the pseudocode presented in:

    Using the http://en.wikipedia.org/wiki/ARC4 
    """
    # The key-scheduling algorithm (KSA)
    S = range(256)
    j = 0
    for i in xrange(256):
        j = ( j + S[i] + ord(key[i % len(key)]) ) % 256

        S[i], S[j] = S[j], S[i]

    # The pseudo-random generation algorithm (PRGA)
    i = 0
    j = 0
    output = []

    for c in data:
        i = (i + 1) % 256
        j = (j + S[i]) % 256

        S[i], S[j] = S[j], S[i]

        k = ord(c) ^ S[ (S[i] + S[j]) % 256]
        output.append( chr(k) )

    return ''.join(output)

DEFAULT_URL = 'http://labremf4a.fceia.unr.edu.ar/accesodeusto.aspx?id_instalacion=%(INSTALLATION)s&cadena=%(DATA)s&checksum=%(HASH)s'

class UnrExperiment(Experiment.Experiment):
    def __init__(self, coord_address, locator, cfg_manager, *args, **kwargs):
        super(UnrExperiment,self).__init__(*args, **kwargs)
        self._user     = cfg_manager.get_value('unr_user', None)
        self._password = cfg_manager.get_value('unr_password', None)
        self._url_tpl  = cfg_manager.get_value('unr_url', DEFAULT_URL)

        if self._user is None or self._password is None:
            raise Exception("Attempting to instanciate UnrExperiment without configuring unr_user or unr_password")

    @Override(Experiment.Experiment)
    def do_get_api(self):
        return "2"


    @Override(Experiment.Experiment)
    def do_start_experiment(self, serialized_client_initial_data, serialized_server_initial_data):

        dtime = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

        server_initial_data = json.loads(serialized_server_initial_data)

        username   = server_initial_data.get('request.username')
        fullname   = server_initial_data.get('request.full_name')

        random_str = uuid.uuid4()
        data       = "username=%(username)s&fullname=%(fullname)s&timestamp=%(timestamp)s&random=%(random)s" % {
            'username'  : username,
            'fullname'  : fullname,
            'timestamp' : dtime,
            'random'    : random_str,
        }
        crypted   = rc4(data, self._password)
        data_hash = hashlib.new("md5", data).hexdigest()

        self._url = self._url_tpl %  {
            'INSTALLATION' : self._user,
            'DATA' : crypted.encode('hex'), 
            'HASH' : data_hash,
        }

        return json.dumps({ "initial_configuration" : self._url, "batch" : True })

    @Override(Experiment.Experiment)
    def do_dispose(self):
        return_value = json.dumps({ Coordinator.FINISH_FINISHED_MESSAGE : True, Coordinator.FINISH_DATA_MESSAGE : self._url})
        return return_value

    @Override(Experiment.Experiment)
    def do_should_finish(self):
        return -1

    @Override(Experiment.Experiment)
    def do_send_command_to_device(self, command):
        return 'Not implemented'

    @Override(Experiment.Experiment)
    def do_send_file_to_device(self, content, file_info):
        return 'Not implemented'

