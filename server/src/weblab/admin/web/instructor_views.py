from collections import defaultdict
import random
import datetime
from StringIO import StringIO

import networkx as nx

from flask import redirect, request, flash, Response
from flask.ext.admin import expose, AdminIndexView, BaseView
from flask.ext.admin.contrib.sqla import ModelView

import weblab.permissions as permissions
import weblab.db.model as model
from .community import best_partition

def get_app_instance():
    import weblab.admin.web.app as admin_app
    return admin_app.AdministrationApplication.INSTANCE

def is_instructor():
    is_admin = get_app_instance().is_admin()
    if is_admin:
        return True
    
    return get_app_instance().get_user_role() in ('administrator', 'professor', 'instructor', 'admin')

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
        tree_groups = get_tree_groups(groups)
        return self.render("instructor-index.html", is_admin = get_app_instance().is_admin(), admin_url = get_app_instance().full_admin_url, user_information = user_information, groups = groups, tree_groups = tree_groups)

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

def get_tree_groups(group_list):
    tree = defaultdict(list)

    for group in group_list:
        tree[group.parent].append(group)
    
    return tree    
            
        

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
    column_searchable_list = ('full_name', 'login')

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
    column_searchable_list = ('name',)

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

    column_searchable_list = ('origin',)
    column_list = ['user', 'experiment', 'start_date', 'end_date', 'origin']
    column_filters = ( 'user', 'start_date', 'end_date', 'experiment', 'origin', 'coord_address')

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

def generate_links(hashes, session, user_id_cache):
    EMPTY_HASHES = (
        '',
        '{sha}f96cea198ad1dd5617ac084a3d92c6107708c0ef', # '{sha}' + hashlib.new("sha", "").hexdigest()
        '{sha}da39a3ee5e6b4b0d3255bfef95601890afd80709', # '{sha}' + sha.new("").hexdigest()
        '<file not yet stored>',
    )

    if not hashes:
        return {}

    links = defaultdict(list)

    for file_hash in hashes:
        if file_hash in EMPTY_HASHES:
            # Those files are irrelevant
            continue

        distinct_user_ids = set([ user_id for use_id, user_id in hashes[file_hash] ])
        if len(distinct_user_ids) > 1:
            # One student sending multiple files is not a problem
            first_element = session.query(model.DbUserFile).filter_by(file_hash = file_hash).first()
            if first_element and first_element.experiment_use.user.role.name not in ('administrator', 'professor', 'admin', 'instructor'):
                # It's only a problem when the file has been previously submitted by someone who was not a teacher

                # Get first in course
                first_use_id, first_user_id = hashes[file_hash][0]
                for user_id in distinct_user_ids:
                    if user_id != first_user_id:
                        links[user_id_cache[first_user_id]].append(user_id_cache[user_id])
    return links


