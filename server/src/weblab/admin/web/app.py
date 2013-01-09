from flask import Flask
from flask.ext.admin import Admin
from flask.ext.admin.contrib.sqlamodel import ModelView

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

if __name__ == '__main__':
    import sys, os
    sys.path.insert(0, '.')

import weblab.db.model as model

class UsersPanel(ModelView):

    column_searchable_list = ('full_name', model.DbUser.full_name)
    column_filters = ('full_name','login')

    column_descriptions = dict(
            full_name='First and Last name'
        )

    inline_models = (model.DbUserAuth,)

    def __init__(self, session, **kwargs):
        default_args = { "category":u"General", "name":u"Users" }
        default_args.update(**kwargs)
        super(UsersPanel, self).__init__(model.DbUser, session, **default_args)

# Look at https://gist.github.com/3826421


class GroupsPanel(ModelView):
    def __init__(self, session, **kwargs):
        default_args = { "category":u"General", "name":u"Groups" }
        default_args.update(**kwargs)
        super(GroupsPanel, self).__init__(model.DbGroup, session, **default_args)

class UserUsedExperimentPanel(ModelView):

    column_auto_select_related = True
    # column_display_all_relations = True
    column_select_related_list = ('user',)
    can_delete = False
    can_edit   = False
    can_create = False

    action_disallowed_list = ['create','edit','delete']

    def __init__(self, session, **kwargs):
        default_args = { "category":u"Logs", "name":u"User logs" }
        default_args.update(**kwargs)
        super(UserUsedExperimentPanel, self).__init__(model.DbUserUsedExperiment, session, **default_args)



engine = create_engine('mysql://weblab:weblab@localhost/WebLabTests', convert_unicode=True, pool_recycle=3600)

db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

SECRET_KEY = 'development_key'

app = Flask(__name__)


admin = Admin(app)
admin.add_view(UsersPanel(db_session))
admin.add_view(GroupsPanel(db_session))
admin.add_view(UserUsedExperimentPanel(db_session))



if __name__ == '__main__':
    app.config.from_object(__name__)
    app.run(debug=True)
