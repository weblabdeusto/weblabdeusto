from __future__ import print_function, unicode_literals
import os
import sys
import six
import urlparse
import traceback

from sqlalchemy.orm import scoped_session, sessionmaker

import flask
from flask import Flask, request, redirect, escape, url_for
from flask.ext.admin import Admin
from flask.ext.admin.menu import MenuLink

if __name__ == '__main__':
    sys.path.insert(0, '.')

from weblab.core.exc import SessionNotFoundError

import weblab.core.server 
from weblab.core.i18n import lazy_gettext
import weblab.configuration_doc as configuration_doc
from weblab.data import ValidDatabaseSessionId
from weblab.db import db

import weblab.admin.web as web
import weblab.admin.web.admin_views as admin_views
import weblab.admin.web.profile_views as profile_views
import weblab.admin.web.instructor_views as instructor_views

from weblab.core.wl import weblab_api

from flask.json import JSONEncoder
from speaklater import is_lazy_string

class CustomJSONEncoder(JSONEncoder):
    """ Use a JSON encoder that allows you to use lazy_gettext as key in dictionaries.

    Based on http://blog.miguelgrinberg.com/post/using-flask-babel-with-flask-010

    But applying also the same pattern to the encode() method. Reason: as of Flask-Admin 1.2.0 (and earlier
    versions), when applying lazy_strings to column_labels, it uses them as key in a dictionary, and using 
    default() is not enough, so it fails. With this encoder, it recreates the dictionary (using OrderedDict
    or whatever required) when encoding.
    """
    def default(self, obj):
        if is_lazy_string(obj):
            try:
                return unicode(obj)  # python 2
            except NameError:
                return str(obj)  # python 3
        return super(CustomJSONEncoder, self).default(obj)

    def encode(self, obj, *args, **kwargs):
        if isinstance(obj, dict):
            new_obj = type(obj)()
            for key, value in six.iteritems(obj):
                if is_lazy_string(key):
                    try:
                        key = unicode(key)
                    except NameError:
                        key = str(key)
                new_obj[key] = value
            obj = new_obj 
        return super(JSONEncoder, self).encode(obj, *args, **kwargs)

