from __future__ import print_function, unicode_literals
"""Add new permission to administrator

Revision ID: 498a6d3a1e0f
Revises: 40cdc63a949a
Create Date: 2015-07-19 23:32:37.230646

"""

# revision identifiers, used by Alembic.
revision = '498a6d3a1e0f'
down_revision = u'40cdc63a949a'

import datetime

from alembic import op
import sqlalchemy as sa
import sqlalchemy.sql as sql

metadata = sa.MetaData()
role = sa.Table('Role', metadata,
    sa.Column('id', sa.Integer()),
    sa.Column('name', sa.Unicode(20)),
)

role_permission = sa.Table('RolePermission', metadata,
    sa.Column('id', sa.Integer()),
    sa.Column('role_id', sa.Integer()),
    sa.Column('permission_type', sa.String(255)),
    sa.Column('permanent_id', sa.String(255)),
    sa.Column('date', sa.DateTime),
)

def upgrade():
    s = sql.select([ role.c.id ], role.c.name == 'administrator')
    results = op.get_bind().execute(s)
    if results:
        admin_role_id = list(results)[0][0]
        s = sql.select([ role_permission.c.id ], sql.and_(role_permission.c.role_id == admin_role_id, role_permission.c.permission_type == 'access_all_labs'))
        if len(list(op.get_bind().execute(s))) == 0:
            new_role_permission = role_permission.insert().values(role_id=admin_role_id, permission_type='access_all_labs', date=datetime.datetime.now(), permanent_id="administrator_role::access_all_labs")
            op.get_bind().execute(new_role_permission)


def downgrade():
    pass
