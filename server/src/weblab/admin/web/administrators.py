from flask import Flask, Markup, request
from flask.ext.admin import Admin
import flask_admin.contrib.sqlamodel.filters as filters
from flask.ext.admin.contrib.sqlamodel import tools
from flask.ext.admin.contrib.sqlamodel import ModelView

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

if __name__ == '__main__':
    import sys, os
    sys.path.insert(0, '.')

import weblab.db.model as model

# 
# TODO:
# 
#  - Add an 'federated' role
# 
#  - simplify the schema of permissions, and add support
#    for permissions of the federated role, as well as
#    builtin permissions (such as admin or forward)
# 

class FilterAnyEqual(filters.FilterEqual):
    def __init__(self, column, name, column_any, **kwargs):
        self.column_any = column_any
        super(FilterAnyEqual, self).__init__(column, name, **kwargs)

    def apply(self, query, value):
        return query.filter(self.column_any.any(self.column == value))

class FilterAnyNotEqual(filters.FilterNotEqual):
    def __init__(self, column, name, column_any, **kwargs):
        self.column_any = column_any
        super(FilterAnyNotEqual, self).__init__(column, name, **kwargs)

    def apply(self, query, value):
        return query.filter(self.column_any.any(self.column != value))

class FilterAnyLike(filters.FilterLike):
    def __init__(self, column, name, column_any, **kwargs):
        self.column_any = column_any
        super(FilterAnyLike, self).__init__(column, name, **kwargs)

    def apply(self, query, value):
        stmt = tools.parse_like_term(value)
        return query.filter(self.column_any.any(self.column.ilike(stmt)))

class FilterAnyNotLike(filters.FilterNotLike):
    def __init__(self, column, name, column_any, **kwargs):
        self.column_any = column_any
        super(FilterAnyNotLike, self).__init__(column, name, **kwargs)

    def apply(self, query, value):
        stmt = tools.parse_like_term(value)
        return query.filter(self.column_any.any(~self.column.ilike(stmt)))

def generate_filter_any(column, name, column_any, iter_type = tuple):
    return iter_type( 
                    (FilterAnyEqual(column, name, column_any), FilterAnyNotEqual(column, name, column_any), 
                     FilterAnyLike(column, name, column_any), FilterAnyNotLike(column, name, column_any)) )


def get_filter_number(view, name):
    return [ n  
                for (n, f) in enumerate(view._filters) 
                if unicode(f.column).endswith(name) 
                    and isinstance(f.operation.im_self, filters.FilterEqual) 
        ][0]

class AdministratorModelView(ModelView):

    def is_accessible(self):
        return AdministrationApplication.INSTANCE.is_admin()

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

    instance      = klass.INSTANCE
    url           = instance.url

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
    

class UsersPanel(AdministratorModelView):

    column_list = ('role', 'login', 'full_name', 'email', 'groups', 'logs')
    column_searchable_list = ('full_name', 'login')
    column_filters = ( 'full_name', 'login','role', 'email'
                    ) + generate_filter_any(model.DbGroup.name.property.columns[0], 'Group', model.DbUser.groups)


    column_descriptions = dict( full_name='First and Last name' )

    inline_models = (model.DbUserAuth,)

    column_formatters = dict(
                            role   = lambda c, u, p: show_link(UsersPanel,              'role', u, 'role.name', SAME_DATA),
                            groups = lambda c, u, p: show_link(GroupsPanel,             'user', u, 'login'),
                            logs   = lambda c, u, p: show_link(UserUsedExperimentPanel, 'user', u, 'login'),
                        )

    INSTANCE = None

    def __init__(self, session, **kwargs):
        default_args = { "category":u"General", "name":u"Users" }
        default_args.update(**kwargs)
        super(UsersPanel, self).__init__(model.DbUser, session, **default_args)
        self.login_filter_number = get_filter_number(self, u'User.login')
        self.group_filter_number = get_filter_number(self, u'Group.name')
        self.role_filter_number  = get_filter_number(self, u'Role.name')
        UsersPanel.INSTANCE = self

class GroupsPanel(AdministratorModelView):

    column_list = ('name','parent', 'users')

    column_filters = ( ('name',) 
                        + generate_filter_any(model.DbUser.login.property.columns[0], 'User login', model.DbGroup.users)
                        + generate_filter_any(model.DbUser.full_name.property.columns[0], 'User name', model.DbGroup.users)
                    )

    column_formatters = dict(
                            users = lambda c, g, p: show_link(UsersPanel, 'group', g, 'name'),
                        )

    INSTANCE = None

    def __init__(self, session, **kwargs):
        default_args = { "category":u"General", "name":u"Groups" }
        default_args.update(**kwargs)
        super(GroupsPanel, self).__init__(model.DbGroup, session, **default_args)

        self.user_filter_number  = get_filter_number(self, u'User.login')

        GroupsPanel.INSTANCE = self


class UserUsedExperimentPanel(AdministratorModelView):

    column_auto_select_related = True
    column_select_related_list = ('user',)
    can_delete = False
    can_edit   = False
    can_create = False

    column_filters = ( 'user', 'start_date', 'end_date', 'experiment', 'origin', 'coord_address') 

    column_formatters = dict(
                    user = lambda c, uue, p: show_link(UsersPanel, 'login', uue, 'user.login', SAME_DATA),
                    experiment = lambda c, uue, p: show_link(ExperimentPanel, ('name', 'category'), uue, ('experiment.name', 'experiment.category.name'), uue.experiment ),
                )

    action_disallowed_list = ['create','edit','delete']

    INSTANCE = None

    def __init__(self, session, **kwargs):
        default_args = { "category":u"Logs", "name":u"User logs" }
        default_args.update(**kwargs)
        super(UserUsedExperimentPanel, self).__init__(model.DbUserUsedExperiment, session, **default_args)

        self.user_filter_number  = get_filter_number(self, u'User.login')
        self.experiment_filter_number  = get_filter_number(self, u'Experiment.name')
        # self.experiment_category_filter_number  = get_filter_number(self, u'Category.name')

        UserUsedExperimentPanel.INSTANCE = self

