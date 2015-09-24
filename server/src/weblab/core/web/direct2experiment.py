#!/usr/bin/env python
#-*-*- encoding: utf-8 -*-*-
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

import traceback
from flask import redirect
from weblab.core.web import weblab_api, get_argument

from weblab.data.experiments import ExperimentId

EXPERIMENT_ID       = "experiment_id"
SESSION_ID          = "session_id"

HTML_ERROR_TEMPLATE = """<html><body>
There was an error reserving the desired experiment. Typically, this means that
you don't have permissions to use the requested experiment. You can check it by
entering WebLab through the usual interface (<a href="../../client">here</a>).
If you indeed have permissions or this problem persists, please contact the
administrator.
</body></html>
"""


@weblab_api.route_web('/direct2experiment/', methods = ['GET', 'POST'])
def direct2experiment():
    experiment_id_str = get_argument(EXPERIMENT_ID)
    if experiment_id_str is None:
        return "%s argument is missing" % EXPERIMENT_ID
    session_id_str = get_argument(SESSION_ID)
    if session_id_str is None:
        return "%s argument is missing" % EXPERIMENT_ID

    experiment_id = ExperimentId.parse(experiment_id_str)
    weblab_api.context.session_id = session_id_str

    try:
        reservation_id = weblab_api.api.reserve_experiment(experiment_id, "{}", "{}")
    except Exception:
        traceback.print_exc()
        return HTML_ERROR_TEMPLATE

    new_location = "../../client/federated.html#reservation_id=%s" % reservation_id.reservation_id.id
    return redirect(new_location)

