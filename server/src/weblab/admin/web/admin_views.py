import os
import re
import sha
import time
import json
import random
import urlparse
import datetime
import traceback
import threading
import collections

from weblab.util import data_filename

try:
    CLIENTS = json.load(open(data_filename(os.path.join('weblab', 'clients.json'))))
except:
    print "Error loading weblab/clients.json. Did you run weblab-admin upgrade? Check the file"
    raise

from wtforms import TextField, TextAreaField, PasswordField, SelectField, BooleanField, HiddenField
from wtforms.fields.core import UnboundField
from wtforms.fields.html5 import URLField
from wtforms.validators import Email, Regexp, Required, NumberRange, URL

from sqlalchemy.sql.expression import desc

from flask import Markup, request, redirect, abort, url_for, flash, Response

from flask.ext.wtf import Form

from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.admin import expose, AdminIndexView, BaseView
from flask.ext.admin.form import Select2Field, rules
from flask.ext.admin.model.form import InlineFormAdmin

import weblab.configuration_doc as configuration_doc
import weblab.db.model as model
import weblab.permissions as permissions

from weblab.admin.web.filters import get_filter_number, generate_filter_any
from weblab.admin.web.fields import DisabledTextField, VisiblePasswordField, RecordingQuerySelectField

try:
    from weblab.admin.ldap_gateway import LdapGateway

    LdapGatewayClass = LdapGateway
except ImportError:
    LdapGatewayClass = None

from weblab.core.coordinator.clients.weblabdeusto import WebLabDeustoClient

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


class MyProfileView(AdministratorView):
    @expose()
    def index(self):
        return redirect(request.url.split('/weblab/administration')[0] + '/weblab/administration/profile')


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


def get_full_url(url):
    script_name = get_app_instance().script_name
    return script_name + url


def show_link(klass, filter_name, field, name, view='View'):
    instance = klass.INSTANCE
    url = get_full_url(instance.url)

    link = u'<a href="%s?' % url

    if isinstance(filter_name, basestring):
        filter_numbers = [getattr(instance, u'%s_filter_number' % filter_name)]
    else:
        filter_numbers = [getattr(instance, u'%s_filter_number' % fname) for fname in filter_name]

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
        form_class.auth.field_class = RecordingQuerySelectField
        form_class.configuration = UnboundField(VisiblePasswordField,
                                                description='Detail the password (DB), Facebook ID -the number- (Facebook), OpenID identifier.')
        return form_class


LOGIN_REGEX = '^[A-Za-z0-9\._-][A-Za-z0-9\._-][A-Za-z0-9\._-][A-Za-z0-9\._-]*$'


def _password2sha(password):
    # TODO: Avoid replicating
    randomstuff = ""
    for _ in range(4):
        c = chr(ord('a') + random.randint(0, 25))
        randomstuff += c
    password = password if password is not None else ''
    return randomstuff + "{sha}" + sha.new(randomstuff + password).hexdigest()


class UsersPanel(AdministratorModelView):
    column_list = ('role', 'login', 'full_name', 'email', 'groups', 'logs', 'permissions')
    column_searchable_list = ('full_name', 'login')
    column_filters = ( 'full_name', 'login', 'role', 'email', 
                     ) + generate_filter_any(model.DbGroup.name.property.columns[0], 'Group', model.DbUser.groups)

    form_excluded_columns = 'avatar', 'experiment_uses', 'permissions'
    form_args = dict(email=dict(validators=[Email()]), login=dict(validators=[Regexp(LOGIN_REGEX)]))

    column_descriptions = dict(login='Username (all letters, dots and numbers)',
                               full_name='First and Last name',
                               email='Valid e-mail address',
                               avatar='Not implemented yet, it should be a public URL for a user picture.')

    inline_models = (UserAuthForm(model.DbUserAuth),)

    column_formatters = dict(
        role=lambda v, c, u, p: show_link(UsersPanel, 'role', u, 'role.name', SAME_DATA),
        groups=lambda v, c, u, p: show_link(GroupsPanel, 'user', u, 'login'),
        logs=lambda v, c, u, p: show_link(UserUsedExperimentPanel, 'user', u, 'login'),
        permissions=lambda v, c, u, p: show_link(UserPermissionPanel, 'user', u, 'login'),
    )

    INSTANCE = None

    def __init__(self, session, **kwargs):
        super(UsersPanel, self).__init__(model.DbUser, session, **kwargs)
        self.login_filter_number = get_filter_number(self, u'User.login')
        self.group_filter_number = get_filter_number(self, u'Group.name')
        self.role_filter_number = get_filter_number(self, u'Role.name')

        self.local_data = threading.local()

        UsersPanel.INSTANCE = self

    def edit_form(self, obj=None):
        form = super(UsersPanel, self).edit_form(obj)
        self.local_data.authentications = {}
        if obj is not None:
            for auth_instance in obj.auths:
                self.local_data.authentications[auth_instance.id] = (
                    auth_instance.auth.name, auth_instance.configuration)
        return form

    def on_model_change(self, form, user_model):
        auths = set()
        for auth_instance in user_model.auths:
            auths.add(auth_instance.auth)

            if hasattr(self.local_data, 'authentications'):

                old_auth_type, old_auth_conf = self.local_data.authentications.get(auth_instance.id, (None, None))
                if old_auth_type == auth_instance.auth.name and old_auth_conf == auth_instance.configuration:
                    # Same as before: ignore
                    continue

                if not auth_instance.configuration:
                    # User didn't do anything here. Restoring configuration.
                    auth_instance.configuration = old_auth_conf or ''
                    continue

            self._on_auth_changed(auth_instance)


    def _on_auth_changed(self, auth_instance):
        if auth_instance.auth.auth_type.name.lower() == 'db':
            password = auth_instance.configuration
            if len(password) < 6:
                raise Exception("Password too short")
            auth_instance.configuration = _password2sha(password)
        elif auth_instance.auth.auth_type.name.lower() == 'facebook':
            try:
                int(auth_instance.configuration)
            except:
                raise Exception("Use a numeric ID for Facebook")
                # Other validations would be here


class UsersBatchForm(Form):
    """This form enables adding multiple users in a single action."""

    users = TextAreaField(u"Users:", description="Add the user list using the detailed format")
    new_group = TextField(u"New group:")
    existing_group = Select2Field(u"Existing group:")


