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
#

import smtplib
import traceback
import sys

from DbManager import DbManager

try:
    import configuration
except Exception, e:
    print "File configuration.py not found. See configuration.py.dist. Error:", str(e)
    sys.exit(1)


def send_mails(users):

    server = smtplib.SMTP(configuration.SMTP_SERVER)
    server.starttls()
    server.helo(configuration.SMTP_SERVER_HELO)

    for user in users:
        print "Sending e-mail to %s" % user['login']
        try:
            recipients = (user['email'],) + configuration.ADMINS
            server.sendmail(
                    configuration.FROM, 
                    recipients,
                    configuration.BODY % {'TO': user['email'], 'FULL_NAME': user['full_name']}
                )
        except Exception, e:
            print "Error sending e-mail: ", e
            traceback.print_stack()
    print "[done]" 
    

if __name__ == '__main__':
    
    db = DbManager()
    
    for group in configuration.GROUPS:
        print "Grupo:", group
        send_mails(db.get_group_users(group))
