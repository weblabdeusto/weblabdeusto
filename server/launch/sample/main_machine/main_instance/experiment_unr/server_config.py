#!/usr/bin/env python
#-*-*- encoding: utf-8 -*-*-

import os

secret_credentials = os.path.join(os.path.dirname(CURRENT_PATH), 'secret_credentials.py')

unr_user     = 'not configured'
unr_password = 'not configured'


if os.path.exists(secret_credentials):
    # If this file exists (ignored by .gitignore), it will use those credentials 
    # instead of "not configured"
    execfile(secret_credentials)

