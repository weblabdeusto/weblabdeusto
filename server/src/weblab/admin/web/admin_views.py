import os
import sha
import time
import random
import threading

from wtforms.fields import PasswordField
from wtforms.validators import Email

from flask import Markup, request, redirect, abort, url_for, flash, Response

from flask.ext.admin.contrib.sqlamodel import ModelView
from flask.ext.admin import expose, AdminIndexView, BaseView
from flask.ext.admin.model.form import InlineFormAdmin

import weblab.configuration_doc as configuration_doc
import weblab.db.model as model
from weblab.admin.web.filters import get_filter_number, generate_filter_any

def get_app_instance():
    import weblab.admin.web.app as admin_app
    return admin_app.AdministrationApplication.INSTANCE

class AdministratorView(BaseView):

    def is_accessible(self):
        return get_app_instance().is_admin()

    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            return redirect(request.url.split('/weblab/administration')[0] + '/weblab/client')

        return super(AdministratorView, self)._handle_view(name, **kwargs)


class AdministratorModelView(ModelView):

    def is_accessible(self):
        return get_app_instance().is_admin()

    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            return redirect(request.url.split('/weblab/administration')[0] + '/weblab/client')

        return super(AdministratorModelView, self)._handle_view(name, **kwargs)


    # 
    # TODO XXX FIXME: This may be a bug. However, whenever this is commented,
    # Flask-Admin does this:
    #
    #       # Auto join
    #       for j in self._auto_joins:
    #                   query = query.options(subqueryload(j))
    # 
    # And some (weird) results in UserUsedExperiment are not shown, while other yes
    # 
    def scaffold_auto_joins(self):
        return []

SAME_DATA = object()

def show_link(klass, filter_name, field, name, view = 'View'):

    script_name = get_app_instance().script_name
    instance      = klass.INSTANCE
    url           = script_name + instance.url

    link = u'<a href="%s?' % url

    if isinstance(filter_name, basestring):
        filter_numbers = [ getattr(instance, u'%s_filter_number' % filter_name) ]
    else:
        filter_numbers = [ getattr(instance, u'%s_filter_number' % fname) for fname in filter_name]

    if isinstance(name, basestring):
        names = [name]
    else:
        names = name

    for pos, (filter_number, name) in enumerate(zip(filter_numbers, names)):
        if '.' not in name:
            data = getattr(field, name)
        else:
            variables = name.split('.')
            current = field
            data = None
            for variable in variables:
                current = getattr(current, variable)
                if current is None:
                    data = ''
                    break
            if data is None:
                data = current
        link += u'flt%s_%s=%s&' % (pos + 1, filter_number, data)

    if view == SAME_DATA:
        view = data

    link = link[:-1] + u'">%s</a>' % view

    return Markup(link)
   
class UserAuthForm(InlineFormAdmin):
    def postprocess_form(self, form_class):
        form_class.configuration = PasswordField('configuration', description = 'Detail the password (DB), Facebook ID -the number- (Facebook), OpenID identifier.')
        return form_class

