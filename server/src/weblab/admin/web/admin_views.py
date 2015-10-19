from __future__ import print_function, unicode_literals

import os
import re
import sha
import sys
import time
import json
import random
import zipfile
import urlparse
import datetime
import traceback
import threading
import collections


import six

from weblab.core.web.logo import logo_impl
from weblab.core.i18n import gettext, lazy_gettext
from weblab.admin.util import password2sha, display_date
from weblab.util import data_filename

try:
    CLIENTS = json.load(open(data_filename(os.path.join('weblab', 'clients.json'))))
except:
    print("Error loading weblab/clients.json. Did you run weblab-admin upgrade? Check the file")
    raise

from wtforms import TextField, TextAreaField, PasswordField, SelectField, BooleanField, HiddenField, ValidationError
from wtforms.fields.core import UnboundField
from wtforms.fields.html5 import URLField, DateField, EmailField
from wtforms.validators import Email, Regexp, Required, NumberRange, URL

from sqlalchemy.sql.expression import desc
from sqlalchemy.orm import joinedload

from werkzeug import secure_filename

from flask import Markup, request, redirect, abort, url_for, flash, Response

from flask.ext.wtf import Form
from flask.ext.wtf.file import FileField, FileAllowed

from flask.ext.admin.contrib.sqla.filters import FilterEqual
from flask.ext.admin import expose
from flask.ext.admin.form import Select2Field
from flask.ext.admin.actions import action
from flask.ext.admin.model.form import InlineFormAdmin
from weblab.admin.web.util import WebLabModelView, WebLabAdminIndexView, WebLabBaseView, WebLabFileAdmin

import weblab.configuration_doc as configuration_doc
import weblab.db.model as model
import weblab.permissions as permissions

from weblab.admin.web.fields import DisabledTextField, VisiblePasswordField, RecordingQuerySelectField

try:
    from weblab.admin.ldap_gateway import LdapGateway

    LdapGatewayClass = LdapGateway
except ImportError:
    LdapGatewayClass = None

from weblab.core.coordinator.clients.weblabdeusto import WebLabDeustoClient

class AdminAuthnMixIn(object):
    @property
    def app_instance(self):
        return self.admin.weblab_admin_app

    def before_request(self):
        self.request_context.is_admin = self.app_instance.is_admin()

    def is_accessible(self):
        return self.request_context.is_admin

    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            if self.app_instance.get_user_information() is not None:
                return redirect(url_for('not_allowed'))
            return redirect(url_for('core_webclient.login', next=request.url))

        return super(AdminAuthnMixIn, self)._handle_view(name, **kwargs)

class AdministratorView(AdminAuthnMixIn, WebLabBaseView):
    pass


class AdministratorModelView(AdminAuthnMixIn, WebLabModelView):
    pass

class BaseAdministratorFileAdmin(AdminAuthnMixIn, WebLabFileAdmin):
    pass

class AdministratorFileAdmin(BaseAdministratorFileAdmin):
    @action("unzip", lazy_gettext("Unzip"), confirmation = lazy_gettext("Are you sure you want to unzip this file? Every file with the same name will be overriden"))
    def unzip(self, files):
        errors = False
        for filename in files:
            if not filename.lower().endswith('.zip'):
                flash(gettext('File "%(name)s" does not have a .zip extension.', name=filename), 'error')
                errors = True
        if errors:
            return
        for filename in files:
            try:
                with zipfile.ZipFile(os.path.join(self.base_path, secure_filename(filename))) as zfile:
                    target_directory = os.path.join(self.base_path, os.path.dirname(secure_filename(filename)))
                    try:
                        zfile.extractall(target_directory)
                    except Exception as e:
                        flash(gettext('Unable to extract file: %(name)s: %(error)s', name=filename, error=unicode(e)), 'error')
            except zipfile.BadZipfile:
                flash(gettext('Unable to extract file: %(name)s: it is not a zip file', name=filename), 'error')

        if files:
            return_dir = os.path.dirname(secure_filename(files[0]))
            if return_dir:
                return redirect(url_for('.index', path=return_dir))

SAME_DATA = object()

def _get_instance(cur_view, klass):
    # TODO: find a better way to find the klass on admin
    for view in cur_view.admin._views:
        if isinstance(view, klass):
            return view
    
    # For example, in the profile logs view, you may not access the Experiments panel
    if cur_view.admin.app.debug:
        print("ERROR", "INSTANCE NOT FOUND FOR {0} and {1}".format(cur_view, klass))


def show_link(cur_view, klass, filter_info, view_name=lazy_gettext('View')):
    """ Given the current view, a class (e.g. UsersPanel) and a set of filters (in the form of dictionary), provide a link with the name provided.

    Examples: 
        show_link(self, UsersPanel, { 'login' : 'student1' }) -> link to UsersPanel filtering by login = 'student1'
        show_link(self, UsersPanel, { ('Role', 'name') : 'administrator' }) -> link to UsersPanel filtering by Role.name = 'administrator'
        show_link(self, ExperimentPanel, { 'name : 'ud-pld', ('ExperimentCategory', 'name') : 'PLD experiments' }) -> link to UsersPanel with two filters
        show_link(self, UsersPanel, { 'login' : 'student1' }, SAME_DATA) -> link to UsersPanel filtering by login = 'student1', using 'student1' as visible data
    """
    if view_name == SAME_DATA:
        view_name = filter_info.values()[0]

    instance = _get_instance(cur_view, klass)
    if instance is None:
        return view_name
    
    filters = {
        # filter_key : filter_id
    }
    for pos, flt in enumerate(instance.get_filters()):
        if isinstance(flt, FilterEqual):
            for filter_key in filter_info:
                if isinstance(filter_key, unicode):
                    filter_table = cur_view.model.__tablename__
                    filter_column = filter_key
                else:
                    filter_table, filter_column = filter_key
                if flt.column.name in filter_column and flt.column.table.name == filter_table:
                    filters[filter_key] = pos

    if not filters:
        return "Error; filter not found"
    
    kwargs = {}
    for pos, (filter_key, filter_id) in enumerate(six.iteritems(filters)):
        kwargs['flt{0}_{1}'.format(pos, filter_id)] = filter_info[filter_key]

    link = url_for(instance.endpoint + '.index_view', **kwargs)
    return Markup("<a href='{0}'>{1}</a>".format(link, view_name))


class UserAuthForm(InlineFormAdmin):
    def postprocess_form(self, form_class):
        form_class.auth.field_class = RecordingQuerySelectField
        form_class.configuration = UnboundField(VisiblePasswordField,
                                                description=lazy_gettext('Detail the password (DB), Facebook ID -the number- (Facebook), OpenID identifier.'))
        return form_class


LOGIN_REGEX = '^[A-Za-z0-9\._-][A-Za-z0-9\._-][A-Za-z0-9\._-][A-Za-z0-9\._-]*$'




class UsersPanel(AdministratorModelView):
    column_list = ('role', 'login', 'full_name', 'email', 'groups', 'logs', 'permissions')
    column_filters = ( 'full_name', 'login', 'role', 'email', model.DbGroup.name ) 
    column_searchable_list = ('full_name', 'login')
    column_labels = dict(role=lazy_gettext("Role"), login=lazy_gettext("Login"), full_name=lazy_gettext("Full name"), email=lazy_gettext("e-mail"), groups=lazy_gettext("Groups"), logs=lazy_gettext("Logs"), permissions=lazy_gettext("Permissions"), auths=lazy_gettext("Credentials"))

    form_excluded_columns = 'avatar', 'experiment_uses', 'permissions'
    form_args = dict(email=dict(validators=[Email()]), login=dict(validators=[Regexp(LOGIN_REGEX)]))

    column_descriptions = dict(login=lazy_gettext('Username (all letters, dots and numbers)'),
                               full_name=lazy_gettext('First and Last name'),
                               email=lazy_gettext('Valid e-mail address'),
                               avatar=lazy_gettext('Not implemented yet, it should be a public URL for a user picture.'),
                               auths=lazy_gettext("User credentials: a password or alternative mechanisms"))

    inline_models = (UserAuthForm(model.DbUserAuth),)

    column_formatters = dict(
        role=lambda v, c, u, p: show_link(v, UsersPanel, { ('Role', 'name'): u.role.name }, SAME_DATA),
        groups=lambda v, c, u, p: show_link(v, GroupsPanel, { 'login': u.login }),
        logs=lambda v, c, u, p: show_link(v, UserUsedExperimentPanel, { 'login': u.login }),
        permissions=lambda v, c, u, p: show_link(v, UserPermissionPanel, { 'login': u.login }),
    )

    def __init__(self, session, **kwargs):
        super(UsersPanel, self).__init__(model.DbUser, session, **kwargs)
        self.local_data = threading.local()

    def scaffold_filters(self, name):
        filters = super(UsersPanel, self).scaffold_filters(name)

        if "DbGroup" in unicode(name):
            for key in self._filter_joins:
                self._filter_joins[key].insert(0, model.t_user_is_member_of)

        return filters

    def edit_form(self, obj=None):
        form = super(UsersPanel, self).edit_form(obj)
        self.local_data.authentications = {}
        if obj is not None:
            for auth_instance in obj.auths:
                self.local_data.authentications[auth_instance.id] = (
                    auth_instance.auth.name, auth_instance.configuration)
        return form

    def on_model_change(self, form, user_model, is_created):
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
            if len(password) < 4: # "demo" should be a valid password
                raise ValidationError(gettext("Password too short"))
            auth_instance.configuration = password2sha(password)
        elif auth_instance.auth.auth_type.name.lower() == 'facebook':
            try:
                int(auth_instance.configuration)
            except:
                raise ValidationError(gettext("Use a numeric ID for Facebook"))
                # Other validations would be here


