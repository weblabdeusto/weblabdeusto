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

from flask.ext.wtf import Form, BooleanField, TextField, PasswordField, FileField, validators, file_allowed, ValidationError

from flask.ext.uploads import UploadSet, IMAGES
from wcloud.models import User, Entity
from flask import session

class DisabledTextField(TextField):
    def __call__(self, *args, **kwargs):
        new_kwargs = kwargs.copy()
        new_kwargs['readonly'] = 'true'
        return super(DisabledTextField, self).__call__(*args, **new_kwargs)

#Validators
class UserExists(object):
    def __init__(self, message=None):
        if not message:
            message = u"User already exists"
        self.message = message

    def __call__(self, form, field):
        if User.user_exists(field.data):
            raise validators.ValidationError(self.message)

class BaseURLExists(object):
    def __init__(self, message=None):
        if not message:
            message = u"Base url already exists"
        self.message = message

    def __call__(self, form, field):
        if Entity.url_exists(session['user_email'], field.data):
            raise validators.ValidationError(self.message)


#Forms
class LoginForm(Form):
    email = TextField('Email Address', [validators.Length(min=6, max=35),
                        validators.Email()])
    password = PasswordField('New Password', [
        validators.Required(),
    ])


class RegistrationForm(Form):
    full_name = TextField('Full name', [validators.Length(min=4, max=25)])
    email = TextField('Email Address', [validators.Length(min=6, max=35),
                                validators.Email(),
                                UserExists('User already exists')])
    password = PasswordField('New Password', [
        validators.Required(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
#    accept_tos = BooleanField('I accept the TOS', [validators.Required()])
    

images = UploadSet("images", IMAGES)

class ConfigurationForm(Form):
    name = TextField('Institution name', [validators.Length(min=4, max=100)], description = "Example: University of Deusto")
    logo = FileField('Institution logo', validators=[ file_allowed(images, "Images only")])
    base_url = TextField('Base url', [validators.Length(min=4, max=100),
                                validators.Regexp('^[\w-]+$'),
                                BaseURLExists('Base url already exists')], 
                                description = "Example: deusto")
    link_url = TextField('Link url', [validators.Length(min=4, max=100),
                                validators.Regexp('^http:\/\/(\w|-|\.|\/)+$')],
                                description ="Example: http://www.deusto.es/")
    google_analytics_number = TextField('Google analytics number', description="Optional. Example: UA-12576838-6")

class DisabledConfigurationForm(Form):
    name = DisabledTextField('Institution name', [validators.Length(min=4, max=100)], description = "Example: University of Deusto")
    base_url = DisabledTextField('Base url', [validators.Length(min=4, max=100),
                                validators.Regexp('^[\w-]+$'),
                                BaseURLExists('Base url already exists')], 
                                description = "Example: deusto")
    link_url = DisabledTextField('Link url', [validators.Length(min=4, max=100),
                                validators.Regexp('^http:\/\/(\w|-|\.|\/)+$')],
                                description ="Example: http://www.deusto.es/")
    google_analytics_number = DisabledTextField('Google analytics number', description="Optional. Example: UA-12576838-6")



class DeployForm(Form):
    admin_name = TextField('Admin name', [validators.Length(min=4, max=100)])
    admin_user = TextField('Admin user', [validators.Length(min=4, max=100)])
    admin_password = PasswordField('Admin password', [validators.Length(min=4, max=100)])
    admin_email = TextField('Admin email', [validators.Length(min=4, max=100),
                                validators.Email()])
    
    def validate_characters(form, field): # XXX work around to avoid problems with UTF-8
        for c in field.data:
            if c.lower() not in 'abcdefghijklmnopqrstuvwxyz0123456789._-@ ':
                raise ValidationError("Invalid characters found")
        
    validate_admin_name     = validate_characters
    validate_admin_user     = validate_characters
    validate_admin_password = validate_characters
    validate_admin_email    = validate_characters