class UsersPanel(AdministratorModelView):

    column_list = ('role', 'login', 'full_name', 'email', 'groups', 'logs', 'permissions')
    column_searchable_list = ('full_name', 'login')
    column_filters = ( 'full_name', 'login','role', 'email'
                    ) + generate_filter_any(model.DbGroup.name.property.columns[0], 'Group', model.DbUser.groups)


    form_excluded_columns = 'avatar',
    form_args = dict(email = dict(validators = [Email()]) )

    column_descriptions = dict( login     = 'Username (all letters, dots and numbers)', 
                                full_name ='First and Last name',
                                email     = 'Valid e-mail address',
                                avatar    = 'Not implemented yet, it should be a public URL for a user picture.' )

    inline_models = (UserAuthForm(model.DbUserAuth),)

    column_formatters = dict(
                            role        = lambda c, u, p: show_link(UsersPanel,              'role', u, 'role.name', SAME_DATA),
                            groups      = lambda c, u, p: show_link(GroupsPanel,             'user', u, 'login'),
                            logs        = lambda c, u, p: show_link(UserUsedExperimentPanel, 'user', u, 'login'),
                            permissions = lambda c, u, p: show_link(UserPermissionPanel,     'user', u, 'login'),
                        )

    INSTANCE = None

    def __init__(self, session, **kwargs):
        super(UsersPanel, self).__init__(model.DbUser, session, **kwargs)
        self.login_filter_number = get_filter_number(self, u'User.login')
        self.group_filter_number = get_filter_number(self, u'Group.name')
        self.role_filter_number  = get_filter_number(self, u'Role.name')

        self.local_data = threading.local()

        UsersPanel.INSTANCE = self

    def edit_form(self, obj = None):
        form = super(UsersPanel, self).edit_form(obj)
        self.local_data.authentications = {}
        if obj is not None:
            for auth_instance in obj.auths:
                self.local_data.authentications[auth_instance.id] = (auth_instance.auth.name, auth_instance.configuration)
        return form

    def on_model_change(self, form, user_model):
        auths = set()
        for auth_instance in user_model.auths:
            if auth_instance.auth in auths:
                raise Exception("You can not have two equal auth types (of type %s)" % auth_instance.auth.name)
            else:
                auths.add(auth_instance.auth)
               
                if hasattr(self.local_data, 'authentications'):

                    old_auth_type, old_auth_conf = self.local_data.authentications.get(auth_instance.id, (None, None))
                    if old_auth_type == auth_instance.auth.name and old_auth_conf == auth_instance.configuration:
                        # Same as before: ignore
                        print "Ignoring: same name"
                        continue

                    if not auth_instance.configuration:
                        # User didn't do anything here. Restoring configuration.
                        auth_instance.configuration = old_auth_conf or ''
                        print "Restoring config"
                        continue

                self._on_auth_changed(auth_instance)
                    

    def _on_auth_changed(self, auth_instance):
        print "New auth!", auth_instance
        if auth_instance.auth.auth_type.name.lower() == 'db':
            password = auth_instance.configuration
            if len(password) < 6:
                raise Exception("Password too short")
            auth_instance.configuration = self._password2sha(password)
            print "Stored:", auth_instance.configuration
        elif auth_instance.auth.auth_type.name.lower() == 'facebook':
            try:
                int(auth_instance.configuration)
            except:
                raise Exception("Use a numeric ID for Facebook")
        # Other validations would be here


    def _password2sha(self, password):
        randomstuff = ""
        for _ in range(4):
            c = chr(ord('a') + random.randint(0,25))
            randomstuff += c
        password = password if password is not None else ''
        return randomstuff + "{sha}" + sha.new(randomstuff + password).hexdigest()

class GroupsPanel(AdministratorModelView):

    column_searchable_list = ('name',)
    column_list = ('name','parent', 'users','permissions')

    column_filters = ( ('name',) 
                        + generate_filter_any(model.DbUser.login.property.columns[0], 'User login', model.DbGroup.users)
                        + generate_filter_any(model.DbUser.full_name.property.columns[0], 'User name', model.DbGroup.users)
                    )

    column_formatters = dict(
                            users       = lambda c, g, p: show_link(UsersPanel,           'group', g, 'name'),
                            permissions = lambda c, g, p: show_link(GroupPermissionPanel, 'group', g, 'name'),
                        )

    INSTANCE = None

    def __init__(self, session, **kwargs):
        super(GroupsPanel, self).__init__(model.DbGroup, session, **kwargs)

        self.user_filter_number  = get_filter_number(self, u'User.login')

        GroupsPanel.INSTANCE = self