class LdapUsersBatchForm(UsersBatchForm):
    ldap_user = TextField(u"Your LDAP username:")
    ldap_password = PasswordField(u"Your LDAP password:")
    ldap_domain = TextField(u"Your domain:")
    ldap_system = SelectField(u"LDAP gateway:")


class FormException(Exception):
    """ Used to know that there was an error parsing the form """


class UsersAddingView(AdministratorView):
    def __init__(self, session, **kwargs):
        self.session = session
        super(UsersAddingView, self).__init__(**kwargs)

    @expose()
    def index(self):
        # TODO: enable / disable OpenID and LDAP depending on if it is available
        return self.render("admin-add-students-select.html")

    def _get_form(self, klass=UsersBatchForm):
        form = klass()
        groups = [(g.name, g.name) for g in self.session.query(model.DbGroup).order_by(desc('id')).all()]
        form.existing_group.choices = groups
        return form

    def _parse_text(self, text, columns):
        rows = []
        errors = False
        for n, line in enumerate(text.splitlines()):
            if line.strip():
                cur_columns = [col.strip() for col in line.split(',')]
                if len(cur_columns) != len(columns):
                    flash(
                        u"Line %s (%s) does not have %s columns (%s found)" % (n, line, len(columns), len(cur_columns)))
                    errors = True
                    continue

                cur_error = False
                for column, fmt in zip(cur_columns, columns):
                    if fmt == 'login':
                        regex = re.compile(LOGIN_REGEX)
                        if not regex.match(column):
                            flash(u"Login %s contains invalid characters" % column)
                            cur_error = True
                        existing_user = self.session.query(model.DbUser).filter_by(login=column).first()
                        if existing_user is not None:
                            flash(u"User %s already exists" % column)
                            # The user exists already. However, we do not consider this an error.
                            # That way we can add groups for which some users exist already.
                            # cur_error = True
                    elif fmt == 'mail':
                        # Not exhaustive
                        regex = re.compile('^.*@.*\..*')
                        if not regex.match(column):
                            flash("Invalid e-mail address: %s" % column)
                            cur_error = True
                if cur_error:
                    errors = True
                else:
                    rows.append(cur_columns)

        if not errors and len(rows) == 0:
            flash("No user provided")
            raise FormException()

        if errors:
            flash("No user added due to errors detailed", 'error')
            raise FormException()
        return rows

    def _process_db(self, text):
        role = self.session.query(model.DbRole).filter_by(name='student').one()
        auth_type = self.session.query(model.DbAuthType).filter_by(name='DB').one()
        auth = auth_type.auths[0]

        users = []
        rows = self._parse_text(text, ('login', 'full_name', 'mail', 'password'))
        for login, full_name, mail, password in rows:
            user = model.DbUser(login=login, full_name=full_name, email=mail, role=role)
            self.session.add(user)
            user_auth = model.DbUserAuth(user=user, auth=auth, configuration=_password2sha(password))
            self.session.add(user_auth)
            users.append(user)

        return users


    def _process_openid(self, text):
        role = self.session.query(model.DbRole).filter_by(name='student').one()
        auth_type = self.session.query(model.DbAuthType).filter_by(name='OPENID').one()
        auth = auth_type.auths[0]

        users = []
        rows = self._parse_text(text, ('login', 'full_name', 'mail', 'open_id'))
        for login, full_name, mail, open_id in rows:
            user = model.DbUser(login=login, full_name=full_name, email=mail, role=role)
            self.session.add(user)
            user_auth = model.DbUserAuth(user=user, auth=auth, configuration=open_id)
            self.session.add(user_auth)
            users.append(user)

        return users

    def _process_ldap(self, text, form):
        if LdapGatewayClass is None:
            flash("Error: ldap libraries not installed")
            return []

        role = self.session.query(model.DbRole).filter_by(name='student').one()
        auth_ldap = self.session.query(model.DbAuth).filter_by(name=form.ldap_system.data).one()

        ldap_uri = auth_ldap.get_config_value("ldap_uri")
        ldap_base = auth_ldap.get_config_value("base")
        ldap = LdapGatewayClass(ldap_uri, form.ldap_domain.data, ldap_base, form.ldap_user.data,
                                form.ldap_password.data)

        users = []

        rows = [user[0] for user in self._parse_text(text, ('login',))]
        try:
            users_data = ldap.get_users(rows)
        except:
            traceback.print_exc()
            flash("Error retrieving users from the LDAP server. Contact your administrator.")
            raise FormException()

        if len(users_data) != len(rows):
            retrieved_logins = [user['login'] for user in users_data]
            missing_logins = []
            for login in rows:
                if login not in retrieved_logins:
                    missing_logins.append(login)
            all_missing_logins = ', '.join(missing_logins)
            flash("Error: could not find the following users: %s" % all_missing_logins)
            raise FormException()

        if len(users_data) == 0:
            flash("No user processed")
            raise FormException()

        for user_data in users_data:
            ENCODING = 'utf-8'
            login = user_data['login'].decode(ENCODING)
            full_name = user_data['full_name'].decode(ENCODING)
            email = user_data['email'].decode(ENCODING)

            # First, we try to retrieve the user. If it exists already we don't need
            # to create it.
            user = self.session.query(model.DbUser).filter_by(login=login).first()

            if user is None:
                user = model.DbUser(login=login, full_name=full_name, email=email, role=role)
                self.session.add(user)
                user_auth = model.DbUserAuth(user=user, auth=auth_ldap, configuration=None)
                self.session.add(user_auth)

            users.append(user)

        return users

    def _process_groups(self, form, users):
        group_option = request.form.get('group', 'none')
        if group_option == 'new':
            group = model.DbGroup(name=form.new_group.data)
            self.session.add(group)
        elif group_option == 'existing':
            group = self.session.query(model.DbGroup).filter_by(name=form.existing_group.data).one()

        if group_option in ('new', 'existing'):
            group_name = group.name
            for user in users:
                group.users.append(user)
        else:
            group_name = ""

        return group_name


    @expose('/db/', methods=['GET', 'POST'])
    def add_db(self):
        form = self._get_form()
        description = "In this case, you need to provide the user's login, full_name, e-mail address, and password, in this order and separated by commas."
        example = ("j.doe, John Doe, john@institution.edu, appl3_1980\n" +
                   "j.smith, Jack Smith, jack@institution.edu, h4m_1980\n")
        if form.validate_on_submit():
            try:
                users = self._process_db(form.users.data)
            except FormException:
                pass
            else:
                group_name = self._process_groups(form, users)
                try:
                    self.session.commit()
                except:
                    flash("Errors occurred while adding users")
                else:
                    return self.render("admin-add-students-finished.html", users=users, group_name=group_name)
        elif not form.users.data:
            form.users.data = example
        return self.render("admin-add-students.html", form=form, description=description, example=example)

    @expose('/ldap/', methods=['GET', 'POST'])
    def add_ldap(self):
        form = self._get_form(LdapUsersBatchForm)

        ldap_auth_type = self.session.query(model.DbAuthType).filter_by(name='LDAP').first()
        if ldap_auth_type is None:
            return "LDAP not registered as an Auth Type"

        form.ldap_system.choices = [(auth.name, auth.name) for auth in ldap_auth_type.auths]
        description = "In this case, you only need to provide the username of the users, separated by spaces or new lines. WebLab-Deusto will retrieve the rest of the information from the LDAP system."
        example = "user1\nuser2\nuser3"
        if form.validate_on_submit():
            try:
                users = self._process_ldap(form.users.data, form)
            except FormException:
                pass
            else:
                group_name = self._process_groups(form, users)
                try:
                    self.session.commit()
                except:
                    flash("Errors occurred while adding users")
                else:
                    return self.render("admin-add-students-finished.html", users=users, group_name=group_name)
        elif not form.users.data:
            form.users.data = example
        return self.render("admin-add-students.html", form=form, description=description, example=example)

    @expose('/openid/', methods=['GET', 'POST'])
    def add_openid(self):
        form = self._get_form()
        description = "In this case, you only need to provide the username of the user, the full name, e-mail address and OpenID, in this order and separated by commas."
        example = ( "j.doe,   John Doe,   john@institution.edu, institution.edu/users/john\n" +
                    "j.smith, Jack Smith, jack@institution.edu, institution.edu/users/jack\n" )
        if form.validate_on_submit():
            try:
                users = self._process_openid(form.users.data)
            except FormException:
                pass
            else:
                group_name = self._process_groups(form, users)
                try:
                    self.session.commit()
                except:
                    flash("Errors occurred while adding users")
                else:
                    return self.render("admin-add-students-finished.html", users=users, group_name=group_name)
        elif not form.users.data:
            form.users.data = example
        return self.render("admin-add-students.html", form=form, description=description, example=example)