class AdministrationApplication(object):

    def __init__(self, app, cfg_manager, core_server, bypass_authz = False):
        super(AdministrationApplication, self).__init__()
        app.json_encoder = CustomJSONEncoder
        
        self.cfg_manager = cfg_manager
        pub_directory = os.path.join(os.path.abspath(self.cfg_manager.get('deployment_dir', '')), 'pub')
        self.config = cfg_manager
        db.initialize(cfg_manager)

        self.core_server = core_server

        db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=db.engine))

        files_directory = cfg_manager.get_doc_value(configuration_doc.CORE_STORE_STUDENTS_PROGRAMS_PATH)
        core_server_url  = cfg_manager.get_value( 'core_server_url', '' )
        self.script_name = urlparse.urlparse(core_server_url).path.split('/weblab')[0] or ''

        self.app = app

        static_folder = os.path.abspath(os.path.join(os.path.dirname(web.__file__), 'static'))

        # Not allowed
        @app.route('/weblab/not_allowed')
        def not_allowed():
            return "You are logged in, but not allowed to see this content. Please log in with a proper account"

        # Back
        @app.route('/weblab/back')
        def back_to_client():
            return redirect(url_for('core_webclient.labs'))
   
        ################################################
        # 
        #  Administration panel for administrators
        # 
        # 

        admin_url = '/weblab/admin'
        category_system = lazy_gettext("System")
        category_users = lazy_gettext("Users")
        category_logs = lazy_gettext("Logs")
        category_experiments = lazy_gettext("Experiments")
        category_permissions = lazy_gettext("Permissions")
        self.admin = Admin(index_view = admin_views.HomeView(db_session, url = admin_url),name = lazy_gettext('WebLab-Deusto Admin'), url = admin_url, endpoint = admin_url, base_template = 'weblab-master.html', template_mode = 'bootstrap3')
        self.admin.weblab_admin_app = self

        self.admin.add_view(admin_views.SystemProperties(db_session, category = category_system, name = lazy_gettext('Settings'), endpoint = 'system/settings', url='settings'))
        self.admin.add_view(admin_views.AuthsPanel(db_session, category = category_system, name = lazy_gettext('Authentication'), endpoint = 'system/auth', url='auth'))
        if not os.path.exists(pub_directory):
            try:
                os.mkdir(pub_directory)
            except (IOError, OSError) as e:
                print("WARNING: %s not found. Create it to upload files to it." % pub_directory)
                    
        if os.path.exists(pub_directory):
            self.admin.add_view(admin_views.AdministratorFileAdmin(pub_directory, category = category_system, name = lazy_gettext('Public directory'), endpoint = 'system/pub', url='pub'))

        self.admin.add_view(admin_views.UsersAddingView(db_session,  category = category_users, name = lazy_gettext('Add multiple users'),  endpoint = 'users/multiple'))
        self.admin.add_view(admin_views.UsersPanel(db_session,  category = category_users, name = lazy_gettext('Users'),  endpoint = 'users/users', url='users'))
        self.admin.add_view(admin_views.GroupsPanel(db_session, category = category_users, name = lazy_gettext('Groups'), endpoint = 'users/groups', url='groups'))

        self.admin.add_view(admin_views.UserUsedExperimentPanel(files_directory, db_session, category = category_logs, name = lazy_gettext('User logs'), endpoint = 'logs/users', url='logs'))

        self.admin.add_view(admin_views.ExperimentCategoryPanel(db_session, category = category_experiments, name = lazy_gettext('Categories'),  endpoint = 'experiments/categories', url='experiments/categories'))
        self.admin.add_view(admin_views.ExperimentPanel(db_session,         category = category_experiments, name = lazy_gettext('Experiments'), endpoint = 'experiments/experiments', url='experiments'))
        # TODO: Until finished, do not display
        # self.admin.add_view(admin_views.SchedulerPanel(db_session,         category = category_experiments, name = lazy_gettext('Schedulers'), endpoint = 'experiments/schedulers'))

        self.admin.add_view(admin_views.PermissionsAddingView(db_session,  category = category_permissions, name = lazy_gettext('Create'), endpoint = 'permissions/create', url='permissions'))
        self.admin.add_view(admin_views.UserPermissionPanel(db_session,  category = category_permissions, name = lazy_gettext('User'),   endpoint = 'permissions/user'))
        self.admin.add_view(admin_views.GroupPermissionPanel(db_session, category = category_permissions, name = lazy_gettext('Group'),  endpoint = 'permissions/group'))
        self.admin.add_view(admin_views.RolePermissionPanel(db_session,  category = category_permissions, name = lazy_gettext('Roles'),  endpoint = 'permissions/role'))

        self.admin.add_link(MenuLink(endpoint='instructor.index', name = lazy_gettext('Instructor panel'), icon_type='glyph', icon_value='glyphicon-stats'))
        self.admin.add_link(MenuLink(endpoint='profile.index', name = lazy_gettext('My profile'), icon_type='glyph', icon_value='glyphicon-user'))
        self.admin.add_link(MenuLink(endpoint = 'back_to_client', name = lazy_gettext('Back'), icon_type='glyph', icon_value='glyphicon-log-out'))

        self.admin.init_app(self.app)

        self.full_admin_url = self.script_name + admin_url

        ################################################
        # 
        #  Profile panel
        # 

        profile_url = '/weblab/profile'
        self.profile = Admin(index_view = profile_views.ProfileHomeView(db_session, url = profile_url, endpoint = 'profile'),name = lazy_gettext('WebLab-Deusto profile'), url = profile_url, endpoint = profile_url, base_template = 'weblab-master.html', template_mode='bootstrap3')
        self.profile.weblab_admin_app = self

        self.profile.add_view(profile_views.ProfileEditView(db_session, name = lazy_gettext('Edit'), endpoint = 'edit'))

        self.profile.add_view(profile_views.MyAccessesPanel(files_directory, db_session,  name = lazy_gettext('My accesses'), endpoint = 'accesses'))
        self.profile.add_link(MenuLink(endpoint = 'back_to_client', name = lazy_gettext('Back'), icon_type='glyph', icon_value='glyphicon-log-out'))

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

        instructor_url = '/weblab/instructor'
        instructor_home = instructor_views.InstructorHomeView(db_session, url = instructor_url, endpoint = 'instructor')
        instructor_home.static_folder = static_folder
        self.instructor = Admin(index_view = instructor_home, name = lazy_gettext("Weblab-Deusto instructor"), url = instructor_url, endpoint = instructor_url, base_template = 'weblab-master.html', template_mode='bootstrap3')
        self.instructor.weblab_admin_app = self
        
        category_general = lazy_gettext("General")
        category_stats = lazy_gettext("Stats")
        self.instructor.add_view(instructor_views.UsersPanel(db_session, category = category_general, name = lazy_gettext('Users'), endpoint = 'users'))
        self.instructor.add_view(instructor_views.GroupsPanel(db_session, category = category_general, name = lazy_gettext('Groups'), endpoint = 'groups'))
        self.instructor.add_view(instructor_views.UserUsedExperimentPanel(db_session, category = category_general, name = lazy_gettext('Raw accesses'), endpoint = 'logs'))

        self.instructor.add_view(instructor_views.GroupStats(db_session, category = category_stats, name = lazy_gettext('Group'), endpoint = 'stats/groups'))
        self.instructor.add_link(MenuLink(endpoint='profile.index', name = lazy_gettext('My profile'), icon_type='glyph', icon_value='glyphicon-user'))
        self.instructor.add_link(MenuLink(endpoint = 'back_to_client', name = lazy_gettext('Back'), icon_type='glyph', icon_value='glyphicon-log-out'))

        self.instructor.init_app(self.app)

        ################################################
        # 
        #  Other
        # 
        self.bypass_authz = bypass_authz

    @property
    def db(self):
        return self.core_server.db

    def get_db(self):
        return self.core_server.db

    def is_admin(self):
        if self.bypass_authz:
            return True

        try:
            session_id = (request.cookies.get('weblabsessionid') or '').split('.')[0]
            if not session_id:
                return False
            
            with weblab_api(self.core_server, session_id = session_id):
                is_admin = weblab_api.is_admin
            
            return is_admin
        except:
            traceback.print_exc()
            return False

    def get_user_role(self):
        if self.bypass_authz:
            return 'admin'

        try:
            session_id = (request.cookies.get('weblabsessionid') or '').split('.')[0]
            if session_id:
                try:
                    with weblab_api(self.core_server, session_id = session_id):
                        user_info = weblab.core.server.get_user_information()
                except SessionNotFoundError:
                    # Gotcha
                    traceback.print_exc()
                else:
                    return user_info.role.name
            return None
        except:
            traceback.print_exc()
            return None

    def _reserve_fake_session(self):
        fake_names = ('student1', 'porduna', 'user7', 'admin')
        exc = None
        for fake_name in fake_names:
            try:
                session_id, route = self.core_server._reserve_session(ValidDatabaseSessionId(fake_name, 'administrator'))
            except Exception as exc:
                pass
            else:
                return session_id, route
        raise exc

    def get_permissions(self):
        if self.bypass_authz:
            session_id, _ = self._reserve_fake_session()
            with weblab_api(self.core_server, session_id = session_id.id):
                return weblab.core.server.get_user_permissions()

        session_id = (request.cookies.get('weblabsessionid') or '').split('.')[0]
        if session_id:
            try:
                with weblab_api(self.core_server, session_id = session_id):
                    return weblab.core.server.get_user_permissions()
            except:
                traceback.print_exc()
        return None

    def get_user_information(self):
        if self.bypass_authz:
            session_id, _ = self._reserve_fake_session()
            with weblab_api(self.core_server, session_id = session_id.id):
                return weblab.core.server.get_user_information()

        session_id = (request.cookies.get('weblabsessionid') or '').split('.')[0]
        if session_id:
            try:
                with weblab_api(self.core_server, session_id = session_id):
                    return weblab.core.server.get_user_information()
            except SessionNotFoundError:
                pass
        return None


#############################################
# 
# The code below is only used for testing
# 

if __name__ == '__main__':
    from voodoo.configuration import ConfigurationManager
    from weblab.core.server import UserProcessingServer
    from weblab.core.i18n import initialize_i18n
    from flask_debugtoolbar import DebugToolbarExtension

    cfg_manager = ConfigurationManager()
    cfg_manager.append_path('test/unit/configuration.py')

    ups = UserProcessingServer(None, None, cfg_manager, dont_start = True)

    app = Flask('weblab.core.server')
    app.config['SECRET_KEY'] = os.urandom(32)
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
    app.config['DEBUG'] = True

    @app.route("/site-map")
    def site_map():
        lines = []
        for rule in app.url_map.iter_rules():
            line = str(escape(repr(rule)))
            lines.append(line)

        ret = "<br>".join(lines)
        return ret

    admin_app = AdministrationApplication(app, cfg_manager, ups, bypass_authz = True)

    @admin_app.app.route('/')
    def index():
        return redirect('/weblab/admin')
    
    initialize_i18n(app)

    toolbar = DebugToolbarExtension()
    toolbar.init_app(app)

    print("Open: http://localhost:5000/weblab/admin/")
    app.run(debug=True, host='0.0.0.0')

