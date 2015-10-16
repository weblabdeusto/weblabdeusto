from __future__ import print_function, unicode_literals

import threading

from flask.ext.admin import expose, AdminIndexView, BaseView
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.admin.contrib.fileadmin import FileAdmin

admin_request = threading.local()

class AdminRequestInjector(object):

    def before_request(self, *args, **kwargs):
        pass

    def after_request(self, response, *args, **kwargs):
        pass

    @property
    def request_context(self):
        return admin_request

    def create_blueprint(self, *args, **kwargs):
        blueprint = super(AdminRequestInjector, self).create_blueprint(*args, **kwargs)
        @blueprint.before_request
        def before(*args, **kwargs):
            self.before_request(*args, **kwargs)

        @blueprint.after_request
        def after(response, *args, **kwargs):
            self.after_request(response, *args, **kwargs)
            # Clean
            for name in dir(admin_request):
                if not name.startswith('_'):
                    delattr(admin_request, name)
            return response

        return blueprint

class WebLabAdminIndexView(AdminRequestInjector, AdminIndexView):
    pass

class WebLabBaseView(AdminRequestInjector, BaseView):
    pass

class WebLabModelView(AdminRequestInjector, ModelView):
    pass

class WebLabFileAdmin(AdminRequestInjector, FileAdmin):
    pass

