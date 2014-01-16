import os
import urlparse
import traceback

import logging
from logging.handlers import RotatingFileHandler

from sqlalchemy.orm import scoped_session, sessionmaker

from flask import Flask, request, redirect, url_for
from flask.ext.admin import Admin, BaseView, expose

from voodoo.sessions.session_id import SessionId
from weblab.core.exc import SessionNotFoundError

import weblab.configuration_doc as configuration_doc
import weblab.db.session as DbSession
from weblab.db.gateway import AbstractDatabaseGateway

import weblab.admin.web as web
import weblab.admin.web.admin_views as admin_views
import weblab.admin.web.profile_views as profile_views
import weblab.admin.web.instructor_views as instructor_views

class BackView(BaseView):
    @expose()
    def index(self):
        return redirect(request.url.split('/weblab/administration')[0] + '/weblab/client')

class RedirectView(BaseView):
    def __init__(self, url_token, *args, **kwargs):
        self.url_token = url_token
        super(RedirectView, self).__init__(*args, **kwargs)

    @expose()
    def index(self):
        return redirect(url_for(self.url_token))

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
        self.app.config['SESSION_COOKIE_PATH'] = self.script_name + '/weblab/'
        self.app.config['SESSION_COOKIE_NAME'] = 'weblabsession'

        if os.path.exists('logs'):
            f = os.path.join('logs','admin_app.log')
        else:
            f = 'admin_app.log'
        file_handler = RotatingFileHandler(f, maxBytes = 50 * 1024 * 1024)
        file_handler.setLevel(logging.WARNING)
        self.app.logger.addHandler(file_handler)

        static_folder = os.path.abspath(os.path.join(os.path.dirname(web.__file__), 'static'))

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

        self.admin.add_view(admin_views.UserUsedExperimentPanel(files_directory, db_session, category = 'Logs', name = 'User logs', endpoint = 'logs/users'))

        self.admin.add_view(admin_views.ExperimentCategoryPanel(db_session, category = 'Experiments', name = 'Categories',  endpoint = 'experiments/categories'))
        self.admin.add_view(admin_views.ExperimentPanel(db_session,         category = 'Experiments', name = 'Experiments', endpoint = 'experiments/experiments'))
        self.admin.add_view(admin_views.SchedulerPanel(db_session,         category = 'Experiments', name = 'Schedulers', endpoint = 'experiments/schedulers'))

        self.admin.add_view(admin_views.PermissionsAddingView(db_session,  category = 'Permissions', name = 'Create', endpoint = 'permissions/create'))
        self.admin.add_view(admin_views.UserPermissionPanel(db_session,  category = 'Permissions', name = 'User',   endpoint = 'permissions/user'))
        self.admin.add_view(admin_views.GroupPermissionPanel(db_session, category = 'Permissions', name = 'Group',  endpoint = 'permissions/group'))
        self.admin.add_view(admin_views.RolePermissionPanel(db_session,  category = 'Permissions', name = 'Roles',  endpoint = 'permissions/role'))

        self.admin.add_view(RedirectView('instructor.index', url = 'instructor', name = 'Instructor panel',  endpoint = 'instructor/admin'))
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

        instructor_url = '/weblab/administration/instructor'
        instructor_home = instructor_views.InstructorHomeView(db_session, url = instructor_url, endpoint = 'instructor')
        instructor_home.static_folder = static_folder
        self.instructor = Admin(index_view = instructor_home, name = "Weblab-Deusto instructor", url = instructor_url, endpoint = instructor_url, base_template = 'weblab-master.html')
        
        self.instructor.add_view(instructor_views.UsersPanel(db_session, category = 'General', name = 'Users', endpoint = 'users'))
        self.instructor.add_view(instructor_views.GroupsPanel(db_session, category = 'General', name = 'Groups', endpoint = 'groups'))
        self.instructor.add_view(instructor_views.UserUsedExperimentPanel(db_session, category = 'General', name = 'Raw accesses', endpoint = 'logs'))

        self.instructor.add_view(instructor_views.GroupStats(db_session, category = 'Stats', name = 'Group', endpoint = 'stats/groups'))

        self.instructor.add_view(BackView(url = 'back', name = 'Back',  endpoint = 'back/instructor'))

        self.instructor.init_app(self.app)

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

    def get_user_role(self):
        if self.bypass_authz:
            return 'admin'

        try:
            session_id = SessionId((request.cookies.get('weblabsessionid') or '').split('.')[0])
            try:
                user_info = self.ups.get_user_information(session_id)
            except SessionNotFoundError:
                # Gotcha
                return None
            else:
                user_info.role.name
        except:
            traceback.print_exc()
            return None

    def get_permissions(self):
        if self.bypass_authz:
            try:
                session_id, route = self.ups.do_reserve_session(DbSession.ValidDatabaseSessionId('student1', 'administrator'))
            except:
                try:
                    session_id, route = self.ups.do_reserve_session(DbSession.ValidDatabaseSessionId('porduna', 'administrator'))
                except:
                    session_id = "foo"
                if session_id == "foo":
                    raise
            return self.ups.get_user_permissions(session_id.id)

        try:
            session_id = SessionId((request.cookies.get('weblabsessionid') or '').split('.')[0])
            return self.ups.get_user_permissions(session_id)
        except:
            traceback.print_exc()
            return None

    def get_user_information(self):
        if self.bypass_authz:
            try:
                session_id, route = self.ups.do_reserve_session(DbSession.ValidDatabaseSessionId('student1', 'administrator'))
            except:
                try:
                    session_id, route = self.ups.do_reserve_session(DbSession.ValidDatabaseSessionId('porduna', 'administrator'))
                except:
                    session_id = "foo"
                if session_id == "foo":
                    raise
            return self.ups.get_user_information(session_id.id)

        session_id = SessionId((request.cookies.get('weblabsessionid') or '').split('.')[0])
        try:
            return self.ups.get_user_information(session_id)
        except SessionNotFoundError:
            return None