class GroupsPanel(AdministratorModelView):
    column_searchable_list = ('name',)
    column_list = ('name', 'parent', 'users', 'permissions')

    column_filters = ( ('name',)
                       + generate_filter_any(model.DbUser.login.property.columns[0], 'User login', model.DbGroup.users)
                       + generate_filter_any(model.DbUser.full_name.property.columns[0], 'User name',
                                             model.DbGroup.users)
    )

    column_formatters = dict(
        users=lambda v, c, g, p: show_link(UsersPanel, 'group', g, 'name'),
        permissions=lambda v, c, g, p: show_link(GroupPermissionPanel, 'group', g, 'name'),
    )

    INSTANCE = None

    def __init__(self, session, **kwargs):
        super(GroupsPanel, self).__init__(model.DbGroup, session, **kwargs)

        self.user_filter_number = get_filter_number(self, u'User.login')

        GroupsPanel.INSTANCE = self


class UserUsedExperimentPanel(AdministratorModelView):
    column_auto_select_related = True
    column_select_related_list = ('user',)
    can_delete = False
    can_edit = False
    can_create = False

    column_searchable_list = ('origin',)
    column_sortable_list = (
        'UserUsedExperiment.id', ('user', model.DbUser.login), ('experiment', model.DbExperiment.id), 'start_date',
        'end_date', 'origin', 'coord_address')
    column_list = ( 'user', 'experiment', 'start_date', 'end_date', 'origin', 'coord_address', 'details')
    column_filters = ( 'user', 'start_date', 'end_date', 'experiment', 'origin', 'coord_address')

    column_formatters = dict(
        user=lambda v, c, uue, p: show_link(UsersPanel, 'login', uue, 'user.login', SAME_DATA),
        experiment=lambda v, c, uue, p: show_link(ExperimentPanel, ('name', 'category'), uue,
                                               ('experiment.name', 'experiment.category.name'), uue.experiment),
        details=lambda v, c, uue, p: Markup('<a href="%s">Details</a>' % (url_for('.detail', id=uue.id))),
    )

    action_disallowed_list = ['create', 'edit', 'delete']

    INSTANCE = None

    def __init__(self, files_directory, session, **kwargs):
        super(UserUsedExperimentPanel, self).__init__(model.DbUserUsedExperiment, session, **kwargs)

        self.files_directory = files_directory
        if type(self) == UserUsedExperimentPanel:
            self.user_filter_number = get_filter_number(self, u'User.login')
        self.experiment_filter_number = get_filter_number(self, u'Experiment.name')
        # self.experiment_category_filter_number  = get_filter_number(self, u'Category.name')

        if type(self) == UserUsedExperimentPanel:
            UserUsedExperimentPanel.INSTANCE = self

    def get_list(self, page, sort_column, sort_desc, search, filters, *args, **kwargs):
        # So as to sort descending, force sorting by 'id' and reverse the sort_desc

        if sort_column is None:
            sort_column = 'start_date'
            sort_desc = not sort_desc

            # If that fails, try to avoid it using a different sort_column
            try:
                return super(UserUsedExperimentPanel, self).get_list(page, sort_column, sort_desc, search, filters,
                                                                     *args, **kwargs)
            except:
                sort_column = 'UserUsedExperiment_start_date'
                return super(UserUsedExperimentPanel, self).get_list(page, sort_column, sort_desc, search, filters,
                                                                     *args, **kwargs)

        return super(UserUsedExperimentPanel, self).get_list(page, sort_column, sort_desc, search, filters, *args,
                                                             **kwargs)

    @expose('/details/<int:id>')
    def detail(self, id):
        uue = self.get_query().filter_by(id=id).first()
        if uue is None:
            return abort(404)

        properties = {}
        for prop in uue.properties:
            properties[prop.property_name.name] = prop.value

        return self.render("details.html", uue=uue, properties=properties)

    @expose('/interactions/<int:id>')
    def interactions(self, id):
        uue = self.get_query().filter_by(id=id).first()

        if uue is None:
            return abort(404)

        interactions = []

        for command in uue.commands:
            timestamp = time.mktime(command.timestamp_before.timetuple()) + 1e-6 * command.timestamp_before_micro
            interactions.append((timestamp, True, command))

        for f in uue.files:
            timestamp = time.mktime(f.timestamp_before.timetuple()) + 1e-6 * f.timestamp_before_micro
            interactions.append((timestamp, False, f))

        interactions.sort(lambda (x1, x2, x3), (y1, y2, y3): cmp(x1, y1))

        return self.render("interactions.html", uue=uue, interactions=interactions, unicode=unicode)

    def get_file(self, id):
        return self.session.query(model.DbUserFile).filter_by(id=id).first()

    @expose('/files/<int:id>')
    def files(self, id):
        uf = self.get_file(id)
        if uf is None:
            return abort(404)

        if 'not stored' in uf.file_sent:
            flash("File not stored")
            return self.render("error.html",
                               message="The file has not been stored. Check the %s configuration value." % configuration_doc.CORE_STORE_STUDENTS_PROGRAMS)

        file_path = os.path.join(self.files_directory, uf.file_sent)
        if os.path.exists(file_path):
            content = open(file_path).read()
            return Response(content, headers={'Content-Type': 'application/octstream',
                                              'Content-Disposition': 'attachment; filename=file_%s.bin' % id})
        else:
            if os.path.exists(self.files_directory):
                flash("Wrong configuration or file deleted")
                return self.render("error.html",
                                   message="The file was stored, but now it is not reachable. Check the %s property." % configuration_doc.CORE_STORE_STUDENTS_PROGRAMS_PATH)
            else:
                flash("Wrong configuration")
                return self.render("error.html",
                                   message="The file was stored, but now it is not reachable. The %s directory does not exist." % configuration_doc.CORE_STORE_STUDENTS_PROGRAMS_PATH)