class UsersBatchForm(Form):
    """This form enables adding multiple users in a single action."""

    users = TextAreaField(lazy_gettext(u"Users:"), description=lazy_gettext(u"Add the user list using the detailed format"))
    new_group = TextField(lazy_gettext(u"New group:"))
    existing_group = Select2Field(lazy_gettext(u"Existing group:"))


class LdapUsersBatchForm(UsersBatchForm):
    ldap_user = TextField(lazy_gettext(u"Your LDAP username:"))
    ldap_password = PasswordField(lazy_gettext(u"Your LDAP password:"))
    ldap_domain = TextField(lazy_gettext(u"Your domain:"))
    ldap_system = SelectField(lazy_gettext(u"LDAP gateway:"))


class FormException(Exception):
    """ Used to know that there was an error parsing the form """


class UsersAddingView(AdministratorView):
    def __init__(self, session, **kwargs):
        self.session = session
        super(UsersAddingView, self).__init__(**kwargs)

    @expose()
    def index(self):
        # TODO: enable / disable OpenID and LDAP depending on if it is available
        return self.render("admin/admin-add-students-select.html")

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
                    flash(gettext("Line %(n)s (%(line)s) does not have %(columns)s columns (%(cur_columns)s found)", n=n, line=line, columns=len(columns), cur_columns=len(cur_columns)))
                    errors = True
                    continue

                cur_error = False
                for column, fmt in zip(cur_columns, columns):
                    if fmt == 'login':
                        regex = re.compile(LOGIN_REGEX)
                        if not regex.match(column):
                            flash(gettext("Login %(column)s contains invalid characters", column=column))
                            cur_error = True
                        existing_user = self.session.query(model.DbUser).filter_by(login=column).first()
                        if existing_user is not None:
                            flash(gettext("User %(column)s already exists", column=column))
                            # The user exists already. However, we do not consider this an error.
                            # That way we can add groups for which some users exist already.
                            # cur_error = True
                    elif fmt == 'mail':
                        # Not exhaustive
                        regex = re.compile('^.*@.*\..*')
                        if not regex.match(column):
                            flash(gettext("Invalid e-mail address: %(column)s", column=column))
                            cur_error = True
                if cur_error:
                    errors = True
                else:
                    rows.append(cur_columns)

        if not errors and len(rows) == 0:
            flash(gettext("No user provided"))
            raise FormException()

        if errors:
            flash(gettext("No user added due to errors detailed"), 'error')
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
            user_auth = model.DbUserAuth(user=user, auth=auth, configuration=password2sha(password))
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
            flash(gettext("Error: ldap libraries not installed"))
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
            flash(gettext("Error retrieving users from the LDAP server. Contact your administrator."))
            raise FormException()

        if len(users_data) != len(rows):
            retrieved_logins = [user['login'] for user in users_data]
            missing_logins = []
            for login in rows:
                if login not in retrieved_logins:
                    missing_logins.append(login)
            all_missing_logins = ', '.join(missing_logins)
            flash(gettext("Error: could not find the following users: %(users)s", users=all_missing_logins))
            raise FormException()

        if len(users_data) == 0:
            flash(gettext("No user processed"))
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
        description = gettext("In this case, you need to provide the user's login, full_name, e-mail address, and password, in this order and separated by commas.")
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
                    traceback.print_exc()
                    flash("Errors occurred while adding users")
                    self.session.rollback()
                else:
                    return self.render("admin/admin-add-students-finished.html", users=users, group_name=group_name)
        elif not form.users.data:
            form.users.data = example
        return self.render("admin/admin-add-students.html", form=form, description=description, example=example)

    @expose('/ldap/', methods=['GET', 'POST'])
    def add_ldap(self):
        form = self._get_form(LdapUsersBatchForm)

        ldap_auth_type = self.session.query(model.DbAuthType).filter_by(name='LDAP').first()
        if ldap_auth_type is None:
            return gettext("LDAP not registered as an Auth Type")

        form.ldap_system.choices = [(auth.name, auth.name) for auth in ldap_auth_type.auths]
        description = gettext("In this case, you only need to provide the username of the users, separated by spaces or new lines. WebLab-Deusto will retrieve the rest of the information from the LDAP system.")
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
                    traceback.print_exc()
                    flash("Errors occurred while adding users")
                    self.session.rollback()
                else:
                    return self.render("admin/admin-add-students-finished.html", users=users, group_name=group_name)
        elif not form.users.data:
            form.users.data = example
        return self.render("admin/admin-add-students.html", form=form, description=description, example=example)

    @expose('/openid/', methods=['GET', 'POST'])
    def add_openid(self):
        form = self._get_form()
        description = gettext("In this case, you only need to provide the username of the user, the full name, e-mail address and OpenID, in this order and separated by commas.")
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
                    traceback.print_exc()
                    flash("Errors occurred while adding users")
                    self.session.rollback()
                else:
                    return self.render("admin/admin-add-students-finished.html", users=users, group_name=group_name)
        elif not form.users.data:
            form.users.data = example
        return self.render("admin/admin-add-students.html", form=form, description=description, example=example)


class GroupsPanel(AdministratorModelView):
    column_searchable_list = ('name',)
    column_list = ('name', 'parent', 'users', 'permissions')
    column_labels = dict(name=lazy_gettext("Name"), parent=lazy_gettext("Parent"), users=lazy_gettext("Users"), permissions=lazy_gettext("Permissions"))
    form_columns = ('name', 'parent', 'users')

    column_filters = ( 'name', model.DbUser.login, model.DbUser.full_name )

    column_formatters = dict(
        users=lambda v, c, g, p: show_link(v, UsersPanel, {'name': g.name}),
        permissions=lambda v, c, g, p: show_link(v, GroupPermissionPanel, {'name': g.name}),
    )

    def __init__(self, session, **kwargs):
        super(GroupsPanel, self).__init__(model.DbGroup, session, **kwargs)

    def scaffold_filters(self, name):
        filters = super(GroupsPanel, self).scaffold_filters(name)

        if "DbUser" in unicode(name):
            for key in self._filter_joins:
                self._filter_joins[key].insert(0, model.t_user_is_member_of)

        return filters

class DefaultAuthenticationForm(Form):
    name     = TextField(lazy_gettext(u"Name:"), description=lazy_gettext("Authentication name"), validators = [ Required() ])
    priority = Select2Field(lazy_gettext(u"Priority:"), description=lazy_gettext("Order followed by the authentication system. Authentication mechanism with priority 1 will be checked before the one with priority 2."), validators = [ Required() ])

def generate_generic_config(form):
    return ''

def fill_generic_config(form, config):
    pass

class LdapForm(DefaultAuthenticationForm):
    ldap_uri = TextField(lazy_gettext(u'LDAP server'), description=lazy_gettext("LDAP server URL"), validators = [ URL(), Required() ])
    domain = TextField(lazy_gettext(u"Domain"), description=lazy_gettext("Domain"), validators = [ Required() ])
    base = TextField(lazy_gettext(u"Base"), description=lazy_gettext("Base, e.g.: dc=deusto,dc=es"), validators = [ Required() ])

    def validate_ldap_uri(form, ldap_uri):
        if ';' in ldap_uri.data:
            raise ValidationError(gettext("Character ; not supported"))

    validate_domain = validate_base = validate_ldap_uri

def generate_ldap_config(form):
    return 'ldap_uri=%(ldap_uri)s;domain=%(domain)s;base=%(base)s' % {
            'ldap_uri' : form.ldap_uri.data,
            'domain' : form.domain.data,
            'base' : form.base.data,
        }

def fill_ldap_config(form, config):
    ldap_uri, domain, base = config.split(';')
    form.ldap_uri.data = ldap_uri[len('ldap_uri='):]
    form.domain.data   = domain[len('domain='):]
    form.base.data     = base[len('base='):]

