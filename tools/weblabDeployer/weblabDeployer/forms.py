# -*- coding: utf-8 -*-
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
# Author: Xabier Larrakoetxea <xabier.larrakoetxea@deusto.es>
# Author: Pablo Orduña <pablo.orduna@deusto.es>
#
# These authors would like to acknowledge the Spanish Ministry of science
# and innovation, for the support in the project IPT-2011-1558-430000
# "mCloud: http://innovacion.grupogesfor.com/web/mcloud"
#

from wtforms import Form, BooleanField, TextField, PasswordField, validators

class LoginForm(Form):
    email = TextField('Email Address', [validators.Length(min=6, max=35), validators.Email('No es un email valido')])
    password = PasswordField('New Password', [
        validators.Required(),
    ])


class RegistrationForm(Form):
    full_name = TextField('Full name', [validators.Length(min=4, max=25)])
    email = TextField('Email Address', [validators.Length(min=6, max=35), validators.Email('No es un email valido')])
    password = PasswordField('New Password', [
        validators.Required(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
    accept_tos = BooleanField('I accept the TOS', [validators.Required()]) 