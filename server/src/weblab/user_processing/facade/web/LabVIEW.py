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

from voodoo.sessions.SessionId import SessionId
import weblab.facade.WebFacadeServer as WebFacadeServer

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

class LabViewMethod(WebFacadeServer.Method):
    path = '/labview/'

    def run(self):
        """
        run()
        @return HTML defined above, with the success or failure response.
        """
        try:
            session_id = self._check_arguments()
            sid = SessionId(session_id)
            result = self.server.send_command(sid, "get_html")
        except LabViewException, lve:
            message = lve.args[0]
            return HTML_TEMPLATE % {
                        'MESSAGE' : "Failed to load LabVIEW experiment. Reason: %s." % message
                    }
        except Exception, e:
            message = e.args[0]
            return HTML_TEMPLATE % {
                        'MESSAGE' : "Failed to load LabVIEW experiment. Reason: %s. Call the administrator to fix it." % message
                    }
        else:
            resultstr = result.commandstring
            print "[DBG] Returning result from labview: " + resultstr
            return HTML_TEMPLATE % {
                            'RESULT' : resultstr
                    }

    def _check_arguments(self):
        session_id = self.get_argument(SESSION_ID)
        if session_id is None:
            raise LabViewException("%s argument not provided!" % SESSION_ID)
        
        return session_id

class LabViewException(Exception):
    pass