class TrustedIpForm(DefaultAuthenticationForm):
    ip_addresses = TextField(lazy_gettext(u'IP addresses'), description=lazy_gettext("Put an IP address or set of IP addresses separated by commas"), validators = [ Required() ])

def generate_trusted_ip_config(form):
    return form.ip_addresses.data

def fill_trusted_ip_config(form, config):
    pass

class AuthsPanel(AdministratorModelView):
    column_searchable_list = ('name',)
    column_filters = ( ('name', 'configuration', 'priority') )
    action_disallowed_list = ['delete']
    column_labels = dict(name=lazy_gettext("Name"), configuration=lazy_gettext("Configuration"), priority=lazy_gettext("Priority"))
    
    CONFIGURABLES = {
        'LDAP' : {
            'form': LdapForm,
            'fields': ['ldap_uri', 'domain', 'base'],
            'generate_func': generate_ldap_config,
            'fill_func': fill_ldap_config,
        }, 
        'TRUSTED-IP-ADDRESSES' : {
            'form': TrustedIpForm,
            'fields': ['ip_addresses'],
            'generate_func': generate_trusted_ip_config,
            'fill_func': fill_trusted_ip_config,
        },
    }

    def __init__(self, session, **kwargs):
        super(AuthsPanel, self).__init__(model.DbAuth, session, **kwargs)

    @expose('/create/')
    def create_view(self, *args, **kwargs):
        auth_types = self.session.query(model.DbAuthType).options(joinedload('auths')).all()

        possible_auth_types = [
            [ auth_type, True, '' ]
            for auth_type in auth_types
        ]
        
        for auth_type_pack in possible_auth_types:
            auth_type = auth_type_pack[0]
            if auth_type.name in self.CONFIGURABLES:
                pass # Configurables can 
            else:
                if len(auth_type.auths) > 0:
                    auth_type_pack[1] = False
                    auth_type_pack[2] = gettext("Already created")
        
        return self.render("admin/admin-auths-create.html", auth_types = possible_auth_types)

    @expose('/create/<auth_type_name>/', methods = ['GET', 'POST'])
    def create_auth_view(self, auth_type_name):
        auth_type = self.session.query(model.DbAuthType).filter_by(name = auth_type_name).options(joinedload('auths')).first()

        if not auth_type:
            return gettext("Auth type not found")

        if len(auth_type.auths) > 0 and auth_type_name not in self.CONFIGURABLES:
            return gettext("Existing auth type")

        priorities = [ auth.priority for auth in self.session.query(model.DbAuth).filter_by().all() ]
        priority_choices = [ (str(priority), str(priority)) for priority in range(1, 20) if priority not in priorities ]

        fields = ['name', 'priority']
        if auth_type_name in self.CONFIGURABLES:
            form_config = self.CONFIGURABLES[auth_type_name]
            form = form_config['form']()
            fields.extend(form_config['fields'])
            generate_func = form_config['generate_func']
        else:
            form = DefaultAuthenticationForm()
            generate_func = generate_generic_config

        form.priority.choices = priority_choices
        
        if form.validate_on_submit():
            configuration = generate_func(form)
            if self.session.query(model.DbAuth).filter_by(name = form.name.data).first():
                form.name.errors = [gettext('Name already taken')]
            else:
                auth = model.DbAuth(auth_type = auth_type, name = form.name.data, priority = int(form.priority.data), configuration = configuration)
                self.session.add(auth)
                self.session.commit()
                return redirect(url_for('.index_view'))

        form.name.data = auth_type_name
        return self.render("admin/admin-auths-create-individual.html", auth_type_name = auth_type_name, form = form, fields = fields, back_link = url_for('.create_view'))

    @expose('/edit/', methods = ['GET','POST'])
    def edit_view(self, *args, **kwargs):
        auth = self.session.query(model.DbAuth).filter_by(id = request.args.get('id', -1)).first()
        if auth is None:
            return gettext("Element not found")

        if auth.auth_type.name == 'DB':
            flash(gettext("Can't modify the DB authentication mechanism"))
            return redirect(url_for('.index_view'))

        priorities = [ auth.priority for auth in self.session.query(model.DbAuth).filter_by().all() ]
        priority_choices = [ (str(priority), str(priority)) for priority in range(1, 20) if priority == auth.priority or priority not in priorities ]

        auth_type_name = auth.auth_type.name

        fields = ['name', 'priority']
        if auth_type_name in self.CONFIGURABLES:
            form_config = self.CONFIGURABLES[auth_type_name]
            form = form_config['form']()
            fields.extend(form_config['fields'])
            fill_func = form_config['fill_func']
            generate_func = form_config['generate_func']
        else:
            form = DefaultAuthenticationForm()
            fill_func = fill_generic_config
            generate_func = generate_generic_config
        
        form.priority.choices = priority_choices
        if form.validate_on_submit():
            configuration = generate_func(form)
            existing_auth_name = self.session.query(model.DbAuth).filter_by(name = form.name.data).first()
            if existing_auth_name.id != auth.id:
                form.name.errors = [gettext('Name already taken')]
            else:
                auth.name = form.name.data
                auth.priority = int(form.priority.data)
                auth.configuration = configuration
                self.session.add(auth)
                self.session.commit()
                return redirect(url_for('.index_view'))

        form.name.data = auth.name
        form.priority.data = str(auth.priority)
        fill_func(form, auth.configuration)

        return self.render("admin/admin-auths-create-individual.html", auth_type_name = auth_type_name, form = form, fields = fields, back_link = url_for('.index_view'))

    def on_model_delete(self, auth):
        if auth.auth_type.name == 'DB':
            raise ValidationError(gettext("Can't delete this authentication system"))


class UserUsedExperimentPanel(AdministratorModelView):
    can_delete = False
    can_edit = False
    can_create = False

    column_searchable_list = ('origin',)
    column_sortable_list = (
        'id', ('user', model.DbUser.login), ('experiment', model.DbExperiment.id), 'start_date',
        'end_date', 'origin', 'coord_address')
    column_list = ( 'user', 'experiment', 'start_date', 'end_date', 'origin', 'coord_address', 'details')
    column_filters = ( 'user', 'start_date', 'end_date', 'experiment', 'origin', 'coord_address', 'experiment.category')
    column_labels = dict(user=lazy_gettext("User"), experiment=lazy_gettext("Experiment"), start_date=lazy_gettext("Start date"), end_date=lazy_gettext("End date"), 
                        origin=lazy_gettext("Origin"), coord_address=lazy_gettext("Coord address"), details=lazy_gettext("Details"))

    column_formatters = dict(
        user=lambda v, c, uue, p: show_link(v, UsersPanel, {('User', 'login'): uue.user.login}, SAME_DATA),
        experiment=lambda v, c, uue, p: show_link(v, ExperimentPanel, { ('Experiment', 'name') : uue.experiment.name, ('ExperimentCategory', 'name') : uue.experiment.category.name }, uue.experiment),
        start_date=lambda v,c, uue, p: display_date(uue.start_date),
        end_date=lambda v,c, uue, p: display_date(uue.end_date),
        details=lambda v, c, uue, p: Markup('<a href="%s">%s</a>' % (url_for('.detail', id=uue.id), gettext("Details"))),
    )

    action_disallowed_list = ['create', 'edit', 'delete']

    def __init__(self, files_directory, session, **kwargs):
        super(UserUsedExperimentPanel, self).__init__(model.DbUserUsedExperiment, session, **kwargs)

        self.files_directory = files_directory

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
            flash(gettext("File not stored"))
            return self.render("error.html",
                               message=gettext("The file has not been stored. Check the %(config)s configuration value.", config=configuration_doc.CORE_STORE_STUDENTS_PROGRAMS))

        file_path = os.path.join(self.files_directory, uf.file_sent)
        if os.path.exists(file_path):
            content = open(file_path).read()
            return Response(content, headers={'Content-Type': 'application/octstream',
                                              'Content-Disposition': 'attachment; filename=file_%s.bin' % id})
        else:
            if os.path.exists(self.files_directory):
                flash(gettext("Wrong configuration or file deleted"))
                return self.render("error.html",
                                   message=gettext("The file was stored, but now it is not reachable. Check the %(config)s property.", config=configuration_doc.CORE_STORE_STUDENTS_PROGRAMS_PATH))
            else:
                flash(gettext("Wrong configuration"))
                return self.render("error.html",
                                   message=gettext("The file was stored, but now it is not reachable. The %(config)s directory does not exist.", config=configuration_doc.CORE_STORE_STUDENTS_PROGRAMS_PATH))


