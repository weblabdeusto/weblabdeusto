from __future__ import print_function, unicode_literals
"""Add group_permission_id

Revision ID: f1ce7950ae8
Revises: 3614197cb5da
Create Date: 2014-01-13 16:54:33.181578

"""

# revision identifiers, used by Alembic.
revision = 'f1ce7950ae8'
down_revision = '3614197cb5da'

import time
import datetime
from alembic import op
import sqlalchemy as sa
import sqlalchemy.sql as sql

import os, sys
sys.path.append(os.path.join('..','..','..','..'))
import weblab.permissions as permissions

metadata = sa.MetaData()
uue = sa.Table('UserUsedExperiment', metadata,
    sa.Column('id', sa.Integer()),
    sa.Column('start_date', sa.DateTime()),
    sa.Column('user_permission_id', sa.Integer()),
    sa.Column('group_permission_id', sa.Integer()),
    sa.Column('role_permission_id', sa.Integer()),
    sa.Column('user_id', sa.Integer()),
    sa.Column('experiment_id', sa.Integer()),
)

user = sa.Table('User', metadata,
    sa.Column('id', sa.Integer()),
    sa.Column('role_id', sa.Integer()),
    sa.Column('login', sa.String(32)),
)

group = sa.Table('Group', metadata,
    sa.Column('id', sa.Integer()),
    sa.Column('parent_id', sa.Integer()),
)

user_is_member_of = sa.Table('UserIsMemberOf', metadata,
    sa.Column('user_id', sa.Integer()),
    sa.Column('group_id', sa.Integer()),
)

exp = sa.Table('Experiment', metadata,
    sa.Column('id', sa.Integer()),
    sa.Column('category_id', sa.Integer()),
    sa.Column('name', sa.String(255)),
)

cat = sa.Table('ExperimentCategory', metadata,
    sa.Column('id', sa.Integer()),
    sa.Column('name', sa.String(255)),
)

user_permission = sa.Table('UserPermission', metadata,
    sa.Column('id', sa.Integer()),
    sa.Column('user_id', sa.Integer()),
    sa.Column('permission_type', sa.String(255)),
    sa.Column('date', sa.DateTime),
)

group_permission = sa.Table('GroupPermission', metadata,
    sa.Column('id', sa.Integer()),
    sa.Column('group_id', sa.Integer()),
    sa.Column('permission_type', sa.String(255)),
    sa.Column('date', sa.DateTime),
)

role_permission = sa.Table('RolePermission', metadata,
    sa.Column('id', sa.Integer()),
    sa.Column('role_id', sa.Integer()),
    sa.Column('permission_type', sa.String(255)),
    sa.Column('date', sa.DateTime),
)

user_permission_parameter = sa.Table('UserPermissionParameter', metadata,
    sa.Column('id', sa.Integer()),
    sa.Column('permission_id', sa.Integer()),
    sa.Column('permission_type_parameter', sa.String(255)),
    sa.Column('value', sa.Text()),
)

group_permission_parameter = sa.Table('GroupPermissionParameter', metadata,
    sa.Column('id', sa.Integer()),
    sa.Column('permission_id', sa.Integer()),
    sa.Column('permission_type_parameter', sa.String(255)),
    sa.Column('value', sa.Text()),
)

role_permission_parameter = sa.Table('RolePermissionParameter', metadata,
    sa.Column('id', sa.Integer()),
    sa.Column('permission_id', sa.Integer()),
    sa.Column('permission_type_parameter', sa.String(255)),
    sa.Column('value', sa.Text()),
)

GROUP_CACHE = {
    # (group_id, exp_name, cat_name) : [ permission1, permission2 ]
}

ROLE_CACHE = {
    # (role_id, exp_name, cat_name) : [ permission1, permission2 ]
}

USER_CACHE = {
    # (user_id, exp_name, cat_name) : [ permission1, permission2 ]
}

def _get_group_permissions_recursive(connection, group_id, parent_id, group_ids, exp_name, cat_name):
    cache_key = group_id, exp_name, cat_name
    if cache_key in GROUP_CACHE:
        return GROUP_CACHE[cache_key]

    if group_id in group_ids:
        return []
    
    group_ids.append(group_id)

    group_permissions = []

    current = _get_permissions_by_condition(connection, 'group', group_permission.c.group_id == group_id, exp_name, cat_name)
    group_permissions.extend(current)

    if parent_id is not None:
        grandparent_query = sql.select([group.c.parent_id], group.c.id == group_id).limit(1)

        grandparent_id = None
        for row in connection.execute(grandparent_query):
            grandparent_id = row[group.c.parent_id]

        parent_permissions = _get_group_permissions_recursive(connection, parent_id, grandparent_id, group_ids, exp_name, cat_name)
        group_permissions.extend(parent_permissions)

    GROUP_CACHE[cache_key] = group_permissions
    return group_permissions

