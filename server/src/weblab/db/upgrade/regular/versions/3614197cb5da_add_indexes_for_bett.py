from __future__ import print_function, unicode_literals
"""Add indexes for better admin panel performance

Revision ID: 3614197cb5da
Revises: 35756029a48a
Create Date: 2014-01-12 10:54:21.096200

"""

# revision identifiers, used by Alembic.
revision = '3614197cb5da'
down_revision = '35756029a48a'

from alembic import op


def upgrade():
    op.create_index('ix_User_full_name', 'User', ['full_name'])
    op.create_index('ix_User_email', 'User', ['email'])

    op.create_index('ix_UserUsedExperiment_start_date', 'UserUsedExperiment', ['start_date'])
    op.create_index('ix_UserUsedExperiment_end_date', 'UserUsedExperiment', ['end_date'])
    op.create_index('ix_UserUsedExperiuser_origin', 'UserUsedExperiment', ['origin'])
    op.create_index('ix_UserUsedExperiuser_coord_address', 'UserUsedExperiment', ['coord_address'])

    op.create_index('ix_UserFile_file_hash', 'UserFile', ['file_hash'])

    op.create_index('ix_UserPermission_permanent_id', 'UserPermission', ['permanent_id'])
    op.create_index('ix_GroupPermission_permanent_id', 'GroupPermission', ['permanent_id'])
    op.create_index('ix_RolePermission_permanent_id', 'RolePermission', ['permanent_id'])


def downgrade():
    op.drop_index('ix_User_full_name')
    op.drop_index('ix_User_email')

    op.drop_index('ix_UserUsedExperiment_start_date')
    op.drop_index('ix_UserUsedExperiment_end_date')
    op.drop_index('ix_UserUsedExperiuser_origin')
    op.drop_index('ix_UserUsedExperiuser_coord_address')

    op.drop_index('ix_UserFile_file_hash')

    op.drop_index('ix_UserPermission_permanent_id')
    op.drop_index('ix_GroupPermission_permanent_id')
    op.drop_index('ix_RolePermission_permanent_id')

