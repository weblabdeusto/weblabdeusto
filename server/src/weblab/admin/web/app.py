import os
import urlparse
import traceback

import logging
from logging.handlers import RotatingFileHandler

from sqlalchemy.orm import scoped_session, sessionmaker

from flask import Flask, request, redirect
from flask.ext.admin import Admin, BaseView, expose

from voodoo.sessions.session_id import SessionId
from weblab.core.exc import SessionNotFoundError

import weblab.configuration_doc as configuration_doc
from weblab.db.gateway import AbstractDatabaseGateway

import weblab.admin.web.admin_views as admin_views
import weblab.admin.web.profile_views as profile_views

class BackView(BaseView):
    @expose()
    def index(self):
        return redirect(request.url.split('/weblab/administration')[0] + '/weblab/client')

class AdministrationApplication(AbstractDatabaseGateway):

    INSTANCE = None

    def __init__(self, cfg_manager, ups, bypass_authz = False):

        super(AdministrationApplication, self).__init__(cfg_manager)

        self.ups = ups

        db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=self.engine))

        files_directory = cfg_manager.get_doc_value(configuration_doc.CORE_STORE_STUDENTS_PROGRAMS_PATH)
        core_server_url  = cfg_manager.get_value( 'core_server_url', '' )
        self.script_name = urlparse.urlparse(core_server_url).path.split('/weblab')[0] or ''

        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = os.urandom(32)
        self.app.config['APPLICATION_ROOT'] = self.script_name

        if os.path.exists('logs'):
            f = os.path.join('logs','admin_app.log')
        else:
            f = 'admin_app.log'
        file_handler = RotatingFileHandler(f, maxBytes = 50 * 1024 * 1024)
        file_handler.setLevel(logging.WARNING)
        self.app.logger.addHandler(file_handler)

        ################################################
        # 
        #  Administration panel for administrators
        # 
        # 

        admin_url = '/weblab/administration/admin'
        self.admin = Admin(index_view = admin_views.HomeView(db_session, url = admin_url),name = 'WebLab-Deusto Admin', url = admin_url, endpoint = admin_url)

        self.admin.add_view(admin_views.UsersPanel(db_session,  category = 'General', name = 'Users',  endpoint = 'general/users'))
        self.admin.add_view(admin_views.GroupsPanel(db_session, category = 'General', name = 'Groups', endpoint = 'general/groups'))

        self.admin.add_view(admin_views.UserUsedExperimentPanel(files_directory, db_session, category = 'Logs', name = 'User logs', endpoint = 'logs/users'))

        self.admin.add_view(admin_views.ExperimentCategoryPanel(db_session, category = 'Experiments', name = 'Categories',  endpoint = 'experiments/categories'))
        self.admin.add_view(admin_views.ExperimentPanel(db_session,         category = 'Experiments', name = 'Experiments', endpoint = 'experiments/experiments'))

        self.admin.add_view(admin_views.PermissionsAddingView(db_session,  category = 'Permissions', name = 'Create', endpoint = 'permissions/create'))
        self.admin.add_view(admin_views.UserPermissionPanel(db_session,  category = 'Permissions', name = 'User',   endpoint = 'permissions/user'))
        self.admin.add_view(admin_views.GroupPermissionPanel(db_session, category = 'Permissions', name = 'Group',  endpoint = 'permissions/group'))
        self.admin.add_view(admin_views.RolePermissionPanel(db_session,  category = 'Permissions', name = 'Roles',  endpoint = 'permissions/role'))

        self.admin.add_view(BackView(url = 'back', name = 'Back',  endpoint = 'back/admin'))

        self.admin.init_app(self.app)

        self.full_admin_url = self.script_name + admin_url

        ################################################
        # 
        #  Profile panel
        # 

        profile_url = '/weblab/administration/profile'
        self.profile = Admin(index_view = profile_views.ProfileHomeView(db_session, url = profile_url, endpoint = 'profile'),name = 'WebLab-Deusto profile', url = profile_url, endpoint = profile_url)

        self.profile.add_view(profile_views.MyAccessesPanel(files_directory, db_session,  name = 'My accesses', endpoint = 'accesses'))

        self.profile.add_view(BackView(url = 'back', name = 'Back',  endpoint = 'back/profile'))

        self.profile.init_app(self.app)

        ################################################
        # 
        #  Instructors panel
        # 
    
        # TODO

        ################################################
        # 
        #  Other
        # 
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

    def get_permissions(self):
        try:
            session_id = SessionId((request.cookies.get('weblabsessionid') or '').split('.')[0])
            return self.ups.get_user_permissions(session_id)
        except:
            traceback.print_exc()
            return None

    def get_user_information(self):
        if self.bypass_authz:
            return None # TODO

        session_id = SessionId((request.cookies.get('weblabsessionid') or '').split('.')[0])
        try:
            return self.ups.get_user_information(session_id)
        except SessionNotFoundError:
            return None

