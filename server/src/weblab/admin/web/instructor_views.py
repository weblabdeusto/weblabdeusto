from __future__ import print_function, unicode_literals
import time
import math
import json
import random
import datetime

from collections import defaultdict
from StringIO import StringIO

import networkx as nx

from flask import redirect, request, Response, url_for
from flask.ext.admin import expose

from weblab.admin.web.util import WebLabAdminIndexView, WebLabBaseView, WebLabModelView

from sqlalchemy import sql, func as sa_func, distinct, not_, outerjoin

from weblab.core.babel import gettext, lazy_gettext
import weblab.permissions as permissions
import weblab.db.model as model
from .community import best_partition

def get_app_instance(view):
    return view.admin.weblab_admin_app

def is_instructor(view):
    is_admin = get_app_instance(view).is_admin()
    if is_admin:
        return True
    
    role = get_app_instance(view).get_user_role()
    return role in ('administrator', 'professor', 'instructor', 'admin')

class InstructorAuthnMixIn(object):
    @property
    def app_instance(self):
        return self.admin.weblab_admin_app

    def before_request(self):
        # self.request_context.is_admin = self.app_instance.is_admin()
        is_admin = self.app_instance.is_admin()
        if is_admin:
            self.request_context.is_instructor = True
            return True
        
        role = self.app_instance.get_user_role()
        self.request_context.is_instructor = role in ('administrator', 'professor', 'instructor', 'admin')

    def is_accessible(self):
        return self.request_context.is_instructor

    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            if self.app_instance.get_user_information() is not None:
                return redirect(url_for('not_allowed'))
            return redirect(request.url.split('/weblab/administration')[0] + '/weblab/client/#redirect={0}'.format(request.url))

        return super(InstructorAuthnMixIn, self)._handle_view(name, **kwargs)


class InstructorView(InstructorAuthnMixIn, WebLabBaseView):
    pass

class InstructorModelView(InstructorAuthnMixIn, WebLabModelView):
    pass

class ImmutableGroup(object):
    def __init__(self, group, mapping):
        self.id = group.id
        self.name = group.name
        if group.parent is None:
            self.parent = None
        else:
            if group.parent.id in mapping:
                self.parent = mapping[group.parent.id]
            else:
                self.parent = ImmutableGroup(group.parent, mapping)
                mapping[self.parent.id] = self.parent

    def __eq__(self, other):
        return isinstance(other, ImmutableGroup) and other.id == self.id

    def __hash__(self):
        return self.id

def convert_groups_to_immutable(group_list):
    new_groups = []
    mapping = {}
    for group in group_list:
        new_group = ImmutableGroup(group, mapping)
        new_groups.append(new_group)
    return new_groups

class InstructorHomeView(InstructorAuthnMixIn, WebLabAdminIndexView):
    def __init__(self, db_session, **kwargs):
        self._db_session = db_session
        super(InstructorHomeView, self).__init__(**kwargs)

    @expose()
    def index(self):
        user_information = get_app_instance(self).get_user_information()
        groups = get_assigned_groups(self, self._db_session)
        groups = convert_groups_to_immutable(groups)
        set_uses_number_in_name(self._db_session, groups)
        tree_groups = get_tree_groups(groups)
        return self.render("instructor/instructor-index.html", is_admin = get_app_instance(self).is_admin(), admin_url = get_app_instance(self).full_admin_url, user_information = user_information, groups = groups, tree_groups = tree_groups)

def get_assigned_group_ids(view, session):
    # If the user is an administrator, permissions are not relevant.
    if get_app_instance(view).is_admin():
        return [ group.id for group in session.query(model.DbGroup).all() ]

    # Otherwise, check the permissions and only return those groups
    # where the user has a specific permission
    group_ids = set()

    for permission in get_app_instance(view).get_permissions():
        if permission.name == permissions.INSTRUCTOR_OF_GROUP:
            group_id = permission.get_parameter_value(permissions.TARGET_GROUP)
            if group_id is not None:
                group_ids.add(int(group_id))

    return group_ids

def get_assigned_groups_query(view, session):
    group_ids = get_assigned_group_ids(view, session)
    return session.query(model.DbGroup).filter(model.DbGroup.id.in_(group_ids))

