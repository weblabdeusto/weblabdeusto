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
# Author: Pablo Orduña <pablo@ordunya.com>
# 

import weblab.facade.WebFacadeServer as WebFacadeServer

INTRO_HTML = """<html>
            <head>
                <style>
                    body{
                        font: 14px normal "Lucida Grande", Arial;
                    }
                </style>
            </head>
            <body>
            <center><img src="../logo.png"></center> 
            <p>It seems that your Facebook account has not been linked with a WebLab-Deusto account, or that you don't have a WebLab-Deusto account.</p>
            <br>
            <h2>Already have a WebLab-Deusto account?</h2>
            <p>If you have an account in the University of Deusto and you'd like to link your facebook account (highly recommendable), fill your credentials and press <i>Link</i> to link both accounts so as to use WebLab-Deusto. Doing this you will be able to use the same experiments you use in WebLab-Deusto from Facebook.</p>
            <center><form method="POST" action="%(LINK_URI)s">
            Username: <input type="text" name="username"></input><br/>
            Password: <input type="password" name="password"></input><br/>
            <input type="hidden" name="signed_request" value="%(SIGNED_REQUEST)s"></input>
            <input type="submit" value="Link"></input>
            </form></center>
            <br>
            <h2>New to WebLab-Deusto?</h2>
            <p><a href="http://www.weblab.deusto.es/">WebLab-Deusto</a> is an <a href="http://code.google.com/p/weblabdeusto/">Open Source</a> Remote Laboratory developed in the <a href="http://www.deusto.es/">University of Deusto</a>. Students access experiments physically located in the University from any point in the Internet, just as they would in a hands-on-lab session.
            <p>If you don't have a WebLab-Deusto account but you'd like to see it, click on <i>Create</i> and you'll have a new account with permissions to the default demos we have deployed, with safe experiments that we know that final users will not be able to break.</p>
            <center> <form method="POST" action="%(CREATE_URI)s">
                <input type="hidden" name="signed_request" value="%(SIGNED_REQUEST)s"></input>
                <input type="submit" value="Create"></input>
            </form> </center>
        </body></html>"""

class FacebookMethod(WebFacadeServer.Method):
    path = '/facebook/'

    def get_local_relative_path(self):
        return self.relative_path[len(path)+1:]

    def run(self):
        return ":-)"


