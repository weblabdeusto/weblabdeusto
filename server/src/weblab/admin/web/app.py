import os
import urlparse
import traceback

import logging
from logging.handlers import RotatingFileHandler

from sqlalchemy.orm import scoped_session, sessionmaker

from flask import Flask, request
from flask.ext.admin import Admin

from voodoo.sessions.session_id import SessionId
from weblab.core.exc import SessionNotFoundError

import weblab.configuration_doc as configuration_doc
from weblab.db.gateway import AbstractDatabaseGateway

import weblab.admin.web.admin_views as admin_views

class AdministrationApplication(AbstractDatabaseGateway):

    INSTANCE = None

    def __init__(self, cfg_manager, ups, bypass_authz = False):

        super(AdministrationApplication, self).__init__(cfg_manager)

        self.ups = ups

        db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=self.engine))

        files_directory = cfg_manager.get_doc_value(configuration_doc.CORE_STORE_STUDENTS_PROGRAMS_PATH)
        core_server_url  = cfg_manager.get_value( 'core_server_url', '' )
        script_name = urlparse.urlparse(core_server_url).path.split('/weblab')[0]

        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = os.urandom(32)
        self.app.config['APPLICATION_ROOT'] = script_name

        if os.path.exists('logs'):
            f = os.path.join('logs','admin_app.log')
        else:
            f = 'admin_app.log'
        file_handler = RotatingFileHandler(f, maxBytes = 50 * 1024 * 1024)
        file_handler.setLevel(logging.WARNING)
        self.app.logger.addHandler(file_handler)

        url = '/weblab/administration/admin'
        self.admin = Admin(index_view = admin_views.HomeView(db_session, url = url),name = 'WebLab-Deusto Admin', url = url)

        self.admin.add_view(admin_views.UsersPanel(db_session,  category = 'General', name = 'Users',  endpoint = 'general/users'))
        self.admin.add_view(admin_views.GroupsPanel(db_session, category = 'General', name = 'Groups', endpoint = 'general/groups'))

        self.admin.add_view(admin_views.UserUsedExperimentPanel(files_directory, db_session, category = 'Logs', name = 'User logs', endpoint = 'logs/users'))

        self.admin.add_view(admin_views.ExperimentCategoryPanel(db_session, category = 'Experiments', name = 'Categories',  endpoint = 'experiments/categories'))
        self.admin.add_view(admin_views.ExperimentPanel(db_session,         category = 'Experiments', name = 'Experiments', endpoint = 'experiments/experiments'))

        self.admin.add_view(admin_views.PermissionTypePanel(db_session,  category = 'Permissions', name = 'Types', endpoint = 'permissions/types'))
        self.admin.add_view(admin_views.UserPermissionPanel(db_session,  category = 'Permissions', name = 'User',  endpoint = 'permissions/user'))
        self.admin.add_view(admin_views.GroupPermissionPanel(db_session, category = 'Permissions', name = 'Group', endpoint = 'permissions/group'))
        self.admin.add_view(admin_views.RolePermissionPanel(db_session,  category = 'Permissions', name = 'Roles', endpoint = 'permissions/role'))

        self.admin.init_app(self.app)

        self.bypass_authz = bypass_authz

        AdministrationApplication.INSTANCE = self

    def is_admin(self):
        if self.bypass_authz:
            return True

        try:
            session_id = SessionId((request.cookies.get('weblabsessionid') or '').split('.')[0])
            try:
                permissions = self.ups.get_user_permissions(session_id)
            except SessionNotFoundError:
                # Gotcha
                return False

            admin_permissions = [ permission for permission in permissions if permission.name == 'admin_panel_access' ]
            if len(admin_permissions) == 0:
                return False

            if admin_permissions[0].parameters[0].value:
                return True

            return False
        except:
            traceback.print_exc()
            return False