def get_assigned_groups(view, session):
    return get_assigned_groups_query(view, session).all()

def set_uses_number_in_name(session, group_list):
    for group in group_list:
        permission_ids = set()
        for permission in session.query(model.DbGroupPermission).filter(model.DbGroupPermission.group_id == group.id, model.DbGroupPermission.permission_type == permissions.EXPERIMENT_ALLOWED).all():
            permission_ids.add(permission.id)

        count = session.query(model.DbUserUsedExperiment).filter(model.DbUserUsedExperiment.group_permission_id.in_(permission_ids)).count()
        if count:
            group.name = group.name + ' (%s)' % count


def get_tree_groups(group_list):
    tree = defaultdict(list)

    for group in group_list:
        if group not in tree[group.parent]:
            tree[group.parent].append(group)

    for group in group_list:
        if group.parent is not None:
            parent_tree = get_tree_groups([ group.parent ])
            for g2 in parent_tree:
                if g2 not in tree:
                    tree[g2] = parent_tree[g2]
                else:
                    for g2_child in parent_tree[g2]:
                        if g2_child not in tree[g2]:
                            tree[g2].append(g2_child)
    
    return tree
            
        

def apply_instructor_filters_to_logs(view, session, logs_query):
    """ logs_query is a sqlalchemy query. Here we filter that 
    the teacher only sees those permissions for a group.
    """
    group_ids = get_assigned_group_ids(view, session)

    permission_ids = set()

    for permission in session.query(model.DbGroupPermission).filter(model.DbGroupPermission.group_id.in_(group_ids), model.DbGroupPermission.permission_type == permissions.EXPERIMENT_ALLOWED).all():
        permission_ids.add(permission.id)

    logs_query = logs_query.filter(model.DbUserUsedExperiment.group_permission_id.in_(permission_ids))
    return logs_query


class UsersPanel(InstructorModelView):

    can_edit = can_delete = can_create = False
    column_searchable_list = ('full_name', 'login')

    def __init__(self, session, **kwargs):
        super(UsersPanel, self).__init__(model.DbUser, session, **kwargs)

    def get_query(self):
        query = super(UsersPanel, self).get_query()
        groups = get_assigned_groups_query(self, self.session).subquery()
        query = query.join(groups, model.DbUser.groups)
        return query

    def get_count_query(self):
        query = super(UsersPanel, self).get_count_query()
        groups = get_assigned_groups_query(self, self.session).subquery()
        query = query.join(groups, model.DbUser.groups)
        return query

class GroupsPanel(InstructorModelView):

    can_edit = can_delete = can_create = False
    column_searchable_list = ('name',)

    def __init__(self, session, **kwargs):
        super(GroupsPanel, self).__init__(model.DbGroup, session, **kwargs)

    def get_query(self):
        query = super(GroupsPanel, self).get_query()
        query = query.filter(model.DbGroup.id.in_(get_assigned_group_ids(self, self.session)))
        return query

    def get_count_query(self):
        query = super(GroupsPanel, self).get_count_query()
        query = query.filter(model.DbGroup.id.in_(get_assigned_group_ids(self, self.session)))
        return query


class UserUsedExperimentPanel(InstructorModelView):

    can_edit = can_delete = can_create = False

    column_searchable_list = ('origin',)
    column_list = ['user', 'experiment', 'start_date', 'end_date', 'origin', 'city', 'country']
    column_labels = dict(user=lazy_gettext("User"), experiment=lazy_gettext("Experiment"), start_date=lazy_gettext("Start date"), end_date=lazy_gettext("End date"), 
                        origin=lazy_gettext("Origin"), city=lazy_gettext("City"), country=lazy_gettext("Country"))
    column_filters = ( 'user', 'start_date', 'end_date', 'experiment', 'origin', 'coord_address')

    def __init__(self, session, **kwargs):
        super(UserUsedExperimentPanel, self).__init__(model.DbUserUsedExperiment, session, **kwargs)

    def get_query(self):
        query = super(UserUsedExperimentPanel, self).get_query()
        query = apply_instructor_filters_to_logs(self, self.session, query)
        return query


    def get_count_query(self):
        query = super(UserUsedExperimentPanel, self).get_count_query()
        query = apply_instructor_filters_to_logs(self, self.session, query)
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
    #     'file_hash' : [(use.id, user.id, datetime, login), (use.id,user.id, datetime, login), (use.id, user.id, datetime, login)]
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
                            [model.DbUserUsedExperiment.id, model.DbUserUsedExperiment.user_id, model.DbUserFile.file_hash, model.DbUser.login, model.DbUser.full_name, model.DbUserUsedExperiment.start_date],
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
        # login = 'user%s' % user_id
        start_date = use['start_date']
        # full_name = use['full_name']
        # user_id_cache[user_id] = u'%s (%s)' % (full_name, login)
        user_id_cache[user_id] = login
        hashes[file_hash].append((use_id, user_id, start_date, login))

    if not hashes:
        return {}, {}

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
        first_use_id, first_user_id, use_datetime, login = hashes[file_hash][0]
        distinct_user_ids = set([ user_id for use_id, user_id, use_datetime, login in hashes[file_hash] if user_id != first_user_id ])
        for user_id in distinct_user_ids:
            links[user_id_cache[first_user_id]].append(user_id_cache[user_id])

    return links, hashes