class ExperimentCategoryPanel(AdministratorModelView):
    column_searchable_list = ('name',)
    column_list = ('name', 'experiments')
    column_filters = ( 'name', )

    column_formatters = dict(
        experiments=lambda v, co, c, p: show_link(ExperimentPanel, 'category', c, 'name')
    )

    INSTANCE = None

    def __init__(self, session, **kwargs):
        super(ExperimentCategoryPanel, self).__init__(model.DbExperimentCategory, session, **kwargs)

        self.category_filter_number = get_filter_number(self, u'Category.name')

        ExperimentCategoryPanel.INSTANCE = self

class ExperimentClientParameter(InlineFormAdmin):
    
    _all_possible_parameters = set()
    for _params in [ c['parameters'] for c in CLIENTS.values() ]:
        _all_possible_parameters.update(_params)

    _parameter_types = 'bool', 'string', 'integer', 'floating'

    parameter_name_choices = zip(sorted(_all_possible_parameters), sorted(_all_possible_parameters))
    parameter_type_choices = zip(sorted(_parameter_types), sorted(_parameter_types))

    form_overrides = dict(parameter_name = Select2Field, parameter_type = Select2Field)
    form_args = dict(parameter_name = dict(choices = parameter_name_choices, default = 'experiment.picture'), 
                     parameter_type = dict(choices = parameter_type_choices, default = 'string'))


    def postprocess_form(self, form_class):
        original_validate = form_class.validate
        def validate_wrapper(self):
            if ExperimentClientParameter.validate_parameters(self):
                return original_validate(self)
            return False
        form_class.validate = validate_wrapper
        return form_class

    @staticmethod
    def validate_parameters(form):
        parameter_type = form.parameter_type.data
        parameter_value = form.value.data
        parameter_name = form.parameter_name.data

        valid = True

        if parameter_type == 'bool':
            if parameter_value.lower() not in ('true', 'false'):
                form.value.errors = ["Invalid value for a boolean type: %s. Only true or false are permitted." % parameter_value ]
                valid = False
        elif parameter_type == 'integer':
            try:
                int(parameter_value)
            except:
                form.value.errors = ["Invalid value for an integer type: %s" % parameter_value ]
                valid = False
        elif parameter_type == 'floating':
            try:
                float(parameter_value)
            except:
                form.value.errors = [ "Invalid value for a float type: %s" % parameter_value ]
                valid = False
        # else: Strings are always fine :-)

        potential_types = set()
        for client in CLIENTS:
            for parameter, parameter_value in CLIENTS[client]['parameters'].iteritems():
                if parameter == parameter_name:
                    potential_types.add(parameter_value['type'])
        if parameter_type not in potential_types:
            form.parameter_type.errors = ["Invalid type. Expected %s" % ', '.join(potential_types)]
            valid = False

        return valid



class ExperimentPanel(AdministratorModelView):
    column_searchable_list = ('name',)
    column_list = ('category', 'name', 'client', 'start_date', 'end_date', 'uses')
    form_excluded_columns = 'user_uses',
    column_filters = ('name', 'category')
    form_overrides = dict( client = Select2Field )

    description_html = "<br><p>Parameters per client:</p><ul>"
    default_parameters = "experiment.info.description", "experiment.picture", "experiment.info.link", "experiment.reserve.button.shown"
    description_html += "<li><b>All:</b> %s</li>" % (', '.join(default_parameters))
    description_html += "</ul><ul>"
    for c in CLIENTS:
        client_parameters = [ p for p in CLIENTS[c]['parameters'] if p not in default_parameters]
        if len(client_parameters):
            description_html += "<li><b>%s:</b> " % c
            description_html += ', '.join(client_parameters)
            description_html += "</li>"
    description_html += "</ul>"

    client_choices = [ (c, c) for c in CLIENTS ]
    form_args = dict(
            client = dict(choices = client_choices, validators=[Required()], default = 'blank', description = Markup(description_html))
        )

    column_formatters = dict(
        category=lambda v, c, e, p: show_link(ExperimentCategoryPanel, 'category', e, 'category.name', SAME_DATA),
        uses=lambda v, c, e, p: show_link(UserUsedExperimentPanel, 'experiment', e, 'name'),
    )

    inline_models = (ExperimentClientParameter(model.DbExperimentClientParameter),)

    INSTANCE = None

    def __init__(self, session, **kwargs):
        super(ExperimentPanel, self).__init__(model.DbExperiment, session, **kwargs)

        self.name_filter_number = get_filter_number(self, u'Experiment.name')
        self.category_filter_number = get_filter_number(self, u'Category.name')
        ExperimentPanel.INSTANCE = self

    def create_form(self, obj = None):
        form = super(ExperimentPanel, self).create_form(obj)
        if obj is None:
            now = datetime.datetime.now()
            if form.start_date.data is None:
                form.start_date.data = now
            if form.end_date.data is None:
                # For 10 years (for example)
                form.end_date.data = now.replace(year = now.year + 10)
        return form