class ExperimentCategoryPanel(AdministratorModelView):
    column_searchable_list = ('name',)
    column_list = ('name', 'experiments')
    column_labels = dict(name=lazy_gettext("Name"), experiments=lazy_gettext("Experiments"))
    column_filters = ( 'name', )
    form_excluded_columns = ('experiments',)

    column_formatters = dict(
        experiments=lambda v, co, c, p: show_link(v, ExperimentPanel, { 'name' : c.name })
    )

    def __init__(self, session, **kwargs):
        super(ExperimentCategoryPanel, self).__init__(model.DbExperimentCategory, session, **kwargs)

class ExperimentCreationForm(Form):
    category = Select2Field(lazy_gettext(u"Category"), validators = [ Required() ])
    name = TextField(lazy_gettext("Name"), description = lazy_gettext("Name for this experiment"), validators = [Required()])
    client = Select2Field(lazy_gettext("Client"), description = lazy_gettext("Client to be used"), default = 'blank', validators = [ Required() ])
    start_date = DateField(lazy_gettext("Start date"), description = lazy_gettext("When the laboratory is going to start being used"))
    end_date = DateField(lazy_gettext("End date"), description = lazy_gettext("When the laboratory is not going to be used anymore"))

    # Client parameters
    experiment_info_description = TextField("experiment.info.description", description=lazy_gettext("Experiment description"))
    html = TextField("html", description = lazy_gettext("HTML to be displayed under the experiment"))
    experiment_info_link = URLField("experiment.info.link", description = lazy_gettext("Link to be provided next to the lab (e.g., docs)"))
    experiment_picture = TextField("experiment.picture", description = lazy_gettext("Address to a logo of the laboratory"))
    experiment_reserve_button_shown = BooleanField("experiment.reserve.button.shown", description = lazy_gettext("Whether it should show the reserve button (unless you're sure, leave this set)"), default = True)

ALREADY_PROVIDED_CLIENT_PARAMETERS = ('experiment.info.description', 'html', 'experiment.info.link', 'experiment.reserve.button.shown', 'experiment.picture')

def get_js_client_parameters():
    clients = {}
    for client, value in CLIENTS.iteritems():
        new_parameters = []
        for parameter, parameter_value in value['parameters'].iteritems():
            if parameter not in ALREADY_PROVIDED_CLIENT_PARAMETERS:
                new_parameters.append({
                    'name' : parameter,
                    'type' : parameter_value['type'],
                    'description' : parameter_value['description'],
                })
        clients[client] = new_parameters
                
    return json.dumps(clients, indent = 4)

class ExperimentPanel(AdministratorModelView):

    column_searchable_list = ('name','category.name','client')
    column_list = ('category', 'name', 'client', 'start_date', 'end_date', 'uses')
    column_labels = dict(category=lazy_gettext("Category"), name=lazy_gettext("Name"), client=lazy_gettext("Client"), start_date=lazy_gettext("Start date"), end_date=lazy_gettext("End date"), uses=lazy_gettext("Uses"))
    form_excluded_columns = 'user_uses',
    column_filters = ('name', 'category')
    form_overrides = dict( client = Select2Field )

    column_formatters = dict(
        category=lambda v, c, e, p: show_link(v, ExperimentCategoryPanel, { ('ExperimentCategory', 'name'): e.category.name }, SAME_DATA),
        uses=lambda v, c, e, p: show_link(v, UserUsedExperimentPanel, { 'name' : e.name, ('ExperimentCategory', 'name') : e.category.name }),
    )

    def __init__(self, session, **kwargs):
        super(ExperimentPanel, self).__init__(model.DbExperiment, session, **kwargs)

    def _create_form(self, obj):
        form = ExperimentCreationForm(formdata = request.form, obj = obj)
        form.category.choices = [ (cat.name, cat.name) for cat in self.session.query(model.DbExperimentCategory).order_by(desc('id')).all() ]
        form.client.choices = [ (c, c) for c in CLIENTS ]
        return form

    def _get_parameters(self, client_name):
        return CLIENTS.get(client_name, {}).get('parameters', [])

    def _extract_form_parameters(self):
        static_parameters = []
        dynamic_parameters = []

        client = request.form.get('client')
        existing_client_parameters = self._get_parameters(client)

        errors = False

        for key in sorted(request.form.keys()):
            if key.startswith('parameters_'):
                value = request.form.get(u'value_' + key, 'false')
                name = request.form[u'name_' + key]
                ptype = existing_client_parameters[name]['type']
                if ptype == 'bool':
                    value = value.lower() in ('on', 'true')
                static_parameters.append({
                    'name'  : name,
                    'type'  : ptype,
                    'value' : value,
                    'error' : None
                })
            elif key.startswith('dynamic_'):
                value = request.form.get(u'value_' + key, 'false')
                name = request.form[u'name_' + key]
                ptype = request.form[u'type_' + key]
                if ptype == 'bool':
                    value = value.lower() in ('on', 'true')
                dynamic_parameters.append({
                    'name'  : name,
                    'type'  : ptype,
                    'value' : value,
                    'error' : None
                })

        all_parameters = static_parameters + dynamic_parameters

        # Check that you don't put a string on an integer or so
        # And that there must be a name
        for parameter in all_parameters:
            if not parameter['name']:
                parameter['error'] = gettext("Empty property name")
                errors = True

            if parameter['value']:
                try:
                    if parameter['type'] == 'integer':
                        int(parameter['value'])
                    elif parameter['type'] == 'floating':
                        float(parameter['value'])
                except ValueError:
                    parameter['error'] = gettext("Invalid %(type_name)s", type_name=parameter['type'])
                    errors = True
        
        # Check that you don't use an existing name
        for pos, parameter in enumerate(all_parameters):
            if parameter['name'] in ALREADY_PROVIDED_CLIENT_PARAMETERS:
                parameter['error'] = lazy_gettext("Repeated name!")
                errors = True

            for parameter2 in all_parameters[pos + 1:]:
                if parameter['name'] == parameter2['name']:
                    parameter['error'] = gettext("Repeated name!")
                    parameter2['error'] = gettext("Repeated name!")
                    errors = True

        return static_parameters, dynamic_parameters, errors

    @expose('/new/', methods = ['GET', 'POST'] )
    def create_view(self, *args, **kwargs):
        form = self._create_form(obj = None)

        if request.method == 'POST':
            static_parameters, dynamic_parameters, errors = self._extract_form_parameters()
            if form.validate_on_submit() and not errors:
                db_cat = self.session.query(model.DbExperimentCategory).filter_by(name = form.category.data).first()
                if db_cat is None:
                    form.category.errors = [gettext("Category doesn't exist")]
                else:
                    existing_exp = self.session.query(model.DbExperiment).filter_by(name = form.name.data, category = db_cat).first()
                    if existing_exp:
                        form.name.errors = [gettext("Name already taken")]
                    else:
                        # Everything correct
                        db_exp = model.DbExperiment(name = form.name.data, category = db_cat,start_date = form.start_date.data, end_date = form.end_date.data, client = form.client.data)
                        self.session.add(db_exp)

                        for client_param in ALREADY_PROVIDED_CLIENT_PARAMETERS:
                            field = getattr(form, client_param.replace('.', '_'))
                            if field.data or field.data == False:
                                # There is no integer
                                dtype = 'bool' if isinstance(field.data, bool) else 'string'
                                db_param = model.DbExperimentClientParameter(db_exp, 
                                        parameter_name = client_param, parameter_type = dtype, value = unicode(field.data))
                                self.session.add(db_param)

                        for p in (static_parameters + dynamic_parameters):
                            db_param = model.DbExperimentClientParameter(db_exp, 
                                    parameter_name = p['name'], parameter_type = p['type'], value = unicode(p['value']))
                            self.session.add(db_param)
                        
                        try:
                            self.session.commit()
                        except:
                            self.session.rollback()
                            traceback.print_exc()
                            flash(gettext("Error storing data in the database"), "error")
                        else:
                            return redirect(url_for('.index_view'))
        else:
            now = datetime.datetime.now()
            default_start_date = now
            default_end_date = now.replace(year = now.year + 10)

            form.start_date.data = default_start_date
            form.end_date.data = default_end_date
            static_parameters = []
            dynamic_parameters = []

        return self.render("admin/admin-add-experiment.html", form = form, client_parameters = get_js_client_parameters(),
                                static_parameters = json.dumps(static_parameters, indent = 4), 
                                dynamic_parameters = json.dumps(dynamic_parameters, indent = 4))

    @expose('/edit/', methods = ['GET', 'POST'])
    def edit_view(self):
        exp_id = request.args.get('id', -1)
        db_exp = self.session.query(model.DbExperiment).filter_by(id = exp_id).first()
        if not db_exp:
            return gettext("Experiment not found")

        form = self._create_form(obj = db_exp)

        dynamic_parameters = []
        static_parameters = []

        if request.method == 'GET':
            existing_client_parameters = self._get_parameters(db_exp.client)

            for parameter in db_exp.client_parameters:
                param_obj = {
                    'name'  : parameter.parameter_name,
                    'type'  : parameter.parameter_type,
                    'value' : parameter.value,
                    'error' : None
                }
                if parameter.parameter_type == 'bool':
                    param_obj['value'] = parameter.value.lower() in ('true', 'on')

                if parameter.parameter_name in ALREADY_PROVIDED_CLIENT_PARAMETERS:
                    field = getattr(form, parameter.parameter_name.replace('.','_'))
                    field.data = param_obj['value']
                elif parameter.parameter_name in existing_client_parameters:
                    static_parameters.append(param_obj)
                else:
                    dynamic_parameters.append(param_obj)
        else:
            static_parameters, dynamic_parameters, errors = self._extract_form_parameters()
            if form.validate_on_submit() and not errors:
                db_cat = self.session.query(model.DbExperimentCategory).filter_by(name = form.category.data).first()
                if db_cat:
                    db_exp.category = db_cat
                    db_exp.name = form.name.data
                    db_exp.start_date = form.start_date.data
                    db_exp.end_date = form.end_date.data
                    db_exp.client = form.client.data

                    already_provided_parameters = []
                    for param_name in ALREADY_PROVIDED_CLIENT_PARAMETERS:
                        field = getattr(form, param_name.replace('.', '_'))
                        if field.data or field.data == False:
                            dtype = 'bool' if isinstance(field.data, bool) else 'string'
                            already_provided_parameters.append({ 'name' : param_name, 'type' : dtype, 'value' : field.data })

                    all_parameters = already_provided_parameters + static_parameters + dynamic_parameters
                    all_parameters_by_name = {}
                    for param in all_parameters[::-1]:
                        all_parameters_by_name[param['name']] = param

                    existing_parameters = db_exp.client_parameters
                    existing_parameters_by_name = {}
                    for param in existing_parameters:
                        existing_parameters_by_name[param.parameter_name] = param

                    # First remove parameters not existing anymore
                    for existing_param in existing_parameters_by_name:
                        if existing_param not in all_parameters_by_name:
                            self.session.delete(existing_parameters_by_name[existing_param])
                    
                    # Then update existing parameters and add new parameters
                    for param_name, param in all_parameters_by_name.iteritems():
                        # If already exists, update it
                        if param_name in existing_parameters_by_name:
                            db_param = existing_parameters_by_name[param_name]
                            db_param.parameter_type = param['type']
                            db_param.value = unicode(param['value'])
                            self.session.add(db_param)
                        else: # If it doesn't exist, add it
                            db_param = model.DbExperimentClientParameter(db_exp, 
                                        parameter_name = param_name, parameter_type = param['type'], value = unicode(param['value']))
                            self.session.add(db_param)
                    
                    self.session.add(db_exp)
                    try:
                        self.session.commit()
                    except:
                        self.session.rollback()
                        traceback.print_exc()
                        flash(gettext("Error commiting changes. Contact admin."), "error")
                    else:
                        flash(gettext("Changes saved"))
                else:
                    flash(gettext("Category not found"), "error")
        
        return self.render("admin/admin-add-experiment.html", form = form, client_parameters = get_js_client_parameters(), 
                static_parameters = json.dumps(static_parameters, indent = 4), 
                dynamic_parameters = json.dumps(dynamic_parameters, indent = 4))