def _get_group_permissions(connection, user_id, exp_name, cat_name):
    group_permissions = []
    s = sql.select([ user_is_member_of.c.group_id, group.c.parent_id ], sql.and_(user_is_member_of.c.user_id == user_id, user_is_member_of.c.group_id == group.c.id) )
    for row in connection.execute(s):
        group_id = row[user_is_member_of.c.group_id]
        parent_id = row[group.c.parent_id]
        current = _get_group_permissions_recursive(connection, group_id, parent_id, [], exp_name, cat_name)
        group_permissions.extend(current)

    return group_permissions

def _get_experiment_id(connection, table, permission_id):
    s = sql.select([table.c.permission_type_parameter, table.c.value], sql.and_(
                    table.c.permission_id == permission_id, 
                    sql.or_(
                        table.c.permission_type_parameter == permissions.EXPERIMENT_PERMANENT_ID,
                        table.c.permission_type_parameter == permissions.EXPERIMENT_CATEGORY_ID,
                        table.c.permission_type_parameter == permissions.TIME_ALLOWED,
                    )))
    exp_name = None
    cat_name = None
    time_allowed = None
    for row in connection.execute(s):
        parameter_type = row[table.c.permission_type_parameter]
        if parameter_type == permissions.EXPERIMENT_PERMANENT_ID:
            exp_name = row[table.c.value]
        elif parameter_type == permissions.EXPERIMENT_CATEGORY_ID:
            cat_name = row[table.c.value]
        else:
            time_allowed = row[table.c.value]

    return exp_name, cat_name, time_allowed

def _get_permissions_by_condition(connection, scope, condition, exp_name, cat_name):
    table = globals()['%s_permission' % scope]
    parameter_table = globals()['%s_permission_parameter' % scope]

    current_permissions = []

    s = sql.select([table.c.id, table.c.date], 
                sql.and_(condition, table.c.permission_type == permissions.EXPERIMENT_ALLOWED))

    for row in connection.execute(s):
        exp_retrieved, cat_retrieved, time_allowed = _get_experiment_id(connection, parameter_table, row[table.c.id])
        if exp_retrieved == exp_name and cat_retrieved == cat_name:
            current_permissions.append({
                'id' : row[table.c.id],
                'scope' : scope,
                'time_allowed' : int(time_allowed),
                'start_date' : row[table.c.date],
            })
    return current_permissions

