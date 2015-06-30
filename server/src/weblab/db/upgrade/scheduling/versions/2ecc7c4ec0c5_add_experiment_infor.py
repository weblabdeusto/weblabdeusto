from __future__ import print_function, unicode_literals
"""Add experiment information

Revision ID: 2ecc7c4ec0c5
Revises: None
Create Date: 2013-04-21 19:16:09.441855

"""

# revision identifiers, used by Alembic.
revision = '2ecc7c4ec0c5'
down_revision = None

from alembic import op
import sqlalchemy as sa

import weblab.core.coordinator.sql.priority_queue_scheduler_model as pq_model

def upgrade():
    op.add_column(pq_model.ConcreteCurrentReservation.__tablename__, sa.Column('exp_info', sa.Text))


def downgrade():
    op.drop_column(pq_model.ConcreteCurrentReservation.__tablename__, sa.Column('exp_info', sa.Text))