class SchedulerForm(Form):
    name = TextField(lazy_gettext("Scheduler name"), description = lazy_gettext("Unique name for this scheduler"), validators = [Required()])

class PQueueForm(SchedulerForm):
    randomize_instances = BooleanField(lazy_gettext("Randomize experiments"), description = lazy_gettext("First available slot is always the same or there is an internal random process"))

PQueueObject = collections.namedtuple('PQueueObject', ['name', 'randomize_instances'])

class ExternalWebLabForm(SchedulerForm):
    base_url = URLField(lazy_gettext("Base URL"), description = lazy_gettext("Example: https://www.weblab.deusto.es/weblab/"), validators = [Required(), URL()])
    username = TextField(lazy_gettext("Username"), description = lazy_gettext("Username of the remote system"), validators = [Required()])
    password = PasswordField(lazy_gettext("Password"), description = lazy_gettext("Password of the remote system"), validators = [])

class ILabBatchForm(SchedulerForm):
    lab_server_url = URLField(lazy_gettext("Web service URL"), description = lazy_gettext("Example: http://weblab2.mit.edu/services/WebLabService.asmx"), validators = [Required(), URL()])
    identifier     = TextField(lazy_gettext("Identifier"), description = lazy_gettext("Fake Service Broker identifier"), validators = [Required()])
    passkey        = TextField(lazy_gettext("Passkey"), description = lazy_gettext("Remote Service broker passkey"), validators = [Required()])

class RemoveForm(Form):
    identifier = HiddenField()

class AddExperimentForm(Form):
    experiment_identifier = Select2Field(lazy_gettext("Experiment to add"))