def _get_permissions(connection, user_id, user_role_id, exp_name, cat_name):
    user_cache_key = user_id, exp_name, cat_name
    if user_cache_key in USER_CACHE:
        return USER_CACHE[user_cache_key]

    current_permissions = [
#        {
#            'id' : 5,
#            'scope' : 'group', # or user or role,
#            'time_allowed' : 100,
#            'start_date' : datetime.datetime
#        }
    ]
    
    user_permissions = _get_permissions_by_condition(connection, 'user', user_permission.c.user_id == user_id, exp_name, cat_name)
    current_permissions.extend(user_permissions)

    group_permissions = _get_group_permissions(connection, user_id, exp_name, cat_name)
    current_permissions.extend(group_permissions)

    role_cache_key = user_role_id, exp_name, cat_name
    if role_cache_key in ROLE_CACHE:
        current_permissions.extend(ROLE_CACHE[role_cache_key])
    else:
        role_permissions = _get_permissions_by_condition(connection, 'role', role_permission.c.role_id == user_role_id, exp_name, cat_name)
        current_permissions.extend(role_permissions)
        ROLE_CACHE[role_cache_key] = role_permissions

    USER_CACHE[user_cache_key] = current_permissions
    return current_permissions

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    engine = op.get_bind()
    if engine.dialect.name == 'sqlite':
        # Same but without Foreign keys
        op.add_column(u'UserUsedExperiment', sa.Column('group_permission_id', sa.Integer(), nullable=True))
        op.add_column(u'UserUsedExperiment', sa.Column('user_permission_id', sa.Integer(), nullable=True))
        op.add_column(u'UserUsedExperiment', sa.Column('role_permission_id', sa.Integer(), nullable=True))
    else:
        op.add_column(u'UserUsedExperiment', sa.Column('group_permission_id', sa.Integer(), sa.ForeignKey('GroupPermission.id'), nullable=True))
        op.add_column(u'UserUsedExperiment', sa.Column('user_permission_id', sa.Integer(), sa.ForeignKey('UserPermission.id'), nullable=True))
        op.add_column(u'UserUsedExperiment', sa.Column('role_permission_id', sa.Integer(), sa.ForeignKey('RolePermission.id'), nullable=True))
    ### end Alembic commands ###
    s = sql.select([
                uue.c.id, uue.c.start_date,
                uue.c.user_permission_id, uue.c.group_permission_id, uue.c.role_permission_id,
                user.c.id, user.c.login, user.c.role_id,
                exp.c.name, cat.c.name,
                ], sql.and_(uue.c.user_id == user.c.id, uue.c.experiment_id == exp.c.id, exp.c.category_id == cat.c.id,
                ),
                use_labels = True 
        ).order_by(uue.c.id)

    skipped = []

    total_uses_count = op.get_bind().execute(sql.select([sa.func.count(uue.c.id)]))
    
    total_uses = [ x[0] for x in total_uses_count ][0]

    if total_uses:
        print("Converting %s uses" % total_uses)

    last_time = time.time()
    
    operations = []
    counter = 0
    for use in op.get_bind().execute(s):
        group_permission_id = use[uue.c.group_permission_id]
        user_permission_id = use[uue.c.user_permission_id]
        role_permission_id = use[uue.c.role_permission_id]
        counter += 1

        if counter % 1000 == 0:
            new_last_time = time.time()
            timespan = new_last_time - last_time
            speed = 1000.0 / timespan
            cur_time = time.asctime()
            print("%s Reading %s out of %s (%.2f%%). 1000 uses processed in %.2f seconds (%.2f uses / second)." % (cur_time, counter, total_uses, 100.0 * counter / total_uses, timespan, speed))
            last_time = new_last_time

        if not user_permission_id and not group_permission_id and not role_permission_id:
            use_id   = use[uue.c.id]
            user_id  = use[user.c.id]
            exp_name = use[exp.c.name]
            cat_name = use[cat.c.name]
            use_date = use[uue.c.start_date]
            user_role_id = use[user.c.role_id]

            current_permissions = _get_permissions(op.get_bind(), user_id, user_role_id, exp_name, cat_name)

            potential_permissions = []
            # Discard permissions assigned AFTER the use (this can happen when somebody repeats)
            for current_permission in current_permissions:
                # We give a 24 hour margin due to UTC issues
                if (current_permission['start_date'] - datetime.timedelta(hours = 24) ) <= use_date:
                    potential_permissions.append(current_permission)

            if not potential_permissions:
                if not current_permissions:
                    skipped.append( (use_id, unicode(use[user.c.login]), exp_name, cat_name) )
                    continue
                else:
                    # If there was not permission before that
                    potential_permissions = current_permissions

            # Sort permissions by time_allowed
            potential_permissions.sort(lambda p1, p2: cmp(p2['time_allowed'], p1['time_allowed']))

            # Break by wherever the time_allowed is lower, and discard them
            break_point = len(potential_permissions)
            for position, potential_permission in enumerate(potential_permissions):
                if potential_permission['time_allowed'] < potential_permissions[0]['time_allowed']:
                    break_point = position
                    break

            potential_permissions = potential_permissions[:break_point]
            # Sort by date: most recent - oldest.
            potential_permissions.sort(lambda p1, p2: cmp(p2['start_date'], p1['start_date']))

            assigned_permission = potential_permissions[0]

            kwargs = {}
            if assigned_permission['scope'] == 'group':
                kwargs = dict(group_permission_id = assigned_permission['id'])
            elif assigned_permission['scope'] == 'user':
                kwargs = dict(user_permission_id = assigned_permission['id'])
            elif assigned_permission['scope'] == 'role':
                kwargs = dict(role_permission_id = assigned_permission['id'])
            
            if kwargs:
                update_stmt = uue.update().where(uue.c.id == use_id).values(**kwargs)
                operations.append(update_stmt)

    if total_uses > 1000:
        new_last_time = time.time()
        timespan = new_last_time - last_time
        remainder = total_uses % 1000
        speed = 1.0 * remainder / timespan
        cur_time = time.asctime()
        print("%s Found %s out of %s (%.2f%%). %s uses processed in %.2f seconds (%.2f uses / second)." % (cur_time, counter, total_uses, 100.0 * counter / total_uses, remainder, timespan, speed))
        last_time = new_last_time

    print("Executing %s operations..." % len(operations))
    for pos, operation in enumerate(operations):
        if pos % 1000 == 0 and pos > 0:
            new_last_time = time.time()
            timespan = new_last_time - last_time
            speed = 1000.0 / timespan
            cur_time = time.asctime()
            print("%s Processing %s out of %s (%.2f%%). 1000 uses processed in %.2f seconds (%.2f uses / second)." % (cur_time, pos, total_uses, 100.0 * pos / total_uses, timespan, speed))
            last_time = new_last_time
        op.execute(operation)
    print("Finished")

    if skipped:
        print("Warning. The following usages (total = %s) did not have any permission assigned and have been skipped:" % len(skipped))
        for use_id, login, exp_name, cat_name in skipped:
            print("\tUsage id=%s by %s on %s@%s" % (use_id, login, exp_name, cat_name))
        print("You can see those by searching uses with user_permission_id, group_permission_id and role_permission_id set all to NULL")
        print()

def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column(u'UserUsedExperiment', 'role_permission_id')
    op.drop_column(u'UserUsedExperiment', 'user_permission_id')
    op.drop_column(u'UserUsedExperiment', 'group_permission_id')
    ### end Alembic commands ###
