"""Add is_admin

Revision ID: 45d111e2f59a
Revises: 2d16d7104dd6
Create Date: 2015-02-09 15:40:45.643486

"""

# revision identifiers, used by Alembic.
revision = '45d111e2f59a'
down_revision = '2d16d7104dd6'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('users', sa.Column('is_admin', sa.Boolean(), server_default='0', nullable=True))


def downgrade():
    op.drop_column('users', 'is_admin')
