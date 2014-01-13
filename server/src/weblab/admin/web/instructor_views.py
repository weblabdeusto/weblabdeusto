from collections import defaultdict

from flask import redirect, request, flash
from flask.ext.admin import expose, AdminIndexView, BaseView
from flask.ext.admin.contrib.sqla import ModelView

import weblab.permissions as permissions
import weblab.db.model as model

def get_app_instance():
    import weblab.admin.web.app as admin_app
    return admin_app.AdministrationApplication.INSTANCE

def is_instructor():
    is_admin = get_app_instance().is_admin()
    if is_admin:
        return True
    
    return get_app_instance().get_user_role() in ('admin', 'instructor')

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
        groups = get_assigned_groups(self._db_session)
        return self.render("instructor-index.html", is_admin = get_app_instance().is_admin(), admin_url = get_app_instance().full_admin_url, user_information = user_information, groups = groups)

    def is_accessible(self):
        return is_instructor()

    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            return redirect(request.url.split('/weblab/administration')[0] + '/weblab/client')

        return super(InstructorHomeView, self)._handle_view(name, **kwargs)

def get_assigned_group_ids(session):
    # If the user is an administrator, permissions are not relevant.
    if get_app_instance().is_admin():
        return [ group.id for group in session.query(model.DbGroup).all() ]

    # Otherwise, check the permissions and only return those groups
    # where the user has a specific permission
    group_ids = set()

    for permission in get_app_instance().get_permissions():
        if permission.name == permissions.INSTRUCTOR_OF_GROUP:
            group_id = permission.get_parameter_value(permissions.TARGET_GROUP)
            if group_id is not None:
                group_ids.add(int(group_id))

    return group_ids

def get_assigned_groups(session):
    group_ids = get_assigned_group_ids(session)

    return session.query(model.DbGroup).filter(model.DbGroup.id.in_(group_ids))

def apply_instrutor_filters_to_logs(session, logs_query):
    """ logs_query is a sqlalchemy query. Here we filter that 
    the teacher only sees those permissions for a group.
    """
    group_ids = get_assigned_group_ids(session)

    permission_ids = set()

    for permission in session.query(model.DbGroupPermission).filter(model.DbGroupPermission.group_id.in_(group_ids), model.DbGroupPermission.permission_type == permissions.EXPERIMENT_ALLOWED).all():
        permission_ids.add(permission.id)

    logs_query.filter(model.DbUserUsedExperiment.group_permission_id.in_(permission_ids))
    return logs_query


class UsersPanel(InstructorModelView):

    can_edit = can_delete = can_create = False

    def __init__(self, session, **kwargs):
        super(UsersPanel, self).__init__(model.DbUser, session, **kwargs)

    def get_query(self):
        query = super(UsersPanel, self).get_query()
        groups = get_assigned_groups(self.session).subquery()
        query = query.join(groups, model.DbUser.groups)
        return query

    def get_count_query(self):
        query = super(UsersPanel, self).get_count_query()
        groups = get_assigned_groups(self.session).subquery()
        query = query.join(groups, model.DbUser.groups)
        return query

class GroupsPanel(InstructorModelView):

    can_edit = can_delete = can_create = False

    def __init__(self, session, **kwargs):
        super(GroupsPanel, self).__init__(model.DbGroup, session, **kwargs)

    def get_query(self):
        query = super(GroupsPanel, self).get_query()
        query = query.filter(model.DbGroup.id.in_(get_assigned_group_ids(self.session)))
        return query

    def get_count_query(self):
        query = super(GroupsPanel, self).get_count_query()
        query = query.filter(model.DbGroup.id.in_(get_assigned_group_ids(self.session)))
        return query


class UserUsedExperimentPanel(InstructorModelView):

    can_edit = can_delete = can_create = False

    column_list = ['user', 'experiment', 'start_date', 'end_date', 'origin']

    def __init__(self, session, **kwargs):
        super(UserUsedExperimentPanel, self).__init__(model.DbUserUsedExperiment, session, **kwargs)

    def get_query(self):
        query = super(UserUsedExperimentPanel, self).get_query()
        query = apply_instrutor_filters_to_logs(self.session, query)
        return query


    def get_count_query(self):
        query = super(UserUsedExperimentPanel, self).get_count_query()
        query = apply_instrutor_filters_to_logs(self.session, query)
        return query

