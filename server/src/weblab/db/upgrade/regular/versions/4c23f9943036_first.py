"""First version

Revision ID: 4c23f9943036
Revises: None
Create Date: 2013-04-18 12:37:52.535777

Apply all the changes added since 3.9.0, if they were not already applied.
"""

# revision identifiers, used by Alembic.
revision = '4c23f9943036'
down_revision = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy.schema import MetaData


def upgrade():
    m = MetaData()
    m.reflect(op.get_bind())
    print m.tables
    pass


def downgrade():
    # TODO
    pass
