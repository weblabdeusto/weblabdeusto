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

from wcloud import app, db

from flask import session, redirect, url_for, request
from flask.ext.admin import Admin, AdminIndexView
from flask.ext.admin.contrib.sqlamodel import ModelView
import wcloud.models as models

databases_per_port = app.config['REDIS_DBS_PER_PORT']
initial_redis_port = app.config['REDIS_START_PORT']

def is_accessible():
    logged_in  = session.get('logged_in', False)
    user_email = session.get('user_email', 'not provided') 
    administrators = app.config.get('ADMINISTRATORS', ())

    print logged_in, user_email, administrators

    return logged_in and user_email in administrators

class AdministratorModelView(ModelView):

    def is_accessible(self):
        return is_accessible()

    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            return redirect(url_for('login', next=request.url))

        return super(AdministratorModelView, self)._handle_view(name, **kwargs)

class HomeView(AdminIndexView):

    def is_accessible(self):
        return is_accessible()

    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            return redirect(url_for('login', next=request.url))

        return super(HomeView, self)._handle_view(name, **kwargs)


class UsersPanel(AdministratorModelView):

    column_list = ('full_name', 'email', 'active', 'token.token', 'entity.name', 'entity.base_url')

    can_edit   = False
    can_create = False
    can_delete = False

    def __init__(self, session, **kwargs):
        super(UsersPanel, self).__init__(models.User, session, **kwargs)

class TokensPanel(AdministratorModelView):

    column_list = ('token', 'date','user.full_name', 'user.email','user.active')

    can_edit   = False
    can_create = False
    can_delete = False

    def __init__(self, session, **kwargs):
        super(TokensPanel, self).__init__(models.Token, session, **kwargs)

class EntitiesPanel(AdministratorModelView):

    column_list = ('name', 'user.full_name', 'user.email', 'link_url','base_url','start_port_number','end_port_number','deployed', 'mysql', 'redis port', 'redis db')

    column_formatters = {
        'mysql' : lambda c, e, p: 'wcloud%s' % e.id,
        'redis port' : lambda c, e, p: initial_redis_port + e.id / databases_per_port,
        'redis db'   : lambda c, e, p: e.id % databases_per_port,
    }

    can_edit   = False
    can_create = False
    can_delete = False

    def __init__(self, session, **kwargs):
        super(EntitiesPanel, self).__init__(models.Entity, session, **kwargs)


admin_url = '/admin'

admin = Admin(app, index_view = HomeView(), name = 'wCloud Admin')

admin.add_view(UsersPanel(db.session,  name = 'Users',  endpoint = 'users'))
admin.add_view(TokensPanel(db.session,  name = 'Tokens',  endpoint = 'tokens'))
admin.add_view(EntitiesPanel(db.session,  name = 'Entities',  endpoint = 'entities'))

