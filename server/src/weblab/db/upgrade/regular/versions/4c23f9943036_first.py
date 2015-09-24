from __future__ import print_function, unicode_literals
"""First version

Revision ID: 4c23f9943036
Revises: None
Create Date: 2013-04-18 12:37:52.535777

Apply all the changes added since 3.9.0, if they were not already applied.
"""

# revision identifiers, used by Alembic.
revision = '4c23f9943036'
down_revision = None

# TODO: add here all the missing migrators from:
# ../admin/cli/migrate_db_40m1_to_50/migrate.py

####################################################################
# 
# Take into account that we are actively supporting SQLite. SQLite
# does not support operations such as ALTER TABLE Foo DROP COLUMN
# or so, so many methods, such as "op.drop_column", will not work, and
# a work arounds (locating all the data in a new table, drop the other
# and rename) will be required.
#


def add_priority_to_permission_parameter(m):
    pass

def add_initialization_in_accounting_to_permission_parameter(m):
    pass

def add_access_forward_to_permission(m):
    pass

def add_federation_role(m):
    pass

def add_access_forward_to_federated(m):
    pass

def add_admin_panel_to_administrators(m):
    pass

def add_reservation_id_to_user_used_experiment(m):
    pass

def add_finish_reason_to_user_experiment(m):
    pass

def add_max_error_in_millis_to_user_used_experiment(m):
    pass

def add_permission_id_to_user_used_experiment(m):
    pass

def remove_external_entity_from_permission_type(m):
    pass

def remove_applicable_permission_types(m):
#     if 'UserApplicablePermissionType' in m.tables:
#         op.add_column('UserPermission', 'permission_type_id', sa.Integer)
# 
#         results = op.execute(
#             op.tables['UserPermission'].
#         )
# 
#         op.drop_table('UserApplicablePermissionType')
    pass

def remove_external_entity_is_member_of(m):
    pass

def remove_external_entity_permission_parameter(m):
    pass

def remove_external_entity_permission(m):
    pass

def remove_external_entity_command(m):
    pass

def remove_external_entity_file(m):
    pass

def remove_external_entity_user_used_experiment(m):
    pass

def remove_external_entity_aplicable_permission_type(m):
    pass

def migrate_user_permissions(m):
    pass

def migrate_group_permissions(m):
    pass

def migrate_role_permissions(m):
    pass

def remove_permission_type_parameter(m):
    pass

def remove_permission_type(m):
    pass

def upgrade():
    # m = MetaData()
    # m.reflect(op.get_bind())
    pass
    # remove_applicable_permission_types(m)


def downgrade():
    # TODO
    pass