class SchedulerForm(Form):
    name = TextField("Scheduler name", description = "Unique name for this scheduler", validators = [Required()])

class PQueueForm(SchedulerForm):
    randomize_instances = BooleanField("Randomize experiments", description = "First available slot is always the same or there is an internal random process")

PQueueObject = collections.namedtuple('PQueueObject', ['name', 'randomize_instances'])

class ExternalWebLabForm(SchedulerForm):
    base_url = URLField("Base URL", description = "Example: https://www.weblab.deusto.es/weblab/", validators = [Required(), URL()])
    username = TextField("Username", description = "Username of the remote system", validators = [Required()])
    password = PasswordField("Password", description = "Password of the remote system", validators = [])

ExternalWebLabObject = collections.namedtuple('ExternalWebLabObject', ['name', 'base_url', 'username', 'password'])

class ILabBatchForm(SchedulerForm):
    lab_server_url = URLField("Web service URL", description = "Example: http://weblab2.mit.edu/services/WebLabService.asmx", validators = [Required(), URL()])
    identifier     = TextField("Identifier", description = "Fake Service Broker identifier", validators = [Required()])
    passkey        = TextField("Passkey", description = "Remote Service broker passkey", validators = [Required()])

ILabBatchObject = collections.namedtuple('ILabBatchObject', ['name', 'lab_server_url', 'identifier', 'passkey'])

class RemoveForm(Form):
    identifier = HiddenField()

class AddExperimentForm(Form):
    experiment_identifier = Select2Field("Experiment to add")