def gefx(session, condition):
    links, _ = generate_links(session, condition)
    if not links:
        return gettext("This groups does not have any detected plagiarism")

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

def to_human(seconds):
    if seconds < 60:
        return gettext("%(num)s sec", num="%.2f" % seconds)
    elif seconds < 3600:
        return gettext("%(min)s min %(sec)s sec", min=(int(seconds) / 60), sec=(int(seconds) % 60))
    elif seconds < 24 * 3600:
        return gettext("%(hours)s hour %(min)s min", hours=(int(seconds) / 3600), min=(int(seconds) % 3600 / 60))
    else:
        return gettext("%(days)s days", days = (int(seconds) / (3600 * 24)))
    
def to_nvd3(timeline):
    # Get timeline in the form of:
    # {
    #    '2013-01-01' : 5
    # }
    # and return:
    # [
    #    [ millis_since_epoch, 5 ],
    # ]
    nvd3 = []
    for key in sorted(timeline.keys()):
        nvd3.append([
            time.mktime(time.strptime(key, "%Y-%m-%d")) * 1000,
            timeline[key]
        ])
    return nvd3


def generate_info(panel, session, condition, experiments, results):
    results['statistics'].update({
        'uses' : 0,
        'total_time' : 0
    })

    max_time = 0.1

    for exp, values in experiments.iteritems():
        max_time_allowed = max([ time_allowed for time_allowed, permission_id in values ])
        max_time = max(max_time, max_time_allowed)            

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

    user_id_cache = {}
    users = defaultdict(int)
    for user_id, login, full_name, uses in session.execute(sql.select([model.DbUser.id, model.DbUser.login, model.DbUser.full_name, sa_func.count(model.DbUserUsedExperiment.id)], 
                                                            sql.and_( model.DbUserUsedExperiment.user_id == model.DbUser.id,
                                                            condition )
                                                    ).group_by(model.DbUserUsedExperiment.user_id)):
        user_id_cache[user_id] = login
        users[login, full_name] = uses
        results['statistics']['uses'] += uses

    per_hour = defaultdict(lambda : defaultdict(int))
    # {
    #     'saturday' : {
    #         23 : 5,
    #     }
    # }
    week_days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    for hour, week_day, uses in session.execute(sql.select([model.DbUserUsedExperiment.start_date_hour, model.DbUserUsedExperiment.start_date_weekday, sa_func.count(model.DbUserUsedExperiment.id)],
                                                            condition
                                                    ).group_by(model.DbUserUsedExperiment.start_date_hour, model.DbUserUsedExperiment.start_date_weekday)):
        per_hour[week_days[week_day]][hour] = uses

    per_day = defaultdict(int)
    # {
    #     '2013-01-01' : 5
    # }
    per_week = defaultdict(int)
    # {
    #     '2013-01-01' : 5 # being 2013-01-01 that monday
    # }
    min_day = datetime.date(2100, 1, 1)
    max_day = datetime.date(1900, 1, 1)
    for start_date_date, uses in session.execute(sql.select([model.DbUserUsedExperiment.start_date_date, sa_func.count(model.DbUserUsedExperiment.id)],
                                                           condition 
                                                    ).group_by(model.DbUserUsedExperiment.start_date_date)):
        if start_date_date > max_day:
            max_day = start_date_date
        if start_date_date < min_day:
            min_day = start_date_date
        per_day[start_date_date.strftime('%Y-%m-%d')] = uses
        week_day = start_date_date.weekday()
        per_week[start_date_date - datetime.timedelta(days = week_day)] += uses

    for user_id, microseconds in session.execute(sql.select([model.DbUserUsedExperiment.user_id, sa_func.sum(model.DbUserUsedExperiment.session_time_micro)],
                                                            sql.and_(condition,
                                                            model.DbUserUsedExperiment.session_time_micro != None)
                                                    ).group_by(model.DbUserUsedExperiment.user_id)):
        users_time[user_id_cache[user_id]] = microseconds / 1000000
    results['users_time'] = users_time
                                                
    per_block_size = defaultdict(int)
    NUM_BLOCKS = 20
    block_size = max_time / NUM_BLOCKS
    for session_time_seconds, count_cases in session.execute(sql.select([model.DbUserUsedExperiment.session_time_seconds, sa_func.count(model.DbUserUsedExperiment.session_time_seconds)], condition)
                                                                  .group_by(model.DbUserUsedExperiment.session_time_seconds)):
        if session_time_seconds is not None:
            if block_size > 0:
                block_number = int(session_time_seconds / block_size)
            else:
                block_number = 0
            per_block_size[ block_number ] += count_cases


    for start_date_date, session_time_micro, session_number in session.execute(
                                                        sql.select(
                                                            [  model.DbUserUsedExperiment.start_date_date, 
                                                               sa_func.sum(model.DbUserUsedExperiment.session_time_micro), 
                                                               sa_func.count(model.DbUserUsedExperiment.id) ], 
                                                            sql.and_(condition,
                                                            model.DbUserUsedExperiment.session_time_micro != None)
                                                            ).group_by(model.DbUserUsedExperiment.start_date_date)):
        time_per_day[start_date_date.strftime('%Y-%m-%d')] = session_time_micro / session_number / 1000000
        results['statistics']['total_time'] += session_time_micro / 1000000
    
    links, hashes = generate_links(session, condition)
    # hashes = { file_hash : [ (use.id, user.id, datetime, login), ... ] }
    results['links'] = links

    if hashes:
        new_hashes = defaultdict(list)
        total_copies_per_date = defaultdict(int)
        total_copy_time_diffs = []
        min_diff = 100 * 365 * 24 * 3600 # a century
        max_diff = 0 
        # new_hashes = { (file_hash, first_login) : [ (use_id, user_id, datetime, login), ... ] } with different logins
        for file_hash, uses in hashes.items():
            original_user_id = uses[0][1]
            original_dt = uses[0][2]
            original_login = uses[0][3]
            for use_id, user_id, dt, login in uses:
                if user_id != original_user_id:
                    difference = dt - original_dt
                    difference = (difference.microseconds + (difference.seconds + difference.days * 24 * 3600) * 10**6) / 10**6
                    current_use = (use_id, user_id, dt, login, difference)
                    new_hashes[(file_hash, original_login)].append( current_use )
                    total_copies_per_date[dt.strftime('%Y-%m-%d')] += 1
                    total_copy_time_diffs.append(difference)
                    if difference > max_diff:
                        max_diff = difference
                    if difference < min_diff:
                        min_diff = difference
        
        DIFF_STEPS = 50
        DIFF_STEP  = math.log10(max_diff) / DIFF_STEPS
        diff_distribution = []

        for pos in range(DIFF_STEPS):
            min_value = 10 ** (DIFF_STEP * pos)
            max_value = 10 ** (DIFF_STEP * (pos + 1))
            current_value = 0
            for time_diff in total_copy_time_diffs:
                if min_value < time_diff <= max_value:
                    current_value += 1

            diff_distribution.append({
                'header' : "%s - %s" % (to_human(min_value), to_human(max_value)),
                'value'  : current_value,
            })

        # Remove first steps
        while diff_distribution and diff_distribution[0]['value'] == 0:
            diff_distribution.pop(0)
        

        results['copies.time.diff'] = {
            'min_diff' : min_diff,
            'max_diff' : max_diff,
            'distribution'  : json.dumps(diff_distribution),
        }
        per_day_nvd3 = to_nvd3(per_day)
        for key in per_day:
            if key not in total_copies_per_date:
                total_copies_per_date[key] = 0
        total_copies_per_date_nvd3 = to_nvd3(total_copies_per_date)

        results['copies.dates'] = {
            'normal' : per_day,
            'copies' : total_copies_per_date,
            'min'    : min_day,
            'max'    : max_day,
        }
        results['copies.timelines'] = json.dumps([
            {
                'key' : 'Total',
                'values' : per_day_nvd3
            },
            {
                'key' : 'Copies',
                'values' : total_copies_per_date_nvd3
            }
        ], indent = 4)

    results['statistics']['total_time_human'] = datetime.timedelta(seconds=int(results['statistics']['total_time']))

    per_block_headers = []
    per_block_values = []
    for block_num in range(NUM_BLOCKS):
        per_block_headers.append( '%s-%s' % (block_num * block_size, (block_num + 1) * block_size) )
        per_block_values.append(per_block_size[block_num])
    per_block_headers.append('On finish')
    per_block_values.append(per_block_size[NUM_BLOCKS])
    results['per_block_headers'] = per_block_headers
    results['per_block_values'] = per_block_values
    
    if results['mode'] in ('group', 'total'):
        results['statistics']['avg_per_user'] = 1.0 * results['statistics']['users'] / ( results['statistics']['uses'] or 1)

    if per_day:
        timeline_headers, timeline_values = zip(*sorted(per_day.items(), lambda (d1, v1), (d2, v2) : cmp(d1, d2)))
        weekly_timeline_headers, weekly_timeline_values = zip(*sorted(per_week.items(), lambda (d1, v1), (d2, v2) : cmp(d1, d2)))
        if time_per_day:
            time_per_day_headers, time_per_day_values = zip(*sorted(time_per_day.items(), lambda (d1, v1), (d2, v2) : cmp(d1, d2)))
        else:
            time_per_day_headers = time_per_day_values = []
    else:
        timeline_headers = timeline_values = []
        time_per_day_headers = time_per_day_values = []
        weekly_timeline_headers = weekly_timeline_values = []

    results['timeline_headers'] = timeline_headers
    results['timeline_values']  = timeline_values
    results['weekly_timeline_headers'] = weekly_timeline_headers
    results['weekly_timeline_values']  = weekly_timeline_values
    results['time_per_day_headers'] = time_per_day_headers
    results['time_per_day_values']  = time_per_day_values

    calendar_day_data = []
    for date, value in zip(timeline_headers, timeline_values):
        year = int(date.split('-')[0])
        if year > 1970:
            calendar_day_data.append({
                'date'  : date,
                'year'  : year,
                'value' : value
            })
    results['calendar_day_data'] = json.dumps(calendar_day_data)

    calendar_week_data = []
    for date, value in zip(weekly_timeline_headers, weekly_timeline_values):
        if date > datetime.date(1971, 1, 1):
            for x in range(7):
                current_date = date + datetime.timedelta(days = x)
                calendar_week_data.append({
                    'date'  : current_date.strftime("%Y-%m-%d"),
                    'year'  : current_date.year,
                    'value' : value
                })
    results['calendar_week_data'] = json.dumps(calendar_week_data)

    users.pop((u'boxtester', u'Box Tester'), None)
    users = sorted(users.items(), lambda (n1, v1), (n2, v2) : cmp(v2, v1))
    results['users'] = users

    timetable = generate_timetable(per_hour)
    results['usage_timetable'] = timetable

    if users:
        users_timeline_headers, users_timeline_values = zip(*users)
    else:
        users_timeline_headers = users_timeline_values = []

    users_timeline_headers = [ login for login, full_name in users_timeline_headers ]
    results['users_timeline_headers'] = users_timeline_headers
    results['users_timeline_values'] = users_timeline_values

    users_timeline_bar_data = []

    for login, value in zip(users_timeline_headers, users_timeline_values):
        users_timeline_bar_data.append({
            'header' : '%s (%s)' % (login, value),
            'value' : value
        })
    results['users_timeline_bar_data'] = json.dumps(users_timeline_bar_data)


