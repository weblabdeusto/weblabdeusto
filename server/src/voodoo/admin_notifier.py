#!/usr/bin/python
# -*- coding: utf-8 -*-
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

import smtplib

import weblab.configuration_doc as configuration_doc

import voodoo.log as log
import voodoo.configuration as ConfigurationManager

EMAIL_HEADER = """From: WebLab Notifier <%(mail_notif_sender)s>
To: %(recipients)s
Subject: %(subject)s

"""

EMAIL_BODY = """There was a critical error in WebLab server %(server_hostaddress)s!

Message: %(message)s

WebLab
"""

class AdminNotifier(object):
    """
        This class wraps the notification system.
        In the future, it would be cool if different
        notifier engines were available and used
        transparently through this class, but right now
        the only system available is the mailing system.

        The configuration parameters are:

        [REQUIRED]
        * server_hostaddress
        * server_admin
        * mail_server_host
        * mail_server_use_tls
        * mail_server_helo
        * mail_notification_sender
        [OPTIONAL]
        * mail_notification_subject

        Examples for these values are:

        server_hostaddress  = 'weblab.deusto.es'
        server_admin        = 'porduna@tecnologico.deusto.es'

        (or, if many administrators are set)
        server_admin        = 'porduna@tecnologico.deusto.es, pablo@ordunya.com'

        mail_server_host    = 'rigel.deusto.es' # Mail server machine
        mail_server_use_tls = 'yes' # or 'no'
        mail_server_helo    = 'weblab.deusto.es'

        mail_notification_sender  = 'porduna@tecnologico.deusto.es'
        mail_notification_subject = '[WebLab] CRITICAL ERROR!'
    """
    DEFAULT_NOTIFICATION_SUBJECT = "[WebLab] CRITICAL ERROR!"

    def __init__(self, cfg_manager):
        self._configuration = cfg_manager

    def notify(self, message = None, recipients = None, subject = None, body = None):
        if self._configuration.get_doc_value(configuration_doc.MAIL_NOTIFICATION_ENABLED):
            try:
                server_hostaddress  = self._configuration.get_doc_value(configuration_doc.SERVER_HOSTADDRESS)
                server_admin        = self._configuration.get_doc_value(configuration_doc.SERVER_ADMIN)
                mail_server_host    = self._configuration.get_doc_value(configuration_doc.MAIL_SERVER_HOST)
                mail_server_use_tls = self._configuration.get_doc_value(configuration_doc.MAIL_SERVER_USE_TLS)
                mail_server_helo    = self._configuration.get_doc_value(configuration_doc.MAIL_SERVER_HELO)
                mail_notif_sender   = self._configuration.get_doc_value(configuration_doc.MAIL_NOTIFICATION_SENDER)
                username            = self._configuration.get_doc_value(configuration_doc.MAIL_NOTIFICATION_USERNAME)
                password            = self._configuration.get_doc_value(configuration_doc.MAIL_NOTIFICATION_PASSWORD)
                mail_prefix         = self._configuration.get_doc_value(configuration_doc.MAIL_NOTIFICATION_PREFIX)
            except ConfigurationManager.KeyNotFoundError as knfe:
                log.log(
                    AdminNotifier,
                    log.level.Critical,
                    "Couldn't find property %s. Couldn't notify administrator about critical problem with message <%s>..." % (knfe.key, message)
                )
                return -1

            if subject is None:
                mail_notification_subject = self._configuration.get_doc_value(configuration_doc.MAIL_NOTIFICATION_SUBJECT)
            else:
                mail_notification_subject = subject

            if mail_prefix:
                mail_notification_subject = mail_prefix + " " + mail_notification_subject

            try:
                if recipients is None:
                    mail_recipients = self._parse_recipients(server_admin)
                else:
                    mail_recipients = recipients

                server = self._create_mailer(mail_server_host)
                try:
                    if mail_server_use_tls == 'yes':
                        server.starttls()
                    server.helo(mail_server_helo)

                    if username and password:
                        server.login(username, password)

                    if body is None:
                        email_body = EMAIL_BODY % {
                                    'server_hostaddress' : server_hostaddress,
                                    'message' : message
                                }
                    else:
                        email_body = body

                    server.sendmail(
                        mail_notif_sender,
                        mail_recipients,
                        "%s%s" % (
                            (EMAIL_HEADER % {
                                    'mail_notif_sender' : mail_notif_sender,
                                    'recipients' : ', '.join(mail_recipients),
                                    'subject' : mail_notification_subject,
                                }),
                            email_body
                        )
                    )
                finally:
                    try:
                        server.close()
                    except:
                        pass

            except Exception as e:
                log.log(
                    AdminNotifier,
                    log.level.Critical,
                    "Unexpected error while notifying administrator with message %s: %s" % (message, e)
                )
                return -2
        return 0

    def _create_mailer(self, mail_server):
        return smtplib.SMTP(mail_server)

    def _parse_recipients(self, server_admin):
        server_admin = server_admin.replace(' ','')
        return tuple(server_admin.split(','))