class GroupStats(InstructorView):
    def __init__(self, session, **kwargs):
        self.session = session
        super(GroupStats, self).__init__(**kwargs)

    @expose('/')
    def index(self):
        groups = get_assigned_groups(self.session)
        return self.render('instructor_group_stats_index.html', groups = groups)

    @expose('/groups/<int:group_id>/plagiarism.gefx')
    def gefx(self, group_id):
        if group_id not in get_assigned_group_ids(self.session):
            return "You don't have permissions for that group"

        permission_ids = set()
        for permission in self.session.query(model.DbGroupPermission).filter_by(group_id = group_id, permission_type = permissions.EXPERIMENT_ALLOWED).all():
            permission_ids.add(permission.id)

        hashes = defaultdict(list)
        # 
        # {
        #     'file_hash' : [(use.id, user.id), (use.id,user.id), (use.id, user.id)]
        # }
        # 
        user_id_cache = {}

        for use in self.session.query(model.DbUserUsedExperiment).filter(model.DbUserUsedExperiment.group_permission_id.in_(permission_ids)).all():
            user = use.user
            user_id_cache[user.id] = user.login

            for f in use.files:
                hashes[f.file_hash].append((use.id, user.id))

        links = generate_links(hashes, self.session, user_id_cache)
        if not links:
            return "This groups does not have any detected plagiarism"

        G = nx.DiGraph()
        
        for source_node in links:
            for target_node in set(links[source_node]):
                weight = links[source_node].count(target_node)
                # G.add_edge(source_node, target_node, weight=weight)
                G.add_edge(source_node, target_node)

        out_degrees = G.out_degree()
        in_degrees = G.in_degree()

        for name in G.nodes():
             G.node[name]['out_degree'] = out_degrees[name]
             G.node[name]['in_degree'] = in_degrees[name]

        G_undirected = G.to_undirected();
        partitions = best_partition(G_undirected)
        colors = {}
        for member, c in partitions.items():
            if not colors.has_key(c):
                r = random.randrange(64,192)
                g = random.randrange(64,192)
                b = random.randrange(64,192)
                colors[c] = (r, g, b)
            G.node[member]["viz"] = {
                'color': { 
                  'r': colors[c][0],
                  'g': colors[c][1],
                  'b': colors[c][2],
                },
                'size': 5 * G.node[member]['out_degree']
            }

        output = StringIO()
        nx.write_gexf(G, output)
        return Response(output.getvalue(), mimetype='text/xml')

    @expose('/groups/<int:group_id>/')
    def group_stats(self, group_id):
        if group_id in get_assigned_group_ids(self.session):
            
            group = self.session.query(model.DbGroup).filter_by(id = group_id).first()

            statistics = {
                'users' : len(group.users),
                'uses' : 0,
                'total_time' : 0
            }

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
            users_time = defaultdict(int)
            # {
            #     login : seconds
            # }
            per_day = defaultdict(int)
            # {
            #     '2013-01-01' : 5
            # }
            time_per_day = defaultdict(list)
            # {
            #     '2013-01-01' : [5,3,5]
            # }
            per_hour = defaultdict(lambda : defaultdict(int))
            # {
            #     'saturday' : {
            #         23 : 5,
            #     }
            # }
            all_times = []
            max_time = 0

            hashes = defaultdict(list)
            # 
            # {
            #     'file_hash' : [(use.id, user.id), (use.id,user.id), (use.id, user.id)]
            # }
            # 

            user_id_cache = {}

            for use in self.session.query(model.DbUserUsedExperiment).filter(model.DbUserUsedExperiment.group_permission_id.in_(permission_ids)).all():
                user = use.user
                users[user.login, user.full_name] += 1
                user_id_cache[user.id] = user.login


                per_day[use.start_date.strftime('%Y-%m-%d')] += 1
                per_hour[use.start_date.strftime('%A').lower()][use.start_date.hour] += 1
                statistics['uses'] += 1
                for f in use.files:
                    hashes[f.file_hash].append((use.id, user.id))
                if use.end_date is not None:
                    td = (use.end_date - use.start_date)
                    session_time_seconds = (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 10**6
                    max_time = max([ time_allowed for time_allowed, _ in experiments['%s@%s' % (use.experiment.name, use.experiment.category.name)] ])
                    session_time_seconds = min(max_time, session_time_seconds)
                    max_time = max(max_time, session_time_seconds)
                    all_times.append(session_time_seconds)
                    statistics['total_time'] += session_time_seconds
                    users_time[user.login] += session_time_seconds
                    time_per_day[use.start_date.strftime('%Y-%m-%d')].append(session_time_seconds)
   
            links = generate_links(hashes, self.session, user_id_cache)

            statistics['total_time_human'] = datetime.timedelta(seconds=statistics['total_time'])

            # Times
            NUM_BLOCKS = 20
            per_block_size = defaultdict(int)
            block_size = max_time / NUM_BLOCKS
            for time in all_times:
                per_block_size[ int(time / block_size) ] += 1

            per_block_headers = []
            per_block_values = []
            for block_num in range(NUM_BLOCKS):
                per_block_headers.append( '%s-%s' % (block_num * block_size, (block_num + 1) * block_size) )
                per_block_values.append(per_block_size[block_num])
            per_block_headers.append('On finish')
            per_block_values.append(per_block_size[NUM_BLOCKS])
            
            statistics['avg_per_user'] = 1.0 * statistics['users'] / ( statistics['uses'] or 1)

            if per_day:
                timeline_headers, timeline_values = zip(*sorted(per_day.items(), lambda (d1, v1), (d2, v2) : cmp(d1, d2)))
                for day in time_per_day:
                    time_per_day[day] = sum(time_per_day[day]) / len(time_per_day[day])
                time_per_day_headers, time_per_day_values = zip(*sorted(time_per_day.items(), lambda (d1, v1), (d2, v2) : cmp(d1, d2)))
            else:
                timeline_headers = timeline_values = []
                time_per_day_headers = time_per_day_values = []
            users = sorted(users.items(), lambda (n1, v1), (n2, v2) : cmp(v2, v1))
            timetable = generate_timetable(per_hour)

            if users:
                users_timeline_headers, users_timeline_values = zip(*users)
            else:
                users_timeline_headers = users_timeline_values = []

            users_timeline_headers = [ login for login, full_name in users_timeline_headers ]

            return self.render('instructor_group_stats.html', experiments = sorted(experiments), timeline_headers = timeline_headers, timeline_values = timeline_values, time_per_day_headers = time_per_day_headers, time_per_day_values = time_per_day_values, users = users, usage_timetable = timetable, group = group, statistics = statistics, per_block_size = per_block_size, users_time = users_time, users_timeline_headers = users_timeline_headers, users_timeline_values = users_timeline_values, per_block_headers = per_block_headers, per_block_values = per_block_values, links = links)

        return "Error: you don't have permission to see that group" # TODO

