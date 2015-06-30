from __future__ import print_function, unicode_literals
"""Add locale cache indexes

Revision ID: 4dd49c571575
Revises: 27fb5b742a71
Create Date: 2015-06-24 01:22:19.378277

"""

# revision identifiers, used by Alembic.
revision = '4dd49c571575'
down_revision = '27fb5b742a71'

from alembic import op


def upgrade():
    op.create_index('ix_LocationCache_ip', 'LocationCache', ['ip'])
    op.create_index('ix_LocationCache_lookup_time', 'LocationCache', ['lookup_time'])

def downgrade():
    pass
