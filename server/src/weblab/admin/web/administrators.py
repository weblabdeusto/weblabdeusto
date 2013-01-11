from flask import Flask, Markup
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
#  - remove everything related to ExternalEntity
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


class UsersPanel(AdministratorModelView):

    column_list = ('role', 'login', 'full_name', 'email', 'groups', 'logs')
    column_searchable_list = ('full_name', 'login')
    column_filters = ( 'full_name', 'login','role', 'email'
                    ) + generate_filter_any(model.DbGroup.name.property.columns[0], 'Group', model.DbUser.groups)


    column_descriptions = dict( full_name='First and Last name' )

    inline_models = (model.DbUserAuth,)

    column_formatters = dict(
                            role   = lambda c, u, p: Markup(u'<a href="%s?flt1_%s=%s">%s</a>' % (UsersPanel.INSTANCE.url,              UsersPanel.INSTANCE.role_filter_number, u.role.name, u.role.name)),
                            groups = lambda c, u, p: Markup(u'<a href="%s?flt1_%s=%s">%s</a>' % (GroupsPanel.INSTANCE.url,             GroupsPanel.INSTANCE.user_filter_number, u.login, 'View')),
                            logs   = lambda c, u, p: Markup(u'<a href="%s?flt1_%s=%s">%s</a>' % (UserUsedExperimentPanel.INSTANCE.url, UserUsedExperimentPanel.INSTANCE.user_filter_number, u.login, 'View'))
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
                            users = lambda c, g, p: Markup(u'<a href="%s?flt1_%s=%s">%s</a>' % (UsersPanel.INSTANCE.url,  UsersPanel.INSTANCE.group_filter_number, g.name, 'View')),
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
                    user = lambda c, uue, p: Markup(u'<a href="%s?flt1_%s=%s">%s</a>' % (UsersPanel.INSTANCE.url, UsersPanel.INSTANCE.login_filter_number, uue.user.login if uue.user is not None else '', uue.user.login if uue.user is not None else '')),
                    experiment = lambda c, uue, p: Markup(u'<a href="%s?flt1_%s=%s&flt2_%s=%s">%s</a>' % (ExperimentPanel.INSTANCE.url, ExperimentPanel.INSTANCE.name_filter_number, uue.experiment.name if uue.experiment is not None else '', ExperimentPanel.INSTANCE.category_filter_number, uue.experiment.category.name if uue.experiment is not None and uue.experiment.category is not None else '', uue.experiment )),
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
                    experiments = lambda co, c, p: Markup(u'<a href="%s?flt1_%s=%s">%s</a>' % (ExperimentPanel.INSTANCE.url, ExperimentPanel.INSTANCE.category_filter_number, c.name, 'View'))
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
                        category = lambda c, e, p: Markup(u'<a href="%s?flt1_%s=%s">%s</a>' % (ExperimentCategoryPanel.INSTANCE.url, ExperimentCategoryPanel.INSTANCE.category_filter_number, e.category.name if e.category is not None else '', e.category.name if e.category is not None else '')),
#                        uses     = lambda c, e, p: Markup(u'<a href="%s?flt1_%s=%s&flt2_%s=%s">%s</a>' % (UserUsedExperimentPanel.INSTANCE.url, UserUsedExperimentPanel.INSTANCE.experiment_filter_number, e.name, UserUsedExperimentPanel.INSTANCE.experiment_category_filter_number, e.category.name if e.category is not None else '', 'View')),
                        uses     = lambda c, e, p: Markup(u'<a href="%s?flt1_%s=%s">%s</a>' % (UserUsedExperimentPanel.INSTANCE.url, UserUsedExperimentPanel.INSTANCE.experiment_filter_number, e.name, 'View')),
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

class UserPermissionPanel(AdministratorModelView):

    inline_models = (model.DbUserPermissionParameter,)

    def __init__(self, session, **kwargs):
        default_args = { "category" : u"Permissions", "name" : u"user permissions" }
        default_args.update(**kwargs)

        super(UserPermissionPanel, self).__init__(model.DbUserPermission, session, **default_args)

class GroupPermissionPanel(AdministratorModelView):

    inline_models = (model.DbGroupPermissionParameter,)

    def __init__(self, session, **kwargs):
        default_args = { "category" : u"Permissions", "name" : u"group permissions" }
        default_args.update(**kwargs)

        super(GroupPermissionPanel, self).__init__(model.DbGroupPermission, session, **default_args)


engine = create_engine('mysql://weblab:weblab@localhost/WebLabTests', convert_unicode=True, pool_recycle=3600, echo = False)

db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

class AdministrationApplication(object):

    INSTANCE = None

    def __init__(self, cfg_manager, bypass_authz = False):

        self.app = Flask(__name__)
        self.admin = Admin(self.app)
        self.admin.add_view(UsersPanel(db_session))
        self.admin.add_view(GroupsPanel(db_session))
        self.admin.add_view(UserUsedExperimentPanel(db_session))
        self.admin.add_view(ExperimentCategoryPanel(db_session))
        self.admin.add_view(ExperimentPanel(db_session))
        self.admin.add_view(PermissionTypePanel(db_session))
        self.admin.add_view(UserPermissionPanel(db_session))
        self.admin.add_view(GroupPermissionPanel(db_session))

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