def generate_color_code(value, max_value):
    # white to red
    percent = 1.0 * value / max_value
    blue  = hex(int(256 - 256 * percent)).split('x')[1].zfill(2)
    green = hex(int(256 - 256 * percent)).split('x')[1].zfill(2)
    return 'ff%s%s' % (green, blue)

def generate_timetable(days_data):
    # {
    #    'saturday' : {
    #         23 : 1413
    #    }
    # }
    timetables = {}
    max_values = {}
    timetable = {
        'format' : '%i',
        'hours' : defaultdict(dict),
        'empty_hours' : set()
        # hours:{
        #    hour : { 
        #        day : {
        #            value : 513,
        #            color : 'ffffff',
        #        }
        #    },
        # },
        # empty_hours : set(['01', '02', '03'])
    }
    max_value = 0

    for day in days_data:
        day_data = days_data[day]
        for hour in day_data:
            value = day_data[hour]

            timetable['hours'][str(hour).zfill(2)][day] = dict(value = value, color = '000000')
            if value > max_value:
                max_value = value

    # Fill empty_hours
    for hour_number in range(24):
        hour = str(hour_number).zfill(2)
        if not hour in timetable['hours']:
            timetable['empty_hours'].add(hour)


    for hour in timetable['hours']:
        for day in timetable['hours'][hour]:
            cur_data = timetable['hours'][hour][day]
            cur_data['color'] = generate_color_code(cur_data['value'], max_value)

    return timetable


class GroupStats(InstructorView):
    def __init__(self, session, **kwargs):
        self.session = session
        super(GroupStats, self).__init__(**kwargs)

    @expose('/')
    def index(self):
        return "TODO" # TODO

    @expose('/groups/<int:group_id>/')
    def group_stats(self, group_id):
        if group_id in get_assigned_group_ids(self.session):
            
            group = self.session.query(model.DbGroup).filter_by(id = group_id).first()

            permission_ids = set()
            experiments = defaultdict(list)
            # {
            #     'foo@Category' : [
            #          ( time_in_seconds, permission_id )
            #     ]
            # }
            for permission in self.session.query(model.DbGroupPermission).filter_by(group_id = group_id, permission_type = permissions.EXPERIMENT_ALLOWED).all():
                permission_ids.add(permission.id)
                exp_id = permission.get_parameter(permissions.EXPERIMENT_PERMANENT_ID).value
                cat_id = permission.get_parameter(permissions.EXPERIMENT_CATEGORY_ID).value
                time_allowed = int(permission.get_parameter(permissions.TIME_ALLOWED).value)
                experiments['%s@%s' % (exp_id, cat_id)].append((time_allowed, permission.id))

            # Get something different per experiment
            # TODO
            # if len(permission_ids) > 1:
            #     pass

            # Get the totals
            users = defaultdict(int)
            # {
            #     login : uses
            # }
            per_day = defaultdict(int)
            # {
            #     '2013-01-01' : 5
            # }
            per_hour = defaultdict(lambda : defaultdict(int))
            # {
            #     'saturday' : {
            #         23 : 5,
            #     }
            # }
            for use in self.session.query(model.DbUserUsedExperiment).filter(model.DbUserUsedExperiment.group_permission_id.in_(permission_ids)).all():
                users[use.user.login] += 1
                per_day[use.start_date.strftime('%Y-%m-%d')] += 1
                per_hour[use.start_date.stftime('%A').lower()][use.start_date.hour] += 1

            if per_day:
                timeline_headers, timeline_values = zip(*sorted(per_day.items(), lambda (d1, v1), (d2, v2) : cmp(d1, d2)))
            else:
                timeline_headers = timeline_values = []
            users = sorted(users.items(), lambda (l1, v1), (l2, v2) : cmp(v2, v1))
            timetable = generate_timetable(per_hour)

            return self.render('instructor_group_stats.html', experiments = sorted(experiments), timeline_headers = timeline_headers, timeline_values = timeline_values, users = users, usage_timetable = timetable, group = group)

        return "Error: you don't have permission to see that group" # TODO