class UserUsedExperimentPanel(AdministratorModelView):

    column_auto_select_related = True
    column_select_related_list = ('user',)
    can_delete = False
    can_edit   = False
    can_create = False

    column_searchable_list = ('origin',)
    column_sortable_list = ('UserUsedExperiment.id', ('user', model.DbUser.login), ('experiment',  model.DbExperiment.id), 'start_date', 'end_date', 'origin', 'coord_address')
    column_list    = ( 'user', 'experiment', 'start_date', 'end_date', 'origin', 'coord_address','details')
    column_filters = ( 'user', 'start_date', 'end_date', 'experiment', 'origin', 'coord_address')

    column_formatters = dict(
                    user       = lambda c, uue, p: show_link(UsersPanel, 'login', uue, 'user.login', SAME_DATA),
                    experiment = lambda c, uue, p: show_link(ExperimentPanel, ('name', 'category'), uue, ('experiment.name', 'experiment.category.name'), uue.experiment ),
                    details    = lambda c, uue, p: Markup('<a href="%s">Details</a>' % (url_for('.detail', id=uue.id))),
                )

    action_disallowed_list = ['create','edit','delete']

    INSTANCE = None

    def __init__(self, files_directory, session, **kwargs):
        super(UserUsedExperimentPanel, self).__init__(model.DbUserUsedExperiment, session, **kwargs)

        self.files_directory     = files_directory
        self.user_filter_number  = get_filter_number(self, u'User.login')
        self.experiment_filter_number  = get_filter_number(self, u'Experiment.name')
        # self.experiment_category_filter_number  = get_filter_number(self, u'Category.name')

        UserUsedExperimentPanel.INSTANCE = self

    def get_list(self, page, sort_column, sort_desc, search, filters, *args, **kwargs):
        # So as to sort descending, force sorting by 'id' and reverse the sort_desc
        if sort_column is None:
            sort_column = 'id'
            sort_desc   = not sort_desc
        return super(UserUsedExperimentPanel, self).get_list(page, sort_column, sort_desc, search, filters, *args, **kwargs)

    @expose('/details/<int:id>')
    def detail(self, id):
        uue = self.get_query().filter_by(id = id).first()
        if uue is None:
            return abort(404)

        properties = {}
        for prop in uue.properties:
            properties[prop.property_name.name] = prop.value

        return self.render("details.html", uue = uue, properties = properties)

    @expose('/interactions/<int:id>')
    def interactions(self, id):
        uue = self.get_query().filter_by(id = id).first()

        if uue is None:
            return abort(404)

        interactions = []

        for command in uue.commands:
            timestamp = time.mktime(command.timestamp_before.timetuple()) + 1e-6 * command.timestamp_before_micro
            interactions.append((timestamp, True, command))

        for f in uue.files:
            timestamp = time.mktime(f.timestamp_before.timetuple()) + 1e-6 * f.timestamp_before_micro
            interactions.append((timestamp, False, f))

        interactions.sort(lambda (x1, x2, x3), (y1, y2, y3) : cmp(x1, y1))

        return self.render("interactions.html", uue = uue, interactions = interactions, unicode = unicode)

    def get_file(self, id):
        return self.session.query(model.DbUserFile).filter_by(id = id).first()

    @expose('/files/<int:id>')
    def files(self, id):
        uf = self.get_file(id)
        if uf is None:
            return abort(404)

        if 'not stored' in uf.file_sent:
            flash("File not stored")
            return self.render("error.html", message = "The file has not been stored. Check the %s configuration value." % configuration_doc.CORE_STORE_STUDENTS_PROGRAMS)
        
        file_path = os.path.join(self.files_directory, uf.file_sent)
        if os.path.exists(file_path):
            content = open(file_path).read()
            return Response(content, headers = {'Content-Type' : 'application/octstream', 'Content-Disposition' : 'attachment; filename=file_%s.bin' % id})
        else:
            if os.path.exists(self.files_directory):
                flash("Wrong configuration or file deleted")
                return self.render("error.html", message = "The file was stored, but now it is not reachable. Check the %s property." % configuration_doc.CORE_STORE_STUDENTS_PROGRAMS_PATH)
            else:
                flash("Wrong configuration")
                return self.render("error.html", message = "The file was stored, but now it is not reachable. The %s directory does not exist." % configuration_doc.CORE_STORE_STUDENTS_PROGRAMS_PATH)


class ExperimentCategoryPanel(AdministratorModelView):
   
    column_searchable_list = ('name',)
    column_list    = ('name', 'experiments')
    column_filters = ( 'name', ) 

    column_formatters = dict(
                    experiments = lambda co, c, p: show_link(ExperimentPanel, 'category', c, 'name')
                )

    INSTANCE = None

    def __init__(self, session, **kwargs):
        super(ExperimentCategoryPanel, self).__init__(model.DbExperimentCategory, session, **kwargs)
        
        self.category_filter_number  = get_filter_number(self, u'Category.name')

        ExperimentCategoryPanel.INSTANCE = self

class ExperimentPanel(AdministratorModelView):
    
    column_searchable_list = ('name',)
    column_list = ('category', 'name', 'start_date', 'end_date', 'uses')

    
    column_filters = ('name','category')

    column_formatters = dict(
                        category = lambda c, e, p: show_link(ExperimentCategoryPanel, 'category', e, 'category.name', SAME_DATA),
                        uses     = lambda c, e, p: show_link(UserUsedExperimentPanel, 'experiment', e, 'name'),
                )

    INSTANCE = None

    def __init__(self, session, **kwargs):
        super(ExperimentPanel, self).__init__(model.DbExperiment, session, **kwargs)
        
        self.name_filter_number  = get_filter_number(self, u'Experiment.name')
        self.category_filter_number  = get_filter_number(self, u'Category.name')
        ExperimentPanel.INSTANCE = self

