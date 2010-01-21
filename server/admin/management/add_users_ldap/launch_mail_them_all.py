#!/usr/bin/env python
#-*-*- encoding: utf-8 -*-*-

from users import User
import pickle
import smtplib
import traceback

from configuration import TESTING, ADMINISTRATORS, MAIL_SERVER, MAIL_SERVER_HELO, MAIL_BODY, USERS_FILE

def send_email_to_users(users):
    if TESTING:
        test_user = User(
                login     = 'generic_user',
                name      = 'Generic',
                surname   = 'User',
                email     = ADMINISTRATORS[0]
            )

        recipients = [test_user]
    else:
        recipients = users

    server = smtplib.SMTP(MAIL_SERVER)
    server.starttls()
    server.helo(MAIL_SERVER_HELO)

    mail_sent = {}

    for user in recipients:
        print "Sending e-mail to %s" % user.login
        try:
            recipients = (user.email,) + ADMINISTRATORS
            server.sendmail(
                    ADMINISTRATORS[0], 
                    recipients,
                    MAIL_BODY % {
                        'recipient'    : user.email,
                        'full_name'    : user.full_name,
                        'login'        : user.login
                    }
                )
        except Exception, e:
            print "Error sending e-mail: ", e
            traceback.print_stack()
            mail_sent[user] = e
        else:
            mail_sent[user] = None

    print "[done]"
    return mail_sent

users = pickle.load(open(USERS_FILE))

response = raw_input("Are you sure you want to send the e-mail to %s users? (y/n)" % len(users))

if response == 'y':
    print "Starting to send emails..."
    send_email_to_users(users)
else:
    print "Action cancelled by user"