class SchedulerPanel(AdministratorModelView):
    
    column_list = ('name', 'summary', 'scheduler_type', 'is_external')

    def __init__(self, session, **kwargs):
        super(SchedulerPanel, self).__init__(model.DbScheduler, session, **kwargs)

    @expose('/create/')
    def create_view(self):
        return self.render("admin-scheduler-create.html")

    @expose('/create/pqueue/', ['GET', 'POST'])
    def create_pqueue_view(self):
        return self._edit_pqueue_view(url_for('.create_view'))

    def _edit_pqueue_view(self, back, obj = None, scheduler = None):
        form = PQueueForm(formdata = request.form, obj = obj)
        if form.validate_on_submit():
            if obj is None and self.session.query(model.DbScheduler).filter_by(name = form.name.data).first() is not None:
                form.name.errors = ["Repeated name"]
            else:
                # Populate config
                if scheduler is None:
                    config = {}
                else:
                    config = json.loads(scheduler.config)
                config['randomize_instances'] = form.randomize_instances.data
                summary = "Queue for %s" % form.name.data

                if scheduler is None:
                    scheduler = model.DbScheduler(name = form.name.data, summary = summary, scheduler_type = 'PRIORITY_QUEUE', config = json.dumps(config), is_external = False)
                else:
                    scheduler.name = form.name.data
                    scheduler.summary = summary

                self.session.add(scheduler)
                try:
                    self.session.commit()
                except:
                    flash("Error adding resource", "error")
                else:
                    flash("Scheduler saved", "success")
                    return redirect(url_for('.edit_view', id = scheduler.id))

        return self.render("admin-scheduler-create-pqueue.html", form = form, back = back)
        

    @expose('/create/weblab/', ['GET', 'POST'])
    def create_weblab_view(self):
        return self._edit_weblab_view(url_for('.create_view'))

    def _edit_weblab_view(self, back, obj = None, scheduler = None, experiments = None):
        form = ExternalWebLabForm(formdata = request.form, obj = obj)
        if form.validate_on_submit():
            if obj is None and self.session.query(model.DbScheduler).filter_by(name = form.name.data).first() is not None:
                form.name.errors = ["Repeated name"]
            else:
                # Populate config
                if scheduler is None:
                    config = { 'experiments_map' : {}}
                else:
                    config = json.loads(scheduler.config)
                config['base_url'] = form.base_url.data
                config['username'] = form.username.data
                if form.password.data or 'password' not in config:
                    config['password'] = form.password.data

                parsed = urlparse.urlparse(form.base_url.data)
                summary = "WebLab-Deusto at %s" % parsed.hostname

                if scheduler is None:
                    scheduler = model.DbScheduler(name = form.name.data, summary = summary, scheduler_type = 'EXTERNAL_WEBLAB_DEUSTO', config = json.dumps(config), is_external = True)
                else:
                    scheduler.name = form.name.data
                    scheduler.summary = summary

                self.session.add(scheduler)
                try:
                    self.session.commit()
                except:
                    flash("Error adding resource", "error")
                else:
                    flash("Scheduler saved", "success")
                    return redirect(url_for('.edit_view', id = scheduler.id))

        if scheduler:
            reverse_experiments_map = {}
            config = json.loads(scheduler.config)
            for local, remote in config['experiments_map'].iteritems():
                if remote in reverse_experiments_map:
                    reverse_experiments_map[remote].append(local)
                else:
                    reverse_experiments_map[remote] = [local]

            all_experiments = []
            for exp_allowed in experiments:
                exp_data = {
                    'experiment' : exp_allowed.experiment,
                }
                all_experiments.append(exp_data)
        else:
            all_experiments = []
        return self.render("admin-scheduler-create-weblab.html", form=form, back = back, experiments = all_experiments)

    @expose('/create/ilab/', ['GET', 'POST'])
    def create_ilab_view(self):    
        return self._edit_ilab_view(url_for('.create_view'))

    def is_action(self, name):
        return request.form and request.form.get('action') == name

    def _edit_ilab_view(self, back, form_kwargs = None, scheduler = None):
        experiments = self.session.query(model.DbExperiment).all()

        if self.is_action('form-add'):
            form = ILabBatchForm(prefix = "ilab_create", **form_kwargs)
        else:
            form = ILabBatchForm(formdata = None, prefix = "ilab_create", **form_kwargs)
        
        if self.is_action('form-add') and form.validate_on_submit():
            if obj is None and self.session.query(model.DbScheduler).filter_by(name = form.name.data).first() is not None:
                form.name.errors = ["Repeated name"]
            else:
                # Populate config
                if scheduler is None:
                    config = {}
                else:
                    config = json.loads(scheduler.config)
                config['lab_server_url'] = form.lab_server_url.data
                config['identifier'] = form.identifier.data
                config['passkey'] = form.passkey.data

                parsed = urlparse.urlparse(form.lab_server_url.data)
                summary = "iLab batch at %s" % parsed.hostname

                if scheduler is None:
                    scheduler = model.DbScheduler(name = form.name.data, summary = summary, scheduler_type = 'ILAB_BATCH_QUEUE', config = json.dumps(config), is_external = True)
                else:
                    scheduler.name = form.name.data
                    scheduler.summary = summary

                self.session.add(scheduler)
                try:
                    self.session.commit()
                except:
                    flash("Error adding resource", "error")
                else:
                    flash("Scheduler saved", "success")
                    return redirect(url_for('.edit_view', id = scheduler.id))

        if scheduler:
            choices = [ unicode(exp) for exp in experiments if exp not in scheduler.experiments]
        else:
            choices = [ unicode(exp) for exp in experiments ]

        if self.is_action('form-register'):
            add_form = AddExperimentForm(prefix = 'add_ilab')
        else:
            add_form = AddExperimentForm(formdata = None, prefix = 'add_ilab')
        add_form.experiment_identifier.choices = zip(choices, choices)
        if self.is_action('form-register') and add_form.validate_on_submit():
            experiment_to_register = add_form.experiment_identifier.data
            for experiment in experiments:
                if experiment_to_register == unicode(experiment) and experiment not in scheduler.experiments:
                    scheduler.experiments.append(experiment)
                    choices.remove(unicode(experiment))
                    self.session.commit()
                    add_form.experiment_identifier.choices = zip(choices, choices)
                    break

        registered_experiments = []
        if scheduler and experiments:

            for registered_experiment in scheduler.experiments[:]:
                prefix = 'remove_ilab_%s' % registered_experiment.id

                if self.is_action(prefix):
                    remove_form = RemoveForm(identifier = registered_experiment.id, prefix = prefix)
                else:
                    remove_form = RemoveForm(formdata = None, identifier = registered_experiment.id, prefix = prefix)

                if self.is_action(prefix) and remove_form.validate_on_submit():
                    print remove_form.identifier.data
                    experiment_id = int(remove_form.identifier.data)
                    scheduler.experiments.remove(registered_experiment)
                    self.session.commit()
                else:
                    registered_experiments.append({
                        'name'   : unicode(registered_experiment),
                        'form'   : remove_form,
                        'prefix' : prefix
                    })


        return self.render("admin-scheduler-create-ilab.html", form = form, back = back, registered_experiments = registered_experiments, add_form = add_form, create = scheduler is None)


    @expose('/edit/', ['GET', 'POST'])
    def edit_view(self):
        id = request.args.get('id')
        if id is None:
            flash("No id provided", "error")
            return redirect(url_for('.index_view'))
        scheduler = self.session.query(model.DbScheduler).filter_by(id = id).first()
        if scheduler is None:
            flash("Id provided does not exist", "error")
            return redirect(url_for('.index_view'))

        back = url_for('.index_view')
        config = json.loads(scheduler.config)
        if scheduler.scheduler_type == 'EXTERNAL_WEBLAB_DEUSTO':
            try:
                client = WebLabDeustoClient(config['base_url'])
                session_id = client.login(config['username'], config['password'])
                experiments = client.list_experiments(session_id)
            except:
                flash("Invalid configuration (or server down)", "error")
                traceback.print_exc()
                experiments = []
            obj = ExternalWebLabObject(name = scheduler.name, base_url = config['base_url'], username = config['username'], password = config['password'])
            return self._edit_weblab_view(back, obj, scheduler, experiments)
        elif scheduler.scheduler_type == 'PRIORITY_QUEUE':
            obj = PQueueObject(name = scheduler.name, randomize_instances = config['randomize_instances'])
            return self._edit_pqueue_view(back, obj, scheduler)
        elif scheduler.scheduler_type == 'ILAB_BATCH_QUEUE':
            form_kwargs = dict(name = scheduler.name, lab_server_url = config['lab_server_url'], identifier = config['identifier'], passkey = config['passkey'])
            return self._edit_ilab_view(back, form_kwargs, scheduler)

        return ":-O Editing"

    @expose('/resources/')
    def resources(self):
        return ":-)"

    @expose('/experiment/resources/')
    def experiment_resources(self):
        return ":-)"

def display_parameters(view, context, permission, p):
    parameters = u''
    for parameter in permission.parameters:
        parameters += u'%s = %s, ' % (parameter.permission_type_parameter, parameter.value)
    permission_str = u'%s(%s)' % (permission.permission_type, parameters[:-2])
    return permission_str