class ExperimentCategoryPanel(AdministratorModelView):
   
    column_list    = ('name', 'experiments')
    column_filters = ( 'name', ) 

    column_formatters = dict(
                    experiments = lambda co, c, p: show_link(ExperimentPanel, 'category', c, 'name')
                )

    INSTANCE = None

    def __init__(self, session, **kwargs):

        default_args = { "category" : u"Experiments", "name" : u"Categories" }
        default_args.update(**kwargs)

        super(ExperimentCategoryPanel, self).__init__(model.DbExperimentCategory, session, **default_args)
        
        self.category_filter_number  = get_filter_number(self, u'Category.name')

        ExperimentCategoryPanel.INSTANCE = self

class ExperimentPanel(AdministratorModelView):
    
    column_list = ('category', 'name', 'start_date', 'end_date', 'uses')

    
    column_filters = ('name','category')

    column_formatters = dict(
                        category = lambda c, e, p: show_link(ExperimentCategoryPanel, 'category', e, 'category.name', SAME_DATA),
                        uses     = lambda c, e, p: show_link(UserUsedExperimentPanel, 'experiment', e, 'name'),
                )

    INSTANCE = None

    def __init__(self, session, **kwargs):

        default_args = { "category" : u"Experiments", "name" : u"Experiments" }
        default_args.update(**kwargs)

        super(ExperimentPanel, self).__init__(model.DbExperiment, session, **default_args)
        
        self.name_filter_number  = get_filter_number(self, u'Experiment.name')
        self.category_filter_number  = get_filter_number(self, u'Category.name')
        ExperimentPanel.INSTANCE = self

class PermissionTypePanel(AdministratorModelView):

    column_list = ('name', 'description')
    can_edit   = False
    can_create = False
    can_delete = False
    inline_models = (model.DbPermissionTypeParameter,)

    def __init__(self, session, **kwargs):
        default_args = { "category" : u"Permissions", "name" : u"types" }
        default_args.update(**kwargs)

        super(PermissionTypePanel, self).__init__(model.DbPermissionType, session, **default_args)

def display_parameters(context, permission, p):
    parameters = u''
    for parameter in permission.parameters:
        parameters += u'%s = %s, ' % (parameter.permission_type_parameter.name, parameter.value)
    permission_str = u'%s(%s)' % (permission.permission_type.name, parameters[:-2])
    return permission_str

class UserPermissionPanel(AdministratorModelView):

    column_list = ('user', 'permission', 'permanent_id', 'date', 'comments')
    column_formatters = dict( permission = display_parameters,
    user = lambda c, u, p: unicode(u.user) )

    inline_models = (model.DbUserPermissionParameter,)

    def __init__(self, session, **kwargs):
        default_args = { "category" : u"Permissions", "name" : u"User permissions" }
        default_args.update(**kwargs)

        super(UserPermissionPanel, self).__init__(model.DbUserPermission, session, **default_args)

class GroupPermissionPanel(AdministratorModelView):

    column_list = ('group', 'permission', 'permanent_id', 'date', 'comments')
    column_formatters = dict( permission = display_parameters )
    inline_models = (model.DbGroupPermissionParameter,)

    def __init__(self, session, **kwargs):
        default_args = { "category" : u"Permissions", "name" : u"Group permissions" }
        default_args.update(**kwargs)

        super(GroupPermissionPanel, self).__init__(model.DbGroupPermission, session, **default_args)

class RolePermissionPanel(AdministratorModelView):

    column_list = ('role', 'permission', 'permanent_id', 'date', 'comments')
    column_formatters = dict( permission = display_parameters )
    inline_models = (model.DbRolePermissionParameter,)

    def __init__(self, session, **kwargs):
        default_args = { "category" : u"Permissions", "name" : u"Role permissions" }
        default_args.update(**kwargs)

        super(RolePermissionPanel, self).__init__(model.DbRolePermission, session, **default_args)


class AdministrationApplication(object):

    INSTANCE = None

    def __init__(self, cfg_manager, bypass_authz = False):
        engine = create_engine('mysql://weblab:weblab@localhost/WebLabTests', convert_unicode=True, pool_recycle=3600, echo = False)
        db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

        self.app = Flask(__name__)
        self.admin = Admin(self.app, name = 'WebLab-Deusto Admin')
        self.admin.add_view(UsersPanel(db_session))
        self.admin.add_view(GroupsPanel(db_session))
        self.admin.add_view(UserUsedExperimentPanel(db_session))
        self.admin.add_view(ExperimentCategoryPanel(db_session))
        self.admin.add_view(ExperimentPanel(db_session))
        self.admin.add_view(PermissionTypePanel(db_session))
        self.admin.add_view(UserPermissionPanel(db_session))
        self.admin.add_view(GroupPermissionPanel(db_session))
        self.admin.add_view(RolePermissionPanel(db_session))

        self.bypass_authz = bypass_authz

        AdministrationApplication.INSTANCE = self

    def is_admin(self):
        if self.bypass_authz:
            return True
        
        # TODO: contact the UPS ask for the session, etc.
        return False
            

if __name__ == '__main__':
    SECRET_KEY = 'development_key'
    admin_app = AdministrationApplication(None, bypass_authz = True)

    admin_app.app.config.from_object(__name__)
    admin_app.app.run(debug=True, host = '0.0.0.0')