class SchedulerPanel(AdministratorModelView):
    
    column_list = ('name', 'summary', 'scheduler_type', 'is_external')

    def __init__(self, session, **kwargs):
        super(SchedulerPanel, self).__init__(model.DbScheduler, session, **kwargs)

    @expose('/create/')
    def create_view(self):
        return self.render("admin/admin-scheduler-create.html")

    @expose('/create/pqueue/', ['GET', 'POST'])
    def create_pqueue_view(self):
        return self._edit_pqueue_view(url_for('.create_view'))

    def _edit_pqueue_view(self, back, obj = None, scheduler = None):
        form = PQueueForm(formdata = request.form, obj = obj)
        if form.validate_on_submit():
            if obj is None and self.session.query(model.DbScheduler).filter_by(name = form.name.data).first() is not None:
                form.name.errors = [gettext("Repeated name")]
            else:
                # Populate config
                if scheduler is None:
                    config = {}
                else:
                    config = json.loads(scheduler.config)
                config['randomize_instances'] = form.randomize_instances.data
                summary = gettext("Queue for %(name)s", name=form.name.data)

                if scheduler is None:
                    scheduler = model.DbScheduler(name = form.name.data, summary = summary, scheduler_type = 'PRIORITY_QUEUE', config = json.dumps(config), is_external = False)
                else:
                    scheduler.name = form.name.data
                    scheduler.summary = summary

                self.session.add(scheduler)
                try:
                    self.session.commit()
                except:
                    traceback.print_exc()
                    flash("Error adding resource", "error")
                    self.session.rollback()
                else:
                    flash("Scheduler saved", "success")
                    return redirect(url_for('.edit_view', id = scheduler.id))

        return self.render("admin/admin-scheduler-create-pqueue.html", form = form, back = back)
        

    @expose('/create/weblab/', ['GET', 'POST'])
    def create_weblab_view(self):
        return self._edit_weblab_view(url_for('.create_view'))

    def _edit_weblab_view(self, back, form_kwargs = None, scheduler = None):
        if form_kwargs is None:
            form_kwargs = {}
        if self.is_action('weblab-create'):
            form = ExternalWebLabForm(prefix='weblab_create', **form_kwargs)
        else:
            form = ExternalWebLabForm(formdata = None, prefix='weblab_create', **form_kwargs)

        if self.is_action('weblab-create') and form.validate_on_submit():
            if scheduler is None and self.session.query(model.DbScheduler).filter_by(name = form.name.data).first() is not None:
                form.name.errors = ["Repeated name"]
            else:
                # Populate config
                if scheduler is None:
                    config = {}
                else:
                    config = json.loads(scheduler.config)
                config['base_url'] = form.base_url.data
                config['username'] = form.username.data
                if form.password.data or 'password' not in config:
                    config['password'] = form.password.data

                parsed = urlparse.urlparse(form.base_url.data)
                summary = gettext("WebLab-Deusto at %(where)s", where=parsed.hostname)

                if scheduler is None:
                    scheduler = model.DbScheduler(name = form.name.data, summary = summary, scheduler_type = 'EXTERNAL_WEBLAB_DEUSTO', config = json.dumps(config), is_external = True)
                else:
                    scheduler.name = form.name.data
                    scheduler.summary = summary

                self.session.add(scheduler)
                try:
                    self.session.commit()
                except:
                    traceback.print_exc()
                    flash(gettext("Error adding resource"), "error")
                    self.session.rollback()
                else:
                    flash(gettext("Scheduler saved"), "success")
                    return redirect(url_for('.edit_view', id = scheduler.id))

        if scheduler:
            config = json.loads(scheduler.config)
            try:
                client = WebLabDeustoClient(config['base_url'])
                session_id = client.login(config['username'], config['password'])
                experiments_allowed = client.list_experiments(session_id)
            except:
                flash(gettext("Invalid configuration (or server down)"), "error")
                traceback.print_exc()
                experiments_allowed = []
            
            # 
            # WebLab-Deusto returns a list of available experiments.
            # 
            # Each experiment can be either:
            # a) Mapped to one or multiple existing experiments (in which case, there
            #    will be an entry where the config is the code)
            # b) Not mapped to any one
            # 
            # If the experiment has the same name or not is irrelevant. This way, if
            # the user changes the experiment in the admin in the local system, there
            # is no issue. And in every case (even if there is an experiment), it 
            # must be possible to add new experiments (except for if all are assigned 
            # to the laboratory, which would be weird).
            # 

            existing_experiment_ids = set()
            reverse_experiments_map = {
                # config : [ scheduler_experiment_entry1, scheduler_experiment_entry2 ]
            }
            for entry in scheduler.external_experiments:
                existing_experiment_ids.add(unicode(entry.experiment))
                if entry.config in reverse_experiments_map:
                    reverse_experiments_map[entry.config].append(entry)
                else:
                    reverse_experiments_map[entry.config] = [entry]
    
            experiments = self.session.query(model.DbExperiment).all()
            choices = [ unicode(exp) for exp in experiments if unicode(exp) not in existing_experiment_ids]
            if request.form:
                experiment_to_be_added = request.form.get(u'%s-experiment_identifier' % self.get_action())
            else:
                experiment_to_be_added = None
            
            retrieved_experiment_ids = set()
            all_experiments = []
            for exp_allowed in experiments_allowed:
                experiment_id = unicode(exp_allowed.experiment.get_unique_name())
                retrieved_experiment_ids.add(experiment_id)

                # Show all the already mapped experiments
                for entry in reverse_experiments_map.get(experiment_id, []):
                    prefix = 'remove_%s' % entry.id
                    if self.is_action(prefix):
                        remove_form = RemoveForm(identifier = unicode(entry.id), prefix = prefix)
                    else:
                        remove_form = RemoveForm(formdata = None, identifier = unicode(entry.id), prefix = prefix)
                    
                    if self.is_action(prefix) and remove_form.validate_on_submit():
                        self.session.delete(entry)
                        try:
                            self.session.commit()
                        except:
                            traceback.print_exc()
                            flash(gettext("Error removing experiment"), "error")
                            self.session.rollback()
                            break
                        else:
                            return redirect(request.url)
                    else:
                        exp_data = {
                            'experiment' : experiment_id,
                            'local_name' : unicode(entry.experiment),
                            'action'     : 'remove',
                            'form'       : remove_form,
                            'prefix'     : prefix,
                        }
                        all_experiments.append(exp_data)

                # Then, show experiments to be added.
                if choices:
                    prefix = 'add_%s' % experiment_id
                    if self.is_action(prefix):
                        add_form = AddExperimentForm(prefix = prefix)
                    else:
                        add_form = AddExperimentForm(formdata = None, prefix = prefix)

                    updated_choices = choices[:]
                    add_form.experiment_identifier.choices = zip(updated_choices, updated_choices)
                    
                    if self.is_action(prefix) and add_form.validate_on_submit():
                        experiment_to_register = add_form.experiment_identifier.data
                        for experiment in experiments:
                            if experiment_to_register == unicode(experiment):
                                entry = model.DbSchedulerExternalExperimentEntry(experiment = experiment, scheduler = scheduler, config = experiment_id)
                                self.session.add(entry)
                                try:
                                    self.session.commit()
                                except:
                                    traceback.print_exc()
                                    flash(gettext("Error registering weblab experiment"), "error")
                                    self.session.rollback()
                                    break
                                else:
                                    return redirect(request.url)

                    exp_data = {
                        'experiment' : experiment_id,
                        'action'     : 'add',
                        'form'       : add_form,
                        'prefix'     : prefix,
                    }
                    all_experiments.append(exp_data)
            
            # 
            # It may happen that some experiments existed in the past in the
            # foreign system and not anymore. Here we list them, and enable
            # the administrator to remove them.
            # 
            misconfigured_experiments = self.session.query(model.DbSchedulerExternalExperimentEntry).filter(model.DbSchedulerExternalExperimentEntry.config.notin_(retrieved_experiment_ids)).all()

            all_misconfigured_experiments = []
            for entry in misconfigured_experiments:
                prefix = 'remove_%s' % entry.id
                if self.is_action(prefix):
                    remove_form = RemoveForm(identifier = unicode(entry.id), prefix = prefix)
                else:
                    remove_form = RemoveForm(formdata = None, identifier = unicode(entry.id), prefix = prefix)
                
                if self.is_action(prefix) and remove_form.validate_on_submit():
                    self.session.delete(entry)
                    try:
                        self.session.commit()
                    except:
                        traceback.print_exc()
                        flash("Error removing experiment", "error")
                        self.session.rollback()
                        break
                    else:
                        return redirect(request.url)
                else:
                    exp_data = {
                        'experiment' : unicode(entry.config),
                        'local_name' : unicode(entry.experiment),
                        'action'     : 'remove',
                        'form'       : remove_form,
                        'prefix'     : prefix,
                    }
                    all_misconfigured_experiments.append(exp_data)

        else:
            all_experiments = []
            all_misconfigured_experiments = []
        return self.render("admin/admin-scheduler-create-weblab.html", form=form, back = back, experiments = all_experiments, misconfigured_experiments = all_misconfigured_experiments)

    @expose('/create/ilab/', ['GET', 'POST'])
    def create_ilab_view(self):    
        return self._edit_ilab_view(url_for('.create_view'))

    def is_action(self, name):
        return request.form and request.form.get('action') == name

    def get_action(self):
        if request.form:
            return request.form.get('action', '')
        return ''

    def _edit_ilab_view(self, back, form_kwargs = None, scheduler = None):
        if form_kwargs is None:
            form_kwargs = {}

        experiments = self.session.query(model.DbExperiment).all()

        if self.is_action('form-add'):
            form = ILabBatchForm(prefix = "ilab_create", **form_kwargs)
        else:
            form = ILabBatchForm(formdata = None, prefix = "ilab_create", **form_kwargs)
        
        if self.is_action('form-add') and form.validate_on_submit():
            if scheduler is None and self.session.query(model.DbScheduler).filter_by(name = form.name.data).first() is not None:
                form.name.errors = [gettext("Repeated name")]
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
                summary = gettext("iLab batch at %(where)s", where=parsed.hostname)

                if scheduler is None:
                    scheduler = model.DbScheduler(name = form.name.data, summary = summary, scheduler_type = 'ILAB_BATCH_QUEUE', config = json.dumps(config), is_external = True)
                else:
                    scheduler.name = form.name.data
                    scheduler.summary = summary

                self.session.add(scheduler)
                try:
                    self.session.commit()
                except:
                    traceback.print_exc()
                    flash(gettext("Error adding resource"), "error")
                    self.session.rollback()
                else:
                    flash(gettext("Scheduler saved"), "success")
                    return redirect(url_for('.edit_view', id = scheduler.id))

        if scheduler:
            external_experiments = [ unicode(exp.experiment) for exp in scheduler.external_experiments ]
            external_experiments_objects = [ exp.experiment for exp in scheduler.external_experiments ]
            choices = [ unicode(exp) for exp in experiments if exp not in external_experiments_objects ]

            if self.is_action('form-register'):
                add_form = AddExperimentForm(prefix = 'add_ilab')
            else:
                add_form = AddExperimentForm(formdata = None, prefix = 'add_ilab')
            add_form.experiment_identifier.choices = zip(choices, choices)
            if self.is_action('form-register') and add_form.validate_on_submit():
                experiment_to_register = add_form.experiment_identifier.data
                for experiment in experiments:
                    if experiment_to_register == unicode(experiment) and unicode(experiment) not in external_experiments:
                        entry = model.DbSchedulerExternalExperimentEntry(experiment = experiment, scheduler = scheduler, config = "")
                        self.session.add(entry)
                        try:
                            self.session.commit()
                        except:
                            traceback.print_exc()
                            flash(gettext("Error registering ilab experiment"), "error")
                            self.session.rollback()
                            break
                        choices.remove(unicode(experiment))
                        add_form.experiment_identifier.choices = zip(choices, choices)
                        break

            registered_experiments = []
            if experiments:

                for registered_experiment_entry in scheduler.external_experiments[:]:
                    prefix = 'remove_ilab_%s' % unicode(registered_experiment_entry.experiment)

                    if self.is_action(prefix):
                        remove_form = RemoveForm(identifier = unicode(registered_experiment_entry.experiment), prefix = prefix)
                    else:
                        remove_form = RemoveForm(formdata = None, identifier = unicode(registered_experiment_entry.experiment), prefix = prefix)

                    if self.is_action(prefix) and remove_form.validate_on_submit():
                        self.session.delete(registered_experiment_entry)
                        try:
                            self.session.commit()
                        except:
                            traceback.print_exc()
                            flash(gettext("Error removing experiment"), "error")
                            self.session.rollback()
                            break
                    else:
                        registered_experiments.append({
                            'name'   : unicode(registered_experiment_entry.experiment),
                            'form'   : remove_form,
                            'prefix' : prefix
                        })
        else:
            add_form = None
            registered_experiments = []

        return self.render("admin/admin-scheduler-create-ilab.html", form = form, back = back, registered_experiments = registered_experiments, add_form = add_form, create = scheduler is None)


    @expose('/edit/', ['GET', 'POST'])
    def edit_view(self):
        id = request.args.get('id')
        if id is None:
            flash(gettext("No id provided"), "error")
            return redirect(url_for('.index_view'))
        scheduler = self.session.query(model.DbScheduler).filter_by(id = id).first()
        if scheduler is None:
            flash(gettext("Id provided does not exist"), "error")
            return redirect(url_for('.index_view'))

        back = url_for('.index_view')
        config = json.loads(scheduler.config)
        if scheduler.scheduler_type == 'EXTERNAL_WEBLAB_DEUSTO':
            form_kwargs = dict(name = scheduler.name, base_url = config['base_url'], username = config['username'], password = config['password'])
            return self._edit_weblab_view(back, form_kwargs, scheduler)
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

    column_descriptions = dict(permanent_id=lazy_gettext('A unique permanent identifier for a particular permission'))
    column_searchable_list = ('permanent_id', 'comments')
    column_formatters = dict(permission=display_parameters)
    column_filters = ( 'permission_type', 'permanent_id', 'date', 'comments')
    column_sortable_list = ( 'permanent_id', 'date', 'comments')
    column_list = ('permission', 'permanent_id', 'date', 'comments')
    column_labels = dict(permission=lazy_gettext("Permission"), permanent_id=lazy_gettext("Permanent ID"), date=lazy_gettext("Date"), comments=lazy_gettext("Comments"))
    form_overrides = dict(permanent_id=DisabledTextField, permission_type=DisabledTextField)
    form_excluded_columns = ('uses',)

    def __init__(self, model, session, **kwargs):
        super(GenericPermissionPanel, self).__init__(model, session, **kwargs)


    def get_list(self, page, sort_column, sort_desc, search, filters, *args, **kwargs):
        # So as to sort descending, force sorting by 'id' and reverse the sort_desc
        if sort_column is None:
            sort_column = 'date'
            sort_desc = not sort_desc
        return super(GenericPermissionPanel, self).get_list(page, sort_column, sort_desc, search, filters, *args,
                                                            **kwargs)


    def on_model_change(self, form, permission, is_created):
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
            message = gettext("Missing arguments: %(arguments)s", arguments=', '.join(missing_arguments))
            if exceeded_arguments:
                message += "; "
        if exceeded_arguments:
            message += gettext("Exceeded arguments: %(arguments)s", arguments=', '.join(exceeded_arguments))
        if message:
            raise ValidationError(message)

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
                raise ValidationError(gettext("Experiment not found: %(experiment)s%", experiment='%s@%s' % (exp_name, cat_name)))

            try:
                int(time_allowed)
            except:
                raise ValidationError(gettext("Time allowed must be a number (in seconds)"))


