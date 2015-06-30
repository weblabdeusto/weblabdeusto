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
#
from __future__ import print_function, unicode_literals

from weblab.core.web import get_argument
from weblab.core.wl import weblab_api

import weblab.data.command as Command

SESSION_ID = 'session_id'

HTML_TEMPLATE="""<?xml version="1.0"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html>
    <head>
        <title>LabVIEW</title>
    </head>
    <body>%(MESSAGE)s</body>
</html>
"""

@weblab_api.route_web('/labview/')
def labview():
    try:
        reservation_id = get_argument(SESSION_ID)
        if reservation_id is None:
            return HTML_TEMPLATE % {
                        'MESSAGE' : "Failed to load LabVIEW experiment. Reason: %s argument not provided!." % SESSION_ID
                    }

        weblab_api.ctx.reservation_id = reservation_id
        result = weblab_api.api.send_command(Command.Command("get_html"))
    except Exception as e:
        message = e.args[0]
        return HTML_TEMPLATE % {
                    'MESSAGE' : "Failed to load LabVIEW experiment. Reason: %s. Call the administrator to fix it." % message
                }
    else:
        resultstr = result.commandstring
        print("[DBG] Returning result from labview: " + resultstr)
        return HTML_TEMPLATE % {
                    'MESSAGE' : resultstr
                }

