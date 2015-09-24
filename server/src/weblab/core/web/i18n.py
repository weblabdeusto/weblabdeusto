#!/usr/bin/env python
#-*-*- encoding: utf-8 -*-*-
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
#         Luis Rodriguez <luis.rodriguez@opendeusto.es>
#
from __future__ import print_function, unicode_literals

import os
import codecs
import json
import traceback

from flask import Response

from weblab.core.wl import weblab_api
from weblab.util import data_filename

try:
    I18N = json.load(codecs.open(data_filename(os.path.join('weblab', 'i18n.json')), encoding = 'utf-8'))
except:
    print("Error loading weblab/i18n.json. Did you run weblab-admin upgrade? Check the file")
    traceback.print_exc()
    I18N = {
        'generic_experiments' : {},
        'experiments' : {}
    }

@weblab_api.route_web('/i18n/<category_name>/<experiment_name>/')
def i18n(category_name, experiment_name):
    mails = [ mail.strip() for mail in weblab_api.config.get('server_admin', '').split(',') if mail.strip() ]
    response = {
        'translations' : {
        # lang : {
        #    key : {
        #        value: value,
        #        namespace: namespace
        #    }
        # }
        },
        'mails' : mails
    }

    generic_experiments = I18N['generic_experiments']
    for lang in generic_experiments:
        response['translations'][lang] = {}
        for key, value in generic_experiments[lang].iteritems():
            response['translations'][lang][key] = {
                'value' : value,
                'namespace' : 'http://weblab.deusto.es/weblab/#'
            }

    client_id = weblab_api.db.get_client_id(experiment_name, category_name)
    if client_id == 'js':
        # TODO: we need something like metadata for the parameters and so on
        if 'archimedes' in experiment_name or 'arquimedes' in experiment_name:
            client_id = 'archimedes'

    if client_id is not None and client_id in I18N['experiments']:
        for lang in I18N['experiments'][client_id]:
            if lang not in response['translations']:
                response['translations'][lang] = {}
            for key, value in I18N['experiments'][client_id][lang].iteritems():
                response['translations'][lang][key] = {
                    'value' : value,
                    'namespace' : 'http://weblab.deusto.es/weblab/experiments/%s/#' % client_id,
                }

    return Response(json.dumps(response, indent = 4), mimetype='application/json')
