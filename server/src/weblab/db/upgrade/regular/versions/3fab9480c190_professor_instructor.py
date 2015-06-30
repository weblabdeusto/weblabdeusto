from __future__ import print_function, unicode_literals
"""professor => instructor

Revision ID: 3fab9480c190
Revises: 31ded1f6ad6
Create Date: 2014-02-17 00:56:12.566690

"""

# revision identifiers, used by Alembic.
revision = '3fab9480c190'
down_revision = '31ded1f6ad6'

from alembic import op
import sqlalchemy as sa

metadata = sa.MetaData()
role = sa.Table('Role', metadata,
    sa.Column('id', sa.Integer()),
    sa.Column('name', sa.String(20)),
)


def upgrade():
    update_stmt = role.update().where(role.c.name == 'professor').values(name = 'instructor')
    op.execute(update_stmt)

def downgrade():
    update_stmt = role.update().where(role.c.name == 'instructor').values(name = 'professor')
    op.execute(update_stmt)

