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
# Author: Jaime Irurzun <jaime.irurzun@gmail.com>

import smtplib

TEMPLATE = """From: %(FROM)s
To: %(TO)s
Subject: %(SUBJECT)s
    
%(TEXT)s
"""

class SmtpGateway(object):

    def __init__(self, host, helo):
        super(SmtpGateway, self).__init__()
        self.host = host
        self.helo = helo
        self.server = smtplib.SMTP(self.host)
        self.server.starttls()
        self.server.helo(self.helo)
        
    def send(self, fromm, to, subject, text):
        self.server.sendmail(fromm, to, TEMPLATE % {'FROM': fromm, 'TO': to, 'SUBJECT': subject, 'TEXT': text})