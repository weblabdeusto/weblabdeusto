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

import urllib
from voodoo.sessions.session_id import SessionId
from weblab.core.exc import SessionNotFoundError
import weblab.comm.web_server as WebFacadeServer

RESERVATION_ID   = 'reservation_id'
FORMAT_PARAMETER = 'format'

REDIRECT_CODE = """<html><head>
<title>WebLab-Deusto client redirect</title>
<script type="text/javascript">
    function submit_form(){
        document.getElementById('reservation_form').submit();
    }
</script>
</head>
<body onload="javascript:submit_form();">
    <p>Please, click on 'Submit'</p>
    <form action="." method="POST" id="reservation_form">
        <input type="text" name="reservation_id" value="%(reservation_id)s" />
        <input type="submit" value="Submit"/>
    </form>
    <p>Reason:%(reason)s</p>
    <input type="submit" value="Back" onclick="window.history.back()"/>
</body>
"""

LABEL_CODE = """<html><head>
<title>WebLab-Deusto client redirect</title>
<script type="text/javascript">
    function submit_form(){
        var cur_hash = location.hash.substring(1);
        var reservation_id = 'Reservation id not found in history object';
        var variables = cur_hash.split('&');
        for(var i in variables){
            var cur_variable = variables[i];
            if(cur_variable.indexOf('reservation_id=') == 0)
                reservation_id = cur_variable.substring('reservation_id='.length);
        }
        document.getElementById('reservation_id_text').value = reservation_id;
        document.getElementById('reservation_form').submit();
    }
</script>
</head>
<body onload="javascript:submit_form();">
    <p>Please, click on 'Submit' to proceed, or in 'Back' to go back.</p>
    <form action="." method="POST" id="reservation_form">
        <input id="reservation_id_text" type="text" name="reservation_id" value="" />
        <input type="submit" value="Submit"/><br/>
    </form>
    <input type="submit" value="Back" onclick="window.history.back()"/>
</body>
"""

FINAL_REDIRECT = """<html><head>
<title>WebLab-Deusto client redirect</title>
<script type="text/javascript">
    function redirect_to_client(){
        window.location="%(URL)s";
    }
</script>
</head>
<body onload="javascript:redirect_to_client();">
Please, go to <a href="%(URL)s">%(URL)s</a>.<br/>
<input type="submit" value="Back" onclick="window.history.back()"/>
</body>
"""

ERROR_CODE = """<html><head>
<title>WebLab-Deusto client redirect</title>
<body>
It was not possible to retrieve the reservation_id %s in this server.
<input type="submit" value="Back" onclick="window.history.back()"/>
</body>
"""

class ClientMethod(WebFacadeServer.Method):
    path = '/client/'

    def run(self):
        """ run()

        If there is a GET argument named %(reservation_id)s, it will take it and resend it as a
        POST argument. If it was passed through the history, then it will be again sent as a
        POST argument. Finally, if it is received as a POST argument, it will generate a redirect
        to the client, using the proper current structure.
        """ % { 'reservation_id' : RESERVATION_ID }

        # If it is passed as a GET argument, send it as POST
        reservation_id = self.get_GET_argument(RESERVATION_ID)
        if reservation_id is not None:
            return REDIRECT_CODE % {
                'reason'         : 'GET performed',
                'reservation_id' : urllib.unquote(reservation_id)
            }

        # If it is passed as History (i.e. it was not passed by GET neither POST),
        # pass it as a POST argument
        reservation_id = self.get_POST_argument(RESERVATION_ID)
        if reservation_id is None:
            return LABEL_CODE

        reservation_id = urllib.unquote(reservation_id)

        if self.req.server_route is not None:
            # If the request should not go to the current server
            if reservation_id.find('.') >= 0 and not reservation_id.endswith(self.req.server_route):
                if reservation_id.find(';') >= 0:
                    partial_reservation_id = reservation_id.split(';')[1]
                else:
                    partial_reservation_id = reservation_id
                self.req.weblab_cookie = 'weblabsessionid=%s' % partial_reservation_id
                self.req.login_weblab_cookie = 'loginweblabsessionid=%s' % partial_reservation_id
                return REDIRECT_CODE % {
                    'reason'         : 'reservation_id %s does not end in server_route %s' % (reservation_id, self.req.server_route),
                    'reservation_id' : reservation_id
                }

        if reservation_id.find(';') >= 0:
            partial_reservation_id = reservation_id.split(';')[1]
        else:
            partial_reservation_id = reservation_id

        self.req.weblab_cookie = 'weblabsessionid=%s' % partial_reservation_id
        self.req.login_weblab_cookie = 'loginweblabsessionid=%s' % partial_reservation_id


        # Finally, if it was passed as a POST argument, generate the proper client address
        reservation_session_id = SessionId(reservation_id.split(';')[0])
        try:
            experiment_id = self.server.get_reservation_info(reservation_session_id)
        except SessionNotFoundError:
            return ERROR_CODE % reservation_id

        client_address = "../../client/index.html#exp.name=%(exp_name)s&exp.category=%(exp_cat)s&reservation_id=%(reservation_id)s&header.visible=false&page=experiment" % {
            'reservation_id' : reservation_id,
            'exp_name'       : experiment_id.exp_name,
            'exp_cat'        : experiment_id.cat_name
        }

        format_parameter = self.get_POST_argument(FORMAT_PARAMETER)
        if format_parameter is not None and format_parameter == 'text':
            return client_address

        return FINAL_REDIRECT % { 'URL' : client_address }