def generate_group_info(panel, session, group, condition, experiments):
    results = dict(
        mode =  'group',
        statistics = {
            'users' : len(group.users),
        },
        experiments = sorted(experiments),
    )

    generate_info(panel, session, condition, experiments, results)

    return panel.render('instructor/instructor_group_stats.html', results = results, group = group, group_id = group.id, statistics = results['statistics'])

def generate_user_in_group_info(panel, session, user, group, condition, experiments):
    results = dict(
        mode =  'user_in_group',
        statistics = {
        },
        experiments = sorted(experiments),
    )

    generate_info(panel, session, condition, experiments, results)

    return panel.render('instructor/instructor_group_stats.html', results = results, user = user, group = group, group_id = group.id, statistics = results['statistics'])

def generate_user_in_total_info(panel, session, user, condition, experiments):
    results = dict(
        mode =  'user_in_total',
        statistics = {
        },
        experiments = sorted(experiments),
    )

    generate_info(panel, session, condition, experiments, results)

    return panel.render('instructor/instructor_group_stats.html', results = results, user = user, statistics = results['statistics'])


def generate_total_info(panel, session, experiments):
    results = dict(
        mode =  'total',
        statistics = {
            'users' : session.query(model.DbUser).count(),
        },
        experiments = sorted(experiments),
    )

    generate_info(panel, session, True, experiments, results)

    return panel.render('instructor/instructor_group_stats.html', results = results, group_id = 'total', statistics = results['statistics'])


