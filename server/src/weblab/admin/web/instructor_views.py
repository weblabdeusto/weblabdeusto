from flask import redirect, request, flash
from flask.ext.admin import expose, AdminIndexView, BaseView
from flask.ext.admin.contrib.sqla import ModelView

def get_app_instance():
    import weblab.admin.web.app as admin_app
    return admin_app.AdministrationApplication.INSTANCE

def is_instructor():
    return get_app_instance().get_user_information() is not None

class InstructorView(BaseView):
    def is_accessible(self):
        return is_instructor()

    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            return redirect(request.url.split('/weblab/instructor')[0] + '/weblab/client')

        return super(InstructorView, self)._handle_view(name, **kwargs)

class InstructorModelView(ModelView):
    def is_accessible(self):
        return is_instructor()

    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            return redirect(request.url.split('/weblab/instructor')[0] + '/weblab/client')

        return super(InstructorModelView, self)._handle_view(name, **kwargs)

class InstructorHomeView(AdminIndexView):
    def __init__(self, db_session, **kwargs):
        self._db_session = db_session
        super(InstructorHomeView, self).__init__(**kwargs)

    @expose()
    def index(self):
        user_information = get_app_instance().get_user_information()
        return self.render("instructor-index.html", is_admin = get_app_instance().is_admin(), admin_url = get_app_instance().full_admin_url, user_information = user_information)

    def is_accessible(self):
        return is_instructor()

    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            return redirect(request.url.split('/weblab/administration')[0] + '/weblab/client')

        return super(InstructorHomeView, self)._handle_view(name, **kwargs)

class UsersPanel(InstructorModelView):
    pass