class GenericPermissionPanel(AdministratorModelView):
    """ Abstract class for UserPermissionPanel, GroupPermissionPanel and RolePermissionPanel """

    can_create = False

    column_descriptions = dict(permanent_id='A unique permanent identifier for a particular permission', )
    column_searchable_list = ('permanent_id', 'comments')
    column_formatters = dict(permission=display_parameters)
    column_filters = ( 'permission_type', 'permanent_id', 'date', 'comments' )
    column_sortable_list = ( 'permission', 'permanent_id', 'date', 'comments')
    column_list = ('permission', 'permanent_id', 'date', 'comments')
    form_overrides = dict(permanent_id=DisabledTextField, permission_type=DisabledTextField)

    def __init__(self, model, session, **kwargs):
        super(GenericPermissionPanel, self).__init__(model, session, **kwargs)


    def get_list(self, page, sort_column, sort_desc, search, filters, *args, **kwargs):
        # So as to sort descending, force sorting by 'id' and reverse the sort_desc
        if sort_column is None:
            sort_column = 'date'
            sort_desc = not sort_desc
        return super(GenericPermissionPanel, self).get_list(page, sort_column, sort_desc, search, filters, *args,
                                                            **kwargs)


    def on_model_change(self, form, permission):
        # TODO: use weblab.permissions directly
        req_arguments = {
            'experiment_allowed': ('experiment_permanent_id', 'experiment_category_id', 'time_allowed'),
            'admin_panel_access': ('full_privileges',),
            'access_forward': (),
        }
        opt_arguments = {
            'experiment_allowed': ('priority', 'initialization_in_accounting'),
            'admin_panel_access': (),
            'access_forward': (),
        }
        required_arguments = set(req_arguments[permission.permission_type])
        optional_arguments = set(opt_arguments[permission.permission_type])
        obtained_arguments = set([parameter.permission_type_parameter for parameter in permission.parameters])

        missing_arguments = required_arguments.difference(obtained_arguments)
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

        if permission.permission_type == 'experiment_allowed':
            exp_name = [parameter for parameter in permission.parameters if
                        parameter.permission_type_parameter == 'experiment_permanent_id'][0].value
            cat_name = [parameter for parameter in permission.parameters if
                        parameter.permission_type_parameter == 'experiment_category_id'][0].value
            time_allowed = \
                [parameter for parameter in permission.parameters if parameter.permission_type_parameter == 'time_allowed'][
                    0].value

            found = False
            for exp in self.session.query(model.DbExperiment).filter_by(name=exp_name).all():
                if exp.category.name == cat_name:
                    found = True
                    break
            if not found:
                raise Exception(u"Experiment not found: %s@%s" % (exp_name, cat_name))

            try:
                int(time_allowed)
            except:
                raise Exception("Time allowed must be a number (in seconds)")


class PermissionEditForm(InlineFormAdmin):
    def postprocess_form(self, form_class):
        form_class.permission_type_parameter = UnboundField(DisabledTextField)
        return form_class


class UserPermissionPanel(GenericPermissionPanel):
    column_filters = GenericPermissionPanel.column_filters + ('user',)
    column_sortable_list = GenericPermissionPanel.column_sortable_list + (('user', model.DbUser.login),)
    column_list = ('user', ) + GenericPermissionPanel.column_list

    inline_models = (PermissionEditForm(model.DbUserPermissionParameter),)

    INSTANCE = None

    def __init__(self, session, **kwargs):
        super(UserPermissionPanel, self).__init__(model.DbUserPermission, session, **kwargs)
        self.user_filter_number = get_filter_number(self, u'User.login')
        UserPermissionPanel.INSTANCE = self


class GroupPermissionPanel(GenericPermissionPanel):
    column_filters = GenericPermissionPanel.column_filters + ('group',)
    column_sortable_list = GenericPermissionPanel.column_sortable_list + (('group', model.DbGroup.name),)
    column_list = ('group', ) + GenericPermissionPanel.column_list

    inline_models = (PermissionEditForm(model.DbGroupPermissionParameter),)

    INSTANCE = None

    def __init__(self, session, **kwargs):
        super(GroupPermissionPanel, self).__init__(model.DbGroupPermission, session, **kwargs)

        self.group_filter_number = get_filter_number(self, u'Group.name')

        GroupPermissionPanel.INSTANCE = self


class RolePermissionPanel(GenericPermissionPanel):
    column_filters = GenericPermissionPanel.column_filters + ('role',)
    column_sortable_list = GenericPermissionPanel.column_sortable_list + (('role', model.DbRole.name),)
    column_list = ('role', ) + GenericPermissionPanel.column_list

    inline_models = (PermissionEditForm(model.DbRolePermissionParameter),)

    INSTANCE = None

    def __init__(self, session, **kwargs):
        super(RolePermissionPanel, self).__init__(model.DbRolePermission, session, **kwargs)

        self.role_filter_number = get_filter_number(self, u'Role.name')

        RolePermissionPanel.INSTANCE = self


class PermissionsForm(Form):
    permission_types = Select2Field(u"Permission type:",
                                    choices=[(permission_type, permission_type) for permission_type in
                                             permissions.permission_types], default=permissions.EXPERIMENT_ALLOWED)
    recipients = Select2Field(u"Type of recipient:", choices=[('user', 'User'), ('group', 'Group'), ('role', 'Role')],
                              default='group')


