import sha
import random

from flask import redirect, request, flash
from flask.ext.admin import expose, AdminIndexView, BaseView

import weblab.db.model as model
import weblab.admin.web.admin_views as admin_views

from flask.ext.wtf import TextField, Form, PasswordField, NumberRange
from weblab.admin.web.fields import DisabledTextField

import weblab.permissions as permissions


def get_app_instance():
    import weblab.admin.web.app as admin_app
    return admin_app.GLOBAL_APP_INSTANCE

class ProfileEditForm(Form):
    full_name   = DisabledTextField(u"Full name:")
    login       = DisabledTextField(u"Login:")
    email       = TextField(u"E-mail:")
    facebook    = TextField(u"Facebook id:", description="Facebook identifier (number).", validators = [NumberRange(min=1000) ])
    password    = PasswordField(u"Password:", description="Password.")

class ProfileEditView(BaseView):

    def __init__(self, db_session, *args, **kwargs):
        super(ProfileEditView, self).__init__(*args, **kwargs)

        self._session = db_session

    @expose(methods=['GET','POST'])
    def index(self):
        login = get_app_instance().get_user_information().login
        user = self._session.query(model.DbUser).filter_by(login = login).one()
        
        facebook_id = ''

        user_auths = {}
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

        user_permissions = get_app_instance().get_permissions()
        
        change_profile = True
        for permission in user_permissions:
            if permission.name == permissions.CANT_CHANGE_PROFILE:
                change_password = False
                change_profile  = False

        if change_profile and form.validate_on_submit():

            errors = []

            if change_password and password_auth is not None and form.password.data:
                if len(form.password.data) < 6:
                    errors.append("Error: too short password")
                else:
                    password_auth.configuration = self._password2sha(form.password.data)

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
                flash("Saved")

        return self.render("profile-edit.html", form=form, change_password=change_password, change_profile=change_profile)

    def _password2sha(self, password):
        randomstuff = ""
        for _ in range(4):
            c = chr(ord('a') + random.randint(0,25))
            randomstuff += c
        password = password if password is not None else ''
        return randomstuff + "{sha}" + sha.new(randomstuff + password).hexdigest()

    def is_accessible(self):
        return get_app_instance().get_user_information() is not None

    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            return redirect(request.url.split('/weblab/administration')[0] + '/weblab/client')

        return super(ProfileEditView, self)._handle_view(name, **kwargs)

class MyAccessesPanel(admin_views.UserUsedExperimentPanel):
    column_list    = ( 'experiment', 'start_date', 'end_date', 'origin', 'details' )
    column_filters = ( 'start_date', 'end_date', 'experiment', 'origin')

    def is_accessible(self):
        return get_app_instance().get_user_information() is not None

    def get_query(self):
        query = super(MyAccessesPanel, self).get_query()

        permissions = get_app_instance().get_permissions()

        # TODO: take permissions and if it says "do not use other logs", only show those logs
        # of the current IP address. This would be useful for the demo.

        user_information = get_app_instance().get_user_information()
        user = self.session.query(model.DbUser).filter_by(login = user_information.login).one()

        return query.filter_by(user = user)

    def get_files_query(self, id):
        uf = super(MyAccessesPanel, self).get_file(id)
        if uf is None:
            return None

        user_information = get_app_instance().get_user_information()
        user = self.session.query(model.DbUser).filter_by(login = user_information.login).one()
        
        if uf.experiment_use.user == user:
            return uf
        return None

class ProfileHomeView(AdminIndexView):

    def __init__(self, db_session, **kwargs):
        self._db_session = db_session
        super(ProfileHomeView, self).__init__(**kwargs)

    @expose()
    def index(self):
        user_information = get_app_instance().get_user_information()
        return self.render("profile-index.html", is_admin = get_app_instance().is_admin(), admin_url = get_app_instance().full_admin_url, user_information = user_information)

    def is_accessible(self):
        return get_app_instance().get_user_information() is not None

    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            return redirect(request.url.split('/weblab/administration')[0] + '/weblab/client')

        return super(ProfileHomeView, self)._handle_view(name, **kwargs)