def display_parameters(context, permission, p):
    parameters = u''
    for parameter in permission.parameters:
        parameters += u'%s = %s, ' % (parameter.permission_type_parameter.name, parameter.value)
    permission_str = u'%s(%s)' % (permission.permission_type.name, parameters[:-2])
    return permission_str


class GenericPermissionPanel(AdministratorModelView):
    
    """ Abstract class for UserPermissionPanel, GroupPermissionPanel and RolePermissionPanel """

    can_create = False

    column_descriptions = dict(permanent_id = 'A unique permanent identifier for a particular permission',)
    column_searchable_list = ('permanent_id', 'comments')
    column_formatters = dict( permission = display_parameters )
    column_filters = ( 'permission_type', 'permanent_id', 'date', 'comments' )
    column_sortable_list = ( 'permission', 'permanent_id', 'date', 'comments')
    column_list = ('permission', 'permanent_id', 'date', 'comments')

    def __init__(self, model, session, **kwargs):
        super(GenericPermissionPanel, self).__init__(model, session, **kwargs)

    def on_model_change(self, form, permission):
        req_arguments = {
            'experiment_allowed' : ('experiment_permanent_id','experiment_category_id','time_allowed'),
            'admin_panel_access' : ('full_privileges',),
            'access_forward'     : (),
        }
        opt_arguments = {
            'experiment_allowed' : ('priority','initialization_in_accounting'),
            'admin_panel_access' : (),
            'access_forward'     : (),
        }
        required_arguments = set(req_arguments[permission.permission_type.name])
        optional_arguments = set(opt_arguments[permission.permission_type.name])
        obtained_arguments = set([ parameter.permission_type_parameter.name for parameter in permission.parameters ])

        missing_arguments  = required_arguments.difference(obtained_arguments)
        exceeded_arguments = obtained_arguments.difference(required_arguments.union(optional_arguments))

        message = ""
        if missing_arguments:
            message = "Missing arguments: %s" % ', '.join(missing_arguments)
            if exceeded_arguments:
                message += "; "
        if exceeded_arguments:
            message += "Exceeded arguments: %s" % ', '.join(exceeded_arguments)
        if message:
            raise Exception(message)
            
        

class UserPermissionPanel(GenericPermissionPanel):

    column_filters       = GenericPermissionPanel.column_filters       + ('user',)
    column_sortable_list = GenericPermissionPanel.column_sortable_list + (('user',model.DbUser.login),)
    column_list          = ('user', )  + GenericPermissionPanel.column_list

    inline_models = (model.DbUserPermissionParameter,)

    INSTANCE = None

    def __init__(self, session, **kwargs):
        super(UserPermissionPanel, self).__init__(model.DbUserPermission, session, **kwargs)
        self.user_filter_number = get_filter_number(self, u'User.login')
        UserPermissionPanel.INSTANCE = self

class GroupPermissionPanel(GenericPermissionPanel):

    column_filters       = GenericPermissionPanel.column_filters       + ('group',)
    column_sortable_list = GenericPermissionPanel.column_sortable_list + (('group',model.DbGroup.name),)
    column_list          = ('group', )  + GenericPermissionPanel.column_list

    inline_models = (model.DbGroupPermissionParameter,)

    INSTANCE = None

    def __init__(self, session, **kwargs):
        super(GroupPermissionPanel, self).__init__(model.DbGroupPermission, session, **kwargs)

        self.group_filter_number = get_filter_number(self, u'Group.name')
        
        GroupPermissionPanel.INSTANCE = self

class RolePermissionPanel(GenericPermissionPanel):

    column_filters       = GenericPermissionPanel.column_filters       + ('role',)
    column_sortable_list = GenericPermissionPanel.column_sortable_list + (('role',model.DbRole.name),)
    column_list          = ('role', )  + GenericPermissionPanel.column_list

    inline_models = (model.DbRolePermissionParameter,)

    INSTANCE = None

    def __init__(self, session, **kwargs):
        super(RolePermissionPanel, self).__init__(model.DbRolePermission, session, **kwargs)
        
        self.role_filter_number = get_filter_number(self, u'Role.name')

        RolePermissionPanel.INSTANCE = self

class HomeView(AdminIndexView):

    def __init__(self, db_session, **kwargs):
        self._db_session = db_session
        super(HomeView, self).__init__(**kwargs)

    @expose()
    def index(self):
        return self.render("admin-index.html")

    def is_accessible(self):
        return get_app_instance().INSTANCE.is_admin()

    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            return redirect(request.url.split('/weblab/administration')[0] + '/weblab/client')

        return super(HomeView, self)._handle_view(name, **kwargs)