class GroupStats(InstructorView):
    def __init__(self, session, **kwargs):
        self.session = session
        super(GroupStats, self).__init__(**kwargs)

    @expose('/')
    def index(self):
        groups = get_assigned_groups(self, self.session)
        return self.render('instructor/instructor_group_stats_index.html', groups = groups)

    @expose('/groups/<group_id>/plagiarism.gefx')
    def gefx(self, group_id):
        if group_id == 'total' and get_app_instance(self).is_admin():
            condition = True
        else:
            try:
                group_id = int(group_id)
            except:
                return "Invalid group identifier"
            if group_id not in get_assigned_group_ids(self, self.session):
                return "You don't have permissions for that group"

            permission_ids = set()
            for permission in self.session.query(model.DbGroupPermission).filter_by(group_id = group_id, permission_type = permissions.EXPERIMENT_ALLOWED).all():
                permission_ids.add(permission.id)

            condition = model.DbUserUsedExperiment.group_permission_id.in_(permission_ids)
        return gefx(self.session, condition)

    @expose('/groups/<int:group_id>/')
    def group_stats(self, group_id):
        if group_id in get_assigned_group_ids(self, self.session):
            
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

            condition = model.DbUserUsedExperiment.group_permission_id.in_(permission_ids)
            # condition = True
            # condition = sql.and_( model.DbUserUsedExperiment.start_date >= datetime.datetime(2013, 3, 4, 0, 0, 0), model.DbUserUsedExperiment.start_date < datetime.datetime(2013, 6, 2, 0, 0, 0) )
            # condition = sql.and_( model.DbUserUsedExperiment.start_date >= datetime.datetime(1971, 1, 1, 0, 0, 0))
            return generate_group_info(self, self.session, group, condition, experiments)

        return "Error: you don't have permission to see that group" # TODO

    @expose('/total/')
    def groups_total_stats(self):
        if not get_app_instance(self).is_admin():
            return "Error: you are not an admin" # TODO

        experiments = defaultdict(list)
        # {
        #     'foo@Category' : [
        #          ( time_in_seconds, permission_id )
        #     ]
        # }
        for permission in self.session.query(model.DbGroupPermission).filter_by(permission_type = permissions.EXPERIMENT_ALLOWED).all():
            exp_id = permission.get_parameter(permissions.EXPERIMENT_PERMANENT_ID).value
            cat_id = permission.get_parameter(permissions.EXPERIMENT_CATEGORY_ID).value
            time_allowed = int(permission.get_parameter(permissions.TIME_ALLOWED).value)
            experiments['%s@%s' % (exp_id, cat_id)].append((time_allowed, permission.id))

        for permission in self.session.query(model.DbUserPermission).filter_by(permission_type = permissions.EXPERIMENT_ALLOWED).all():
            exp_id = permission.get_parameter(permissions.EXPERIMENT_PERMANENT_ID).value
            cat_id = permission.get_parameter(permissions.EXPERIMENT_CATEGORY_ID).value
            time_allowed = int(permission.get_parameter(permissions.TIME_ALLOWED).value)
            experiments['%s@%s' % (exp_id, cat_id)].append((time_allowed, permission.id))

        for permission in self.session.query(model.DbRolePermission).filter_by(permission_type = permissions.EXPERIMENT_ALLOWED).all():
            exp_id = permission.get_parameter(permissions.EXPERIMENT_PERMANENT_ID).value
            cat_id = permission.get_parameter(permissions.EXPERIMENT_CATEGORY_ID).value
            time_allowed = int(permission.get_parameter(permissions.TIME_ALLOWED).value)
            experiments['%s@%s' % (exp_id, cat_id)].append((time_allowed, permission.id))

        return generate_total_info(self, self.session, experiments)
       

    @expose('/users/<login>/in_group/<int:group_id>')
    def user_in_group_stats(self, login, group_id):
        if group_id in get_assigned_group_ids(self, self.session):
            
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

            user = self.session.query(model.DbUser).filter_by(login = login).first()
            if user:
                user_id = user.id
            else:
                user_id = -1

            condition = sql.and_(model.DbUserUsedExperiment.group_permission_id.in_(permission_ids), model.DbUserUsedExperiment.user_id == user_id)
            # condition = True
            # condition = sql.and_( model.DbUserUsedExperiment.start_date >= datetime.datetime(2013, 3, 4, 0, 0, 0), model.DbUserUsedExperiment.start_date < datetime.datetime(2013, 6, 2, 0, 0, 0) )
            # condition = sql.and_( model.DbUserUsedExperiment.start_date >= datetime.datetime(1971, 1, 1, 0, 0, 0))
            return generate_user_in_group_info(self, self.session, user, group, condition, experiments)

        return "Error: you don't have permission to see that group" # TODO

    @expose('/users/<login>/total/')
    def user_in_total_stats(self, login):
        if get_app_instance(self).is_admin():
            experiments = defaultdict(list)
            # {
            #     'foo@Category' : [
            #          ( time_in_seconds, permission_id )
            #     ]
            # }
            for permission in self.session.query(model.DbGroupPermission).filter_by(permission_type = permissions.EXPERIMENT_ALLOWED).all():
                exp_id = permission.get_parameter(permissions.EXPERIMENT_PERMANENT_ID).value
                cat_id = permission.get_parameter(permissions.EXPERIMENT_CATEGORY_ID).value
                time_allowed = int(permission.get_parameter(permissions.TIME_ALLOWED).value)
                experiments['%s@%s' % (exp_id, cat_id)].append((time_allowed, permission.id))
            for permission in self.session.query(model.DbUserPermission).filter_by(permission_type = permissions.EXPERIMENT_ALLOWED).all():
                exp_id = permission.get_parameter(permissions.EXPERIMENT_PERMANENT_ID).value
                cat_id = permission.get_parameter(permissions.EXPERIMENT_CATEGORY_ID).value
                time_allowed = int(permission.get_parameter(permissions.TIME_ALLOWED).value)
                experiments['%s@%s' % (exp_id, cat_id)].append((time_allowed, permission.id))
            for permission in self.session.query(model.DbRolePermission).filter_by(permission_type = permissions.EXPERIMENT_ALLOWED).all():
                exp_id = permission.get_parameter(permissions.EXPERIMENT_PERMANENT_ID).value
                cat_id = permission.get_parameter(permissions.EXPERIMENT_CATEGORY_ID).value
                time_allowed = int(permission.get_parameter(permissions.TIME_ALLOWED).value)
                experiments['%s@%s' % (exp_id, cat_id)].append((time_allowed, permission.id))

            user = self.session.query(model.DbUser).filter_by(login = login).first()
            if user:
                user_id = user.id
            else:
                return "User not found"

            condition = model.DbUserUsedExperiment.user_id == user_id
            return generate_user_in_total_info(self, self.session, user, condition, experiments)

        return "Error: you don't have permission to see that group" # TODO