class PermissionEditForm(InlineFormAdmin):
    def postprocess_form(self, form_class):
        form_class.permission_type_parameter = UnboundField(DisabledTextField)
        return form_class


class UserPermissionPanel(GenericPermissionPanel):
    column_filters = GenericPermissionPanel.column_filters + ('user',)
    column_sortable_list = GenericPermissionPanel.column_sortable_list + (('user', model.DbUser.login),)
    column_list = ('user', ) + GenericPermissionPanel.column_list
    column_labels = GenericPermissionPanel.column_labels.copy()
    column_labels['user'] = lazy_gettext("User")

    inline_models = (PermissionEditForm(model.DbUserPermissionParameter),)

    def __init__(self, session, **kwargs):
        super(UserPermissionPanel, self).__init__(model.DbUserPermission, session, **kwargs)


class GroupPermissionPanel(GenericPermissionPanel):
    column_filters = GenericPermissionPanel.column_filters + ('group',)
    column_sortable_list = GenericPermissionPanel.column_sortable_list + (('group', model.DbGroup.name),)
    column_list = ('group', ) + GenericPermissionPanel.column_list
    column_labels = GenericPermissionPanel.column_labels.copy()
    column_labels['group'] = lazy_gettext("Group")

    inline_models = (PermissionEditForm(model.DbGroupPermissionParameter),)

    def __init__(self, session, **kwargs):
        super(GroupPermissionPanel, self).__init__(model.DbGroupPermission, session, **kwargs)


class RolePermissionPanel(GenericPermissionPanel):
    column_filters = GenericPermissionPanel.column_filters + ('role',)
    column_sortable_list = GenericPermissionPanel.column_sortable_list + (('role', model.DbRole.name),)
    column_list = ('role', ) + GenericPermissionPanel.column_list
    column_labels = GenericPermissionPanel.column_labels.copy()
    column_labels['role'] = lazy_gettext("Role")

    inline_models = (PermissionEditForm(model.DbRolePermissionParameter),)

    def __init__(self, session, **kwargs):
        super(RolePermissionPanel, self).__init__(model.DbRolePermission, session, **kwargs)

