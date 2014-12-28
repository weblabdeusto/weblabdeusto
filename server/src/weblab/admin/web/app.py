import os
import sys
import urlparse
import traceback

import logging
from logging.handlers import RotatingFileHandler

from sqlalchemy.orm import scoped_session, sessionmaker

from flask import Flask, request, redirect
from flask.ext.admin import Admin, BaseView, expose

if __name__ == '__main__':
    import sys
    sys.path.insert(0, '.')

from voodoo.sessions.session_id import SessionId
from weblab.core.exc import SessionNotFoundError

import weblab.core.server 
import weblab.configuration_doc as configuration_doc
from weblab.data import ValidDatabaseSessionId
from weblab.db import db

import weblab.admin.web.admin_views as admin_views
import weblab.admin.web.profile_views as profile_views

from weblab.core.wl import weblab_api

class BackView(BaseView):
    @expose()
    def index(self):
        return redirect(request.url.split('/weblab/administration')[0] + '/weblab/client')

GLOBAL_APP_INSTANCE = None

class AdministrationApplication(object):

    def __init__(self, app, cfg_manager, ups, bypass_authz = False):
        super(AdministrationApplication, self).__init__()
        import weblab.admin.web.app as app_module
        app_module.GLOBAL_APP_INSTANCE = self

        self.cfg_manager = cfg_manager
        db.initialize(cfg_manager)

        self.ups = ups

        db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=db.engine))

        files_directory = cfg_manager.get_doc_value(configuration_doc.CORE_STORE_STUDENTS_PROGRAMS_PATH)
        core_server_url  = cfg_manager.get_value( 'core_server_url', '' )
        self.script_name = urlparse.urlparse(core_server_url).path.split('/weblab')[0] or ''

        self.app = app

        ################################################
        # 
        #  Administration panel for administrators
        # 
        # 

        admin_url = '/weblab/administration/admin'
        self.admin = Admin(index_view = admin_views.HomeView(db_session, url = admin_url),name = 'WebLab-Deusto Admin', url = admin_url, endpoint = admin_url, base_template = 'weblab-master.html')

        self.admin.add_view(admin_views.UsersAddingView(db_session,  category = 'General', name = 'Add multiple users',  endpoint = 'general/multiple/users'))
        self.admin.add_view(admin_views.UsersPanel(db_session,  category = 'General', name = 'Users',  endpoint = 'general/users'))
        self.admin.add_view(admin_views.GroupsPanel(db_session, category = 'General', name = 'Groups', endpoint = 'general/groups'))
        self.admin.add_view(admin_views.AuthsPanel(db_session, category = 'General', name = 'Authentication', endpoint = 'general/auth'))

        self.admin.add_view(admin_views.UserUsedExperimentPanel(files_directory, db_session, category = 'Logs', name = 'User logs', endpoint = 'logs/users'))

        self.admin.add_view(admin_views.ExperimentCategoryPanel(db_session, category = 'Experiments', name = 'Categories',  endpoint = 'experiments/categories'))
        self.admin.add_view(admin_views.ExperimentPanel(db_session,         category = 'Experiments', name = 'Experiments', endpoint = 'experiments/experiments'))

        self.admin.add_view(admin_views.PermissionsAddingView(db_session,  category = 'Permissions', name = 'Create', endpoint = 'permissions/create'))
        self.admin.add_view(admin_views.UserPermissionPanel(db_session,  category = 'Permissions', name = 'User',   endpoint = 'permissions/user'))
        self.admin.add_view(admin_views.GroupPermissionPanel(db_session, category = 'Permissions', name = 'Group',  endpoint = 'permissions/group'))
        self.admin.add_view(admin_views.RolePermissionPanel(db_session,  category = 'Permissions', name = 'Roles',  endpoint = 'permissions/role'))

        self.admin.add_view(admin_views.MyProfileView(url = 'myprofile', name = 'My profile',  endpoint = 'myprofile/admin'))

        self.admin.add_view(BackView(url = 'back', name = 'Back',  endpoint = 'back/admin'))

        self.admin.init_app(self.app)

        self.full_admin_url = self.script_name + admin_url

        ################################################
        # 
        #  Profile panel
        # 

        profile_url = '/weblab/administration/profile'
        self.profile = Admin(index_view = profile_views.ProfileHomeView(db_session, url = profile_url, endpoint = 'profile'),name = 'WebLab-Deusto profile', url = profile_url, endpoint = profile_url, base_template = 'weblab-master.html')

        self.profile.add_view(profile_views.ProfileEditView(db_session, name = 'Edit', endpoint = 'edit'))

        self.profile.add_view(profile_views.MyAccessesPanel(files_directory, db_session,  name = 'My accesses', endpoint = 'accesses'))

        self.profile.add_view(BackView(url = 'back', name = 'Back',  endpoint = 'back/profile'))

        self.profile.init_app(self.app)

        ################################################
        # 
        #  Instructors panel
        # 
    
        # TODO. There should be able a new M2M relation between instructors and groups.
        # 
        # Instructor should be able to:
        # 
        # a) Create new groups (of which they are in charge)
        # b) Make other instructors in charge of these groups
        # c) Add students (and only students) to the system; forcing a group
        # d) Edit users (only students; of those groups that the administrator is in charge of)
        # e) Assign permissions on these courses
        # f) Manage the permissions on these courses
        # g) See the logs of their own students
        # h) See a panel with analytics of each of these groups (this panel is common to the administrator, and has not been implemented)

        ################################################
        # 
        #  Other
        # 
        self.bypass_authz = bypass_authz

    def is_admin(self):
        if self.bypass_authz:
            return True

        try:
            session_id = (request.cookies.get('weblabsessionid') or '').split('.')[0]
            with weblab_api(self.ups, session_id = session_id):
                try:
                    permissions = weblab.core.server.get_user_permissions()
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
        if self.bypass_authz:
            session_id, route = self.ups.do_reserve_session(ValidDatabaseSessionId('student1', 'administrator'))
            with weblab_api(self.ups, session_id = session_id.id):
                return weblab.core.server.get_user_permissions()

        session_id = (request.cookies.get('weblabsessionid') or '').split('.')[0]
        try:
            with weblab_api(self.ups, session_id = session_id):
                return weblab.core.server.get_user_permissions()
        except:
            traceback.print_exc()
            return None

    def get_user_information(self):
        if self.bypass_authz:
            session_id, route = self.ups.do_reserve_session(ValidDatabaseSessionId('student1', 'administrator'))
            with weblab_api(self.ups, session_id = session_id.id):
                return weblab.core.server.get_user_information()

        session_id = (request.cookies.get('weblabsessionid') or '').split('.')[0]
        try:
            with weblab_api(self.ups, session_id = session_id):
                return weblab.core.server.get_user_information()
        except SessionNotFoundError:
            return None

#############################################
# 
# The code below is only used for testing
# 

if __name__ == '__main__':
    from voodoo.configuration import ConfigurationManager
    from weblab.core.server import UserProcessingServer
    cfg_manager = ConfigurationManager()
    cfg_manager.append_path('test/unit/configuration.py')

    ups = UserProcessingServer(None, None, cfg_manager, dont_start = True)

    app = Flask('weblab.core.server')

    DEBUG = True
    admin_app = AdministrationApplication(app, cfg_manager, ups, bypass_authz = True)

    @admin_app.app.route('/')
    def index():
        return redirect('/weblab/administration/admin')

    admin_app.app.run(debug=True, host = '0.0.0.0')

