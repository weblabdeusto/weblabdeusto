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

from flask.ext.admin import Admin
from flask.ext.admin.contrib.sqlamodel import ModelView
import wcloud.models as models

class AdministratorModelView(ModelView):

    def is_accessible(self):
        return True

    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            return redirect(request.url.split('/weblab/administration')[0] + '/weblab/client')

        return super(AdministratorModelView, self)._handle_view(name, **kwargs)


class UsersPanel(AdministratorModelView):

    column_list = ('full_name', 'email', 'active', 'token')

    can_edit   = False
    can_create = False
    can_delete = False

    def __init__(self, session, **kwargs):
        super(UsersPanel, self).__init__(models.User, session, **kwargs)


admin_url = '/admin'

# admin = Admin(index_view = admin_views.HomeView(db_session, url = admin_url),name = 'wCloud Admin', url = admin_url, endpoint = admin_url)
admin = Admin(name = 'wCloud Admin', url = admin_url, endpoint = admin_url)

admin.add_view(UsersPanel(db.session,  name = 'Users',  endpoint = 'users'))

admin.init_app(app)