class PermissionsForm(Form):
    permission_types = Select2Field(lazy_gettext("Permission type:"),
                                    choices=[(permission_type, permission_type) for permission_type in
                                             permissions.permission_types], default=permissions.EXPERIMENT_ALLOWED)
    recipients = Select2Field(lazy_gettext("Type of recipient:"), choices=[('user', lazy_gettext('User')), ('group', lazy_gettext('Group')), ('role', lazy_gettext('Role'))],
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

        return self.render("admin/admin-permissions.html", form=form, permission_types = permissions.permission_types)

    def _get_permission_form(self, permission_type, recipient_type, recipient_resolver, DbPermissionClass,
                             DbPermissionParameterClass):
        key = u'%s__%s' % (permission_type, recipient_type)
        if key in self.PERMISSION_FORMS:
            return self.PERMISSION_FORMS[key]()

        # Otherwise, generate it
        current_permission_type = permissions.permission_types[permission_type]

        session = self.session

        class ParentPermissionForm(Form):

            comments = TextField(lazy_gettext("Comments"))
            recipients = Select2Field(recipient_type, description=lazy_gettext("Recipients of the permission"))

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

                experiment = Select2Field(lazy_gettext('Experiment'), description=lazy_gettext("Experiment"))

                time_allowed = TextField(lazy_gettext('Time assigned'), description=lazy_gettext("Measured in seconds"),
                                         validators=[Required(), NumberRange(min=1)], default=100)
                priority = TextField(lazy_gettext('Priority'), description=lazy_gettext("Priority of the user"),
                                     validators=[Required(), NumberRange(min=0)], default=5)
                initialization_in_accounting = SelectField(lazy_gettext('Initialization'),
                                                           description=lazy_gettext("Take initialization into account"),
                                                           choices=[('1', lazy_gettext('Yes')), ('0', lazy_gettext('No'))], default='1')


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

        elif permission_type == permissions.INSTRUCTOR_OF_GROUP:

            class ParticularPermissionForm(ParentPermissionForm):
                parameter_list = ['target_group']

                target_group = Select2Field(lazy_gettext('Target group'), description=lazy_gettext("Group to be instructed"))

                def __init__(self, *args, **kwargs):
                    super(ParticularPermissionForm, self).__init__(*args, **kwargs)
                    self.target_group.choices = [
                                (unicode(group.id), group.name)
                                for group in session.query(model.DbGroup).all() ]

                def get_permanent_id(self):
                    recipient = recipient_resolver(self.recipients.data)
                    name = self.target_group.data
                    return u'%s::group-%s::%s' % (permission_type, name, recipient)

                def add_parameters(self, db_permission):
                    db_parameter = DbPermissionParameterClass(db_permission, permissions.TARGET_GROUP,
                                                              self.target_group.data)
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
                flash(gettext("Error saving data. May the permission be duplicated?"))
                return self.render("admin/admin-permission-create.html", form=form, fields=form.parameter_list,
                                   description=current_permission_type.description, permission_type=permission_type)
            return redirect(back_url)

        return self.render("admin/admin-permission-create.html", form=form, fields=form.parameter_list,
                           description=current_permission_type.description, permission_type=permission_type)

    @expose('/users/<permission_type>/', methods=['GET', 'POST'])
    def users(self, permission_type):
        self._check_permission_type(permission_type)

        users = [(user.login, u'%s - %s' % (user.login, user.full_name)) for user in
                 self.session.query(model.DbUser).order_by(desc('id')).all()]

        recipient_resolver = lambda login: self.session.query(model.DbUser).filter_by(login=login).one()

        return self._show_form(permission_type, gettext('Users'), users, recipient_resolver,
                               model.DbUserPermission, model.DbUserPermissionParameter,
                               url_for('permissions/user.index_view'))

    @expose('/groups/<permission_type>/', methods=['GET', 'POST'])
    def groups(self, permission_type):
        self._check_permission_type(permission_type)

        groups = [(g.name, g.name) for g in self.session.query(model.DbGroup).order_by(desc('id')).all()]

        recipient_resolver = lambda group_name: self.session.query(model.DbGroup).filter_by(name=group_name).one()

        return self._show_form(permission_type, gettext('Groups'), groups, recipient_resolver,
                               model.DbGroupPermission, model.DbGroupPermissionParameter,
                               url_for('permissions/group.index_view'))


    @expose('/roles/<permission_type>/', methods=['GET', 'POST'])
    def roles(self, permission_type):
        self._check_permission_type(permission_type)

        roles = [(r.name, r.name) for r in self.session.query(model.DbRole).order_by(desc('id')).all()]

        recipient_resolver = lambda role_name: self.session.query(model.DbRole).filter_by(name=role_name).one()

        return self._show_form(permission_type, gettext('Roles'), roles, recipient_resolver,
                               model.DbRolePermission, model.DbRolePermissionParameter,
                               url_for('permissions/role.index_view'))

class ClientField(collections.namedtuple('ClientField', ['field', 'key'])):
    @property
    def type(self):
        return 'client'

class ServerField(collections.namedtuple('ServerField', ['field', 'key'])):
    @property
    def type(self):
        return 'server'

class ImageField(collections.namedtuple('ImageField', ['field', 'image'])):
    @property
    def type(self):
        return 'image'

IMAGES_FORMATS = ['jpg', 'jpeg', 'png', 'gif']

class SystemPropertiesForm(Form):
    demo_available = BooleanField(lazy_gettext("Demo available:"))
    demo_user = Select2Field(lazy_gettext("Demo user"))
    demo_password = TextField(lazy_gettext("Demo password"), description=lazy_gettext("Password of the selected user. It will be publicly shown. Make sure that it is the valid password for the user."))
    host_entity_image = FileField(lazy_gettext("Entity picture:"), validators = [ FileAllowed(IMAGES_FORMATS, lazy_gettext('Images only!')) ])
    host_entity_image_small = FileField(lazy_gettext("Entity small picture:"), validators = [ FileAllowed(IMAGES_FORMATS, lazy_gettext('Images only!')) ])
    host_entity_link = URLField(lazy_gettext("Entity link:"))
    contact_email = EmailField(lazy_gettext("Contact e-mail:"), validators = [Email()])
    admin_emails = TextField(lazy_gettext("Admin e-mails:"), description = lazy_gettext("Separated by commas"))
    google_analytics = TextField(lazy_gettext("Google Analytics Account:"))

    # base.location: "/w/whatever": generated at client_config.py

    FIELDS = [
        {
            'name' : lazy_gettext("Guest accounts"),
            'description' : lazy_gettext("Manage public account creation, guest accounts, etc.:"),
            'values' : [
                ClientField(field='demo_available', key='demo.available'),
                ClientField(field='demo_user', key='demo.username'),
                ClientField(field='demo_password', key='demo.password'),
            ],
        },
        {
            'name' : lazy_gettext("Entity"),
            'description' : lazy_gettext("Entity customization: logo, links, etc.:"),
            'values' : [
                ImageField(field='host_entity_image', image='.logo_regular'),
                ClientField(field='host_entity_link', key='host.entity.link'),
                ClientField(field='contact_email', key='admin.email'),
                ServerField(field='admin_emails', key='admin.emails'),
            ],
        },
        {
            'name' : lazy_gettext("Tracking"),
            'description' : lazy_gettext("Tracking identification"),
            'values' : [
                ClientField(field='google_analytics', key='google.analytics.tracking.code'),
            ]
        },
    ]
    FIELDS_BY_KEY = {
        # key: field_name
    }
    ALL_FIELDS = []


# Validation - double check
for category in SystemPropertiesForm.FIELDS:
    for _field in category['values']:
        if not hasattr(SystemPropertiesForm, _field.field):
            print("Invalid name: %s" % _field.field, file=sys.stderr)
        elif hasattr(_field, 'key'):
            SystemPropertiesForm.ALL_FIELDS.append(_field)
            SystemPropertiesForm.FIELDS_BY_KEY[_field.key] = _field.field


class SystemProperties(AdministratorView):
    def __init__(self, db_session, **kwargs):
        self._db_session = db_session
        super(SystemProperties, self).__init__(**kwargs)

    @expose('/logos/regular')
    def logo_regular(self):
        return logo_impl(self.app_instance.config[configuration_doc.CORE_LOGO_PATH])

    def _store_image(self, field, config_property):
        image_path = self.app_instance.config[config_property]
        image_path = os.path.abspath(image_path)
        if os.path.exists(image_path):
            field.data.save(image_path)
        else:
            field.errors = [gettext("File %(path)s does not exist. Create it first", path=image_path)]

    @expose('/', methods = ['GET', 'POST'])
    def index(self):
        db = self.app_instance.db
        client_config = db.client_configuration()
        server_config = db.server_configuration()
        
        kwargs = {}
        for key, value in six.iteritems(client_config):
            field_name = SystemPropertiesForm.FIELDS_BY_KEY.get(key)
            if field_name is not None:
                kwargs[field_name] = value
            else:
                print("ClientConfiguration key %s not present in the form" % key)

        form = SystemPropertiesForm(**kwargs)
        logins = db.list_user_logins()
        form.demo_user.choices = zip(logins, logins)

        create_msg = gettext("create one")
        create_one = "<a href='{0}'>{1}</a>".format(url_for('users/users.create_view', url=request.url), create_msg)
        form.demo_user.description = Markup(gettext("Select from the list, or %(create_one)s", create_one=create_one))

        if form.validate_on_submit():

            if form.host_entity_image.data:
                self._store_image(form.host_entity_image, configuration_doc.CORE_LOGO_PATH)

            if form.host_entity_image_small.data:
                self._store_image(form.host_entity_image_small, configuration_doc.CORE_LOGO_SMALL_PATH)

            client_properties = {
                # key: value
            }
            server_properties = {
                # key: value
            }

            for field in SystemPropertiesForm.ALL_FIELDS:
                data = getattr(form, field.field).data
                if field.type == 'client':
                    client_properties[field.key] = data
                elif field.type == 'server':
                    server_properties[field.key] = data
                # field.type == 'other' => Discarded. e.g., images
            db.store_configuration(client_properties, server_properties)

        return self.render("admin/admin-system-properties.html", form = form)


class HomeView(AdminAuthnMixIn, WebLabAdminIndexView):
    def __init__(self, db_session, **kwargs):
        self._db_session = db_session
        super(HomeView, self).__init__(**kwargs)

    @expose()
    def index(self):
        db = self.app_instance.db
        last_week_uses = db.frontend_admin_uses_last_week()
        last_year_uses = db.frontend_admin_uses_last_year()
        geo_month = db.frontend_admin_uses_geographical_month()
        latest_uses = db.frontend_admin_latest_uses()
        local_dir = self.app_instance.config.get_value('deployment_dir', '.')
        directory = os.path.basename(os.path.abspath(local_dir))
        return self.render("admin/admin-index.html",
                latest_uses=latest_uses, geo_month=geo_month,
                last_week_uses=self._to_nvd3(last_week_uses), 
                last_year_uses=self._to_nvd3(last_year_uses),
                directory = directory)

    def _to_nvd3(self, data):
        formatted = [
            # {
            #   'key' : 'Experiment name', // or 'Total'
            #   'values' : [
            #       [
            #           milliseconds_since_epoch,
            #           value
            #       ]
            #   ]
            # }
        ]

        total_values = collections.defaultdict(int)
            # date : value

        total_experiments_value = collections.defaultdict(int)
            # experiment : total_value

        for experiment_name, experiment_data in six.iteritems(data):
            for date, value in six.iteritems(experiment_data):
                total_experiments_value[experiment_name] += value
                total_values[date] += value

        total_data = {
            'key' : gettext('Total'),
            'values' : []
        }
        for date in sorted(total_values.keys()):
            total_data['values'].append([int(date.strftime('%s') + '000'), total_values[date]])
        formatted.append(total_data)

        for experiment_name, total_value in collections.Counter(total_experiments_value).most_common(9):
            experiment_data = {
                'key' : experiment_name,
                'values' : []
            }
            for date in sorted(data[experiment_name].keys()):
                experiment_data['values'].append([int(date.strftime('%s') + '000'), data[experiment_name][date]])
            formatted.append(experiment_data)

        return formatted
                
