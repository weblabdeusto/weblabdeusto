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

import weblab.comm.web_server as WebFacadeServer
import weblab.data.client_address as ClientAddress
import weblab.comm.context as RemoteFacadeContext
from weblab.data.experiments import ExperimentId
from voodoo.sessions.session_id import SessionId
from voodoo.log import logged
import voodoo.log as log

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


class Direct2ExperimentMethod(WebFacadeServer.Method):
    path = '/direct2experiment/'

    @logged(log.level.Info)
    def run(self):
        experiment_id_str = self.get_argument(EXPERIMENT_ID)
        if experiment_id_str is None:
            return "%s argument is missing" % EXPERIMENT_ID
        session_id_str = self.get_argument(SESSION_ID)
        if session_id_str is None:
            return "%s argument is missing" % EXPERIMENT_ID

        experiment_id = ExperimentId.parse(experiment_id_str)
        session_id = SessionId(session_id_str)

        address = RemoteFacadeContext.get_context().get_ip_address()
        client_address = ClientAddress.ClientAddress(address)
        try:
            reservation_id = self.server.reserve_experiment(session_id, experiment_id, "{}", "{}", client_address)
        except Exception:
            return HTML_ERROR_TEMPLATE

        new_location = "../../client/federated.html#reservation_id=%s" % reservation_id.reservation_id.id
        self.set_status(302)
        self.add_other_header('Location', new_location)
        return """<html><body><a href="%s">Click here</a></body></html>""" % new_location