class PermissionsAddingView(AdministratorView):
    PERMISSION_FORMS = {}

    def __init__(self, session, **kwargs):
        self.session = session
        super(PermissionsAddingView, self).__init__(**kwargs)

    @expose(methods=['POST', 'GET'])
    def index(self):
        form = PermissionsForm()
        if form.validate_on_submit():
            if form.recipients.data == 'user':
                return redirect(url_for('.users', permission_type=form.permission_types.data))
            elif form.recipients.data == 'role':
                return redirect(url_for('.roles', permission_type=form.permission_types.data))
            elif form.recipients.data == 'group':
                return redirect(url_for('.groups', permission_type=form.permission_types.data))

        return self.render("admin-permissions.html", form=form)

    def _get_permission_form(self, permission_type, recipient_type, recipient_resolver, DbPermissionClass,
                             DbPermissionParameterClass):
        key = u'%s__%s' % (permission_type, recipient_type)
        if key in self.PERMISSION_FORMS:
            return self.PERMISSION_FORMS[key]()

        # Otherwise, generate it
        current_permission_type = permissions.permission_types[permission_type]

        session = self.session

        class ParentPermissionForm(Form):

            comments = TextField("Comments")
            recipients = Select2Field(recipient_type, description="Recipients of the permission")

            def get_permanent_id(self):
                recipient = recipient_resolver(self.recipients.data)
                return u'%s::%s' % (permission_type, recipient)

            def add_permission(self):
                recipient = recipient_resolver(self.recipients.data)
                db_permission = DbPermissionClass(recipient, permission_type, permanent_id=self.get_permanent_id(),
                                                  date=datetime.datetime.today(), comments=self.comments.data)
                session.add(db_permission)

                return db_permission

            def add_parameters(self, db_permission):
                for parameter in current_permission_type.parameters:
                    data = getattr(self, parameter.name).data
                    db_parameter = DbPermissionParameterClass(db_permission, parameter.name, data)
                    db_permission.parameters.append(db_parameter)
                    session.add(db_parameter)

            def self_register(self):
                db_permission = self.add_permission()
                self.add_parameters(db_permission)
                session.commit()

        ###################################################################################
        # 
        # If a permission requires a special treatment, this is where it should be placed
        # 
        if permission_type == permissions.EXPERIMENT_ALLOWED:

            class ParticularPermissionForm(ParentPermissionForm):
                parameter_list = ['experiment', 'time_allowed', 'priority', 'initialization_in_accounting']

                experiment = Select2Field(u'Experiment', description="Experiment")

                time_allowed = TextField(u'Time assigned', description="Measured in seconds",
                                         validators=[Required(), NumberRange(min=1)], default=100)
                priority = TextField(u'Priority', description="Priority of the user",
                                     validators=[Required(), NumberRange(min=0)], default=5)
                initialization_in_accounting = SelectField(u'Initialization',
                                                           description="Take initialization into account",
                                                           choices=[('1', 'Yes'), ('0', 'No')], default='1')


                def __init__(self, *args, **kwargs):
                    super(ParticularPermissionForm, self).__init__(*args, **kwargs)
                    choices = []
                    for exp in session.query(model.DbExperiment).all():
                        exp_id = u'%s@%s' % (exp.name, exp.category.name)
                        choices.append((exp_id, exp_id))
                    self.experiment.choices = choices

                def get_permanent_id(self):
                    recipient = recipient_resolver(self.recipients.data)
                    exp_name, cat_name = self.experiment.data.split('@')
                    return u'%s::%s@%s::%s' % (permission_type, exp_name, cat_name, recipient)

                def add_parameters(self, db_permission):
                    db_parameter = DbPermissionParameterClass(db_permission, permissions.TIME_ALLOWED,
                                                              self.time_allowed.data)
                    db_permission.parameters.append(db_parameter)
                    session.add(db_parameter)

                    db_parameter = DbPermissionParameterClass(db_permission, permissions.PRIORITY, self.priority.data)
                    db_permission.parameters.append(db_parameter)
                    session.add(db_parameter)

                    db_parameter = DbPermissionParameterClass(db_permission, permissions.INITIALIZATION_IN_ACCOUNTING,
                                                              self.initialization_in_accounting.data)
                    db_permission.parameters.append(db_parameter)
                    session.add(db_parameter)

                    exp_name, cat_name = self.experiment.data.split('@')

                    db_parameter = DbPermissionParameterClass(db_permission, permissions.EXPERIMENT_PERMANENT_ID,
                                                              exp_name)
                    db_permission.parameters.append(db_parameter)
                    session.add(db_parameter)

                    db_parameter = DbPermissionParameterClass(db_permission, permissions.EXPERIMENT_CATEGORY_ID,
                                                              cat_name)
                    db_permission.parameters.append(db_parameter)
                    session.add(db_parameter)


        ###################################################################################
        # 
        #  Otherwise, it is automatically generated
        # 
        else: # Auto-generate it by default
            parameters_code = """    parameter_list = %s\n""" % repr(
                [parameter.name for parameter in current_permission_type.parameters])
            for parameter in current_permission_type.parameters:
                parameters_code += """    %s = TextField(u"%s", description="%s", validators = [Required()])\n""" % (
                    parameter.name,
                    parameter.name.replace('_', ' ').capitalize(),
                    parameter.description )

            form_code = """class ParticularPermissionForm(ParentPermissionForm):\n""" + parameters_code

            context = {}
            context.update(globals())
            context.update(locals())

            exec form_code in context, context

            ParticularPermissionForm = context['ParticularPermissionForm']

        self.PERMISSION_FORMS[key] = ParticularPermissionForm
        return ParticularPermissionForm()

    def _check_permission_type(self, permission_type):
        current_permission_type = permissions.permission_types.get(permission_type, None)
        if current_permission_type is None:
            raise abort(400) # TODO:  show an error

    def _show_form(self, permission_type, recipient_type, recipients, recipient_resolver, DbPermissionClass,
                   DbPermissionParameterClass, back_url):
        current_permission_type = permissions.permission_types[permission_type]
        form = self._get_permission_form(permission_type, recipient_type, recipient_resolver, DbPermissionClass,
                                         DbPermissionParameterClass)
        form.recipients.choices = recipients

        if form.validate_on_submit():
            try:
                form.self_register()
            except:
                flash("Error saving data. May the permission be duplicated?")
                return self.render("admin-permission-create.html", form=form, fields=form.parameter_list,
                                   description=current_permission_type.description, permission_type=permission_type)
            return redirect(back_url)

        return self.render("admin-permission-create.html", form=form, fields=form.parameter_list,
                           description=current_permission_type.description, permission_type=permission_type)

    @expose('/users/<permission_type>/', methods=['GET', 'POST'])
    def users(self, permission_type):
        self._check_permission_type(permission_type)

        users = [(user.login, u'%s - %s' % (user.login, user.full_name)) for user in
                 self.session.query(model.DbUser).order_by(desc('id')).all()]

        recipient_resolver = lambda login: self.session.query(model.DbUser).filter_by(login=login).one()

        return self._show_form(permission_type, 'Users', users, recipient_resolver,
                               model.DbUserPermission, model.DbUserPermissionParameter,
                               get_full_url(UserPermissionPanel.INSTANCE.url))

    @expose('/groups/<permission_type>/', methods=['GET', 'POST'])
    def groups(self, permission_type):
        self._check_permission_type(permission_type)

        groups = [(g.name, g.name) for g in self.session.query(model.DbGroup).order_by(desc('id')).all()]

        recipient_resolver = lambda group_name: self.session.query(model.DbGroup).filter_by(name=group_name).one()

        return self._show_form(permission_type, 'Groups', groups, recipient_resolver,
                               model.DbGroupPermission, model.DbGroupPermissionParameter,
                               get_full_url(GroupPermissionPanel.INSTANCE.url))


    @expose('/roles/<permission_type>/', methods=['GET', 'POST'])
    def roles(self, permission_type):
        self._check_permission_type(permission_type)

        roles = [(r.name, r.name) for r in self.session.query(model.DbRole).order_by(desc('id')).all()]

        recipient_resolver = lambda role_name: self.session.query(model.DbRole).filter_by(name=role_name).one()

        return self._show_form(permission_type, 'Roles', roles, recipient_resolver,
                               model.DbRolePermission, model.DbRolePermissionParameter,
                               get_full_url(RolePermissionPanel.INSTANCE.url))


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


