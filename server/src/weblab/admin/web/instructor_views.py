from collections import defaultdict
import random
import datetime
from StringIO import StringIO

import networkx as nx

from flask import redirect, request, flash, Response
from flask.ext.admin import expose, AdminIndexView, BaseView
from flask.ext.admin.contrib.sqla import ModelView

from sqlalchemy import sql, func as sa_func, distinct, not_, outerjoin

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

EMPTY_HASHES = (
    '',
    '{sha}f96cea198ad1dd5617ac084a3d92c6107708c0ef', # '{sha}' + hashlib.new("sha", "").hexdigest()
    '{sha}da39a3ee5e6b4b0d3255bfef95601890afd80709', # '{sha}' + sha.new("").hexdigest()
    '<file not yet stored>',
)

def generate_links(session, condition):
    hashes = defaultdict(list)
    # 
    # {
    #     'file_hash' : [(use.id, user.id), (use.id,user.id), (use.id, user.id)]
    # }
    #
    multiuser_file_hashes = sql.select(
                            [model.DbUserFile.file_hash],
                            sql.and_( 
                                condition,
                                model.DbUserFile.experiment_use_id == model.DbUserUsedExperiment.id,
                                model.DbUser.id == model.DbUserUsedExperiment.user_id,
                                not_(model.DbUserFile.file_hash.in_(EMPTY_HASHES))
                            ),
                            use_labels = True
                        ).group_by(model.DbUserFile.file_hash).having(sa_func.count(distinct(model.DbUserUsedExperiment.user_id)) > 1).alias('foo')

    joined = outerjoin(multiuser_file_hashes, model.DbUserFile, model.DbUserFile.file_hash == multiuser_file_hashes.c.UserFile_file_hash)

    files_query = sql.select(
                            [model.DbUserUsedExperiment.id, model.DbUserUsedExperiment.user_id, model.DbUserFile.file_hash, model.DbUser.login],
                            sql.and_( 
                                condition,
                                model.DbUserFile.experiment_use_id == model.DbUserUsedExperiment.id,
                                model.DbUser.id == model.DbUserUsedExperiment.user_id
                            )
                        ).select_from(joined)

    user_id_cache = {}
    for use in session.execute(files_query):
        use_id  = use['id']
        user_id = use['user_id']
        file_hash = use['file_hash']
        login = use['login']
        user_id_cache[user_id] = login
        hashes[file_hash].append((use_id, user_id))

    if not hashes:
        return {}

    # No group by since there is no easy way to order correctly, and the amount of data is not
    # huge
    query = sql.select( [model.DbUserFile.file_hash, model.DbRole.name], 
                        sql.and_(
                            model.DbUserFile.experiment_use_id == model.DbUserUsedExperiment.id,
                            model.DbUserUsedExperiment.user_id == model.DbUser.id,
                            model.DbUser.role_id == model.DbRole.id,
                            model.DbUserFile.file_hash.in_(hashes.keys())
                        )).order_by(model.DbUserUsedExperiment.start_date)

    correct_file_hashes = set()
    for file_hash, role_name in session.execute(query):
        if file_hash in correct_file_hashes:
            continue
        
        if role_name in ('administrator', 'professor', 'admin', 'instructor'):
            hashes.pop(file_hash, None)
        else:
            correct_file_hashes.add(file_hash)

    # Filter those hashes which were first used by users who were instructor, admin, etc.
    # It's only a problem when the file has been previously submitted by someone who was not a teacher
    links = defaultdict(list)

    # With the remaining, calculate the copies
    for file_hash in hashes:
        # Get first in course
        first_use_id, first_user_id = hashes[file_hash][0]
        distinct_user_ids = set([ user_id for use_id, user_id in hashes[file_hash] if user_id != first_user_id ])
        for user_id in distinct_user_ids:
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

        condition = model.DbUserUsedExperiment.group_permission_id.in_(permission_ids)
        links = generate_links(self.session, condition)
        if not links:
            return "This groups does not have any detected plagiarism"

        G = nx.DiGraph()
        
        for source_node in links:
            for target_node in set(links[source_node]):
                weight = links[source_node].count(target_node)
                G.add_edge(source_node, target_node, weight=weight)

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

            condition = model.DbUserUsedExperiment.group_permission_id.in_(permission_ids)
            # condition = True

            # Get something different per experiment
            # TODO
            # if len(permission_ids) > 1:
            #     pass

            # Get the totals
            users_time = defaultdict(int)
            # {
            #     login : seconds
            # }
            time_per_day = defaultdict(list)
            # {
            #     '2013-01-01' : [5,3,5]
            # }
            all_times = []
            max_time = 0

            user_id_cache = {}
            users = defaultdict(int)
            for user_id, login, full_name, uses in self.session.execute(sql.select([model.DbUser.id, model.DbUser.login, model.DbUser.full_name, sa_func.count(model.DbUserUsedExperiment.id)], 
                                                                    sql.and_( model.DbUserUsedExperiment.user_id == model.DbUser.id,
                                                                    condition )
                                                            ).group_by(model.DbUserUsedExperiment.user_id)):
                user_id_cache[user_id] = login
                users[login, full_name] = uses
                statistics['uses'] += uses

            per_hour = defaultdict(lambda : defaultdict(int))
            # {
            #     'saturday' : {
            #         23 : 5,
            #     }
            # }
            week_days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
            for hour, week_day, uses in self.session.execute(sql.select([model.DbUserUsedExperiment.start_date_hour, model.DbUserUsedExperiment.start_date_weekday, sa_func.count(model.DbUserUsedExperiment.id)],
                                                                    condition
                                                            ).group_by(model.DbUserUsedExperiment.start_date, model.DbUserUsedExperiment.start_date_weekday)):
                print hour, week_day, uses
                # XXX FIXME
                # TODO: failing: uses always = 1
                per_hour[week_days[week_day]][hour] = uses

            per_day = defaultdict(int)
            # {
            #     '2013-01-01' : 5
            # }
            for start_date_date, uses in self.session.execute(sql.select([model.DbUserUsedExperiment.start_date_date, sa_func.count(model.DbUserUsedExperiment.id)],
                                                                   condition 
                                                            ).group_by(model.DbUserUsedExperiment.start_date_date)):
                per_day[start_date_date.strftime('%Y-%m-%d')] = uses

            for user_id, microseconds in self.session.execute(sql.select([model.DbUserUsedExperiment.user_id, sa_func.sum(model.DbUserUsedExperiment.session_time_micro)],
                                                                    sql.and_(condition,
                                                                    model.DbUserUsedExperiment.end_date != None)
                                                            ).group_by(model.DbUserUsedExperiment.user_id)):
                users_time[user_id_cache[user_id]] = microseconds / 1000000
                                                        

            import time
            before_long = time.time()
            # TODO: How to optimize this one? We could group by  (session_time, experiment_id)
            # Being session_time in seconds. There will be many repeated with that granularity.
            for session_time_micro, start_date_date, exp_name, cat_name, user_id in self.session.execute(sql.select([model.DbUserUsedExperiment.session_time_micro, model.DbUserUsedExperiment.start_date_date, model.DbExperiment.name, model.DbExperimentCategory.name, model.DbUserUsedExperiment.user_id],
                                                                sql.and_(
                                                                    model.DbExperiment.category_id == model.DbExperimentCategory.id,
                                                                    model.DbUserUsedExperiment.experiment_id == model.DbExperiment.id,
                                                                    condition,
                                                                    model.DbUserUsedExperiment.end_date != None,
                                                                ))):
                session_time_seconds = session_time_micro / 1e6
                try:
                    max_time = max([ time_allowed for time_allowed, _ in experiments['%s@%s' % (exp_name, cat_name)] ])
                except:
                    # TODO
                    continue
                session_time_seconds = min(max_time, session_time_seconds)
                max_time = max(max_time, session_time_seconds)
                all_times.append(session_time_seconds)
                statistics['total_time'] += session_time_seconds
                time_per_day[start_date_date.strftime('%Y-%m-%d')].append(session_time_seconds)

            end_long = time.time()
            print end_long - before_long

            links = generate_links(self.session, condition)

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

