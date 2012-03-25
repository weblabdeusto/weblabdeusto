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

import cgi
import urllib
import weblab.comm.web_server as WebFacadeServer
import weblab.login.exc as LoginErrors

USERNAME="username"
PASSWORD="password"
EXPERIMENT_ID="experiment_id"

HTML_LOGIN_TEMPLATE="""<html>
<head>
    <title>Log in</title>
</head>
<body>
    <form method="POST" action=".?%s=%s">
        Username: <input type="text" name="username"/><br/>
        Password: <input type="password" name="password"/><br/>
        <input type="submit" name="Log in"/>
    </form>
</body>
</html>""" % (EXPERIMENT_ID, '%s')

HTML_INVALID_CREDENTIALS_TEMPLATE="""<html>
<head>
    <title>Log in</title>
</head>
<body>
    Invalid username or password. Please try again.<br/>
    <form method="POST" action=".?%s=%s">
        Username: <input type="text" name="username"/><br/>
        Password: <input type="password" name="password"/><br/>
        <input type="submit" name="Log in"/>
    </form>
</body>
</html>""" % (EXPERIMENT_ID, '%s')

HTML_ERROR_TEMPLATE="""<html>
<head>
    <title>Log in</title>
</head>
<body>
    Error logging in. Please try again.<br/>
    <form method="POST" action=".?%s=%s">
        Username: <input type="text" name="username"/><br/>
        Password: <input type="password" name="password"/><br/>
        <input type="submit" name="Log in"/>
    </form>
</body>
</html>""" % (EXPERIMENT_ID, '%s')


HTML_REDIRECT_TEMPLATE="""<html>
<head>
    <title>WebLab-Deusto redirector</title>
    <script type="text/javascript">
    <!--
        function redirect_weblab(){
            document.getElementById('reservation_form').submit();
        }
    //-->
    </script>
</head>
<body onload="javascript:redirect_weblab();">
    <p>Please, click on 'Submit'</p>
    <form action="../../../web/direct2experiment/" method="POST" id="reservation_form">
        <input type="text" name="session_id"    value="%(session_id)s" />
        <input type="text" name="experiment_id" value="%(experiment_id)s" />
        <input type="submit" value="Submit"/>
    </form>
    </div>
</body>
</html>
"""

class Direct2ExperimentMethod(WebFacadeServer.Method):
    path = '/direct2experiment/'

    def run(self):
        experiment_id = self.get_argument(EXPERIMENT_ID)
        if experiment_id is None:
            return "%s argument is missing" % EXPERIMENT_ID
        username = self.get_argument(USERNAME)
        if username is None:
            return HTML_LOGIN_TEMPLATE % cgi.escape(experiment_id)

        password = self.get_argument(PASSWORD)
        try:
            session_id = self.server.login(username, password)
        except LoginErrors.InvalidCredentialsError:
            return HTML_INVALID_CREDENTIALS_TEMPLATE % cgi.escape(experiment_id)
        except Exception:
            return HTML_ERROR_TEMPLATE % cgi.escape(experiment_id)

        return HTML_REDIRECT_TEMPLATE % {
            'session_id'    : session_id.id,
            'experiment_id' : urllib.unquote(experiment_id)
        }

