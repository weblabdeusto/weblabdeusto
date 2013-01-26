from flask.ext.admin import expose, AdminIndexView, BaseView

import weblab.db.model as model
import weblab.admin.web.admin_views as admin_views


def get_app_instance():
    import weblab.admin.web.app as admin_app
    return admin_app.AdministrationApplication.INSTANCE

class MyAccessesPanel(admin_views.UserUsedExperimentPanel):
    column_list    = ( 'experiment', 'start_date', 'end_date', 'origin', 'coord_address','details' )

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
        return self.render("profile-index.html", is_admin = get_app_instance().is_admin(), admin_url = get_app_instance().full_admin_url)

    def is_accessible(self):
        return get_app_instance().get_user_information() is not None

    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            return redirect(request.url.split('/weblab/administration')[0] + '/weblab/client')

        return super(ProfileHomeView, self)._handle_view(name, **kwargs)


