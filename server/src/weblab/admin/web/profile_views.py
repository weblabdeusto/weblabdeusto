from __future__ import print_function, unicode_literals
import sha
import random

from flask import redirect, request, flash, url_for
from flask.ext.admin import expose
from weblab.admin.web.util import WebLabAdminIndexView, WebLabBaseView

import weblab.db.model as model
from weblab.admin.util import password2sha
import weblab.admin.web.admin_views as admin_views

from wtforms import TextField, PasswordField
from wtforms.validators import NumberRange
from flask.ext.wtf import Form
from weblab.admin.web.fields import DisabledTextField

from weblab.core.i18n import gettext, lazy_gettext
import weblab.permissions as permissions


def get_app_instance(view):
    return view.admin.weblab_admin_app

class ProfileEditForm(Form):
    full_name   = DisabledTextField(lazy_gettext("Full name:"))
    login       = DisabledTextField(lazy_gettext(u"Login:"))
    email       = TextField(lazy_gettext(u"E-mail:"))
    facebook    = TextField(lazy_gettext(u"Facebook id:"), description=lazy_gettext("Facebook identifier (number)."), validators = [NumberRange(min=1000) ])
    password    = PasswordField(lazy_gettext(u"Password:"), description=lazy_gettext("Password."))

class ProfileEditView(WebLabBaseView):

    def __init__(self, db_session, *args, **kwargs):
        super(ProfileEditView, self).__init__(*args, **kwargs)

        self._session = db_session

    @expose(methods=['GET','POST'])
    def index(self):
        login = get_app_instance(self).get_user_information().login
        user = self._session.query(model.DbUser).filter_by(login = login).one()
        
        facebook_id = ''

        change_password = True
        password_auth = None
        facebook_auth = None

        for user_auth in user.auths:
            if user_auth.auth.auth_type.name.lower() == 'facebook':
                facebook_id = user_auth.configuration
                facebook_auth = user_auth
            if 'ldap' in user_auth.auth.auth_type.name.lower():
                change_password = False
            if user_auth.auth.auth_type.name.lower() == 'db':
                password_auth = user_auth


        if len(request.form):
            form = ProfileEditForm(request.form)
        else:
            form = ProfileEditForm()
            form.full_name.data = user.full_name
            form.login.data     = user.login
            form.email.data     = user.email
            form.facebook.data  = facebook_id

        user_permissions = get_app_instance(self).get_permissions()
        
        change_profile = True
        for permission in user_permissions:
            if permission.name == permissions.CANT_CHANGE_PROFILE:
                change_password = False
                change_profile  = False

        if change_profile and form.validate_on_submit():

            errors = []

            if change_password and password_auth is not None and form.password.data:
                if len(form.password.data) < 6:
                    errors.append(gettext("Error: too short password"))
                else:
                    password_auth.configuration = password2sha(form.password.data)

            user.email = form.email.data
            
            if form.facebook.data:
                if facebook_auth is None:
                    auth = self._session.query(model.DbAuth).filter_by(name = 'FACEBOOK').one()
                    new_auth = model.DbUserAuth(user, auth, form.facebook.data)
                    self._session.add(new_auth)
                else:
                    facebook_auth.configuration = form.facebook.data
            else:
                if facebook_auth is not None:
                    self._session.delete(facebook_auth)

            self._session.commit()

            if errors:
                for error in errors:
                    flash(error)
            else:
                flash(gettext("Saved"))

        return self.render("profile/profile-edit.html", form=form, change_password=change_password, change_profile=change_profile)

    def is_accessible(self):
        return get_app_instance(self).get_user_information() is not None

    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            return redirect(url_for('core_webclient.login', next=request.url))

        return super(ProfileEditView, self)._handle_view(name, **kwargs)

class MyAccessesPanel(admin_views.UserUsedExperimentPanel):
    column_list    = ( 'experiment', 'start_date', 'end_date', 'origin', 'details' )
    column_filters = ( 'start_date', 'end_date', 'experiment', 'origin')
    column_labels  = dict(experiment=lazy_gettext("Experiment"), start_date=lazy_gettext("Start date"), end_date=lazy_gettext("End date"), origin=lazy_gettext("Origin"), details=lazy_gettext("Details"))

    def is_accessible(self):
        return get_app_instance(self).get_user_information() is not None

    def _apply_filters(self, query):
        permissions = get_app_instance(self).get_permissions()

        # TODO: take permissions and if it says "do not use other logs", only show those logs
        # of the current IP address. This would be useful for the demo.

        user_information = get_app_instance(self).get_user_information()
        user = self.session.query(model.DbUser).filter_by(login = user_information.login).one()

        return query.filter_by(user = user)

    def get_query(self):
        query = super(MyAccessesPanel, self).get_query()
        return self._apply_filters(query)

    def get_count_query(self):
        query = super(MyAccessesPanel, self).get_count_query()
        return self._apply_filters(query)

    def get_files_query(self, id):
        uf = super(MyAccessesPanel, self).get_file(id)
        if uf is None:
            return None

        user_information = get_app_instance(self).get_user_information()
        user = self.session.query(model.DbUser).filter_by(login = user_information.login).one()
        
        if uf.experiment_use.user == user:
            return uf
        return None

class ProfileHomeView(WebLabAdminIndexView):

    def __init__(self, db_session, **kwargs):
        self._db_session = db_session
        super(ProfileHomeView, self).__init__(**kwargs)

    @expose()
    def index(self):
        user_information = get_app_instance(self).get_user_information()
        return self.render("profile/profile-index.html", is_admin = get_app_instance(self).is_admin(), admin_url = get_app_instance(self).full_admin_url, user_information = user_information)

    def is_accessible(self):
        return get_app_instance(self).get_user_information() is not None

    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            return redirect(url_for('core_webclient.login', next=request.url))

        return super(ProfileHomeView, self)._handle_view(name, **kwargs)


