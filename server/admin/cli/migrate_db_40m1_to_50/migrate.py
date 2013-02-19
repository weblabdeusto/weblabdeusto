import datetime
from migrationlib import Patch, PatchApplier

import weblab.db.model as Model
import weblab.permissions as permissions

class AddingPriorityToPermissionParameterPatch(Patch):

    APPLY_FORMAT = Patch.SQLALCHEMY_FORMAT

    def check(self, cursor):
        # Check if the 'experiment_allowed' permission type has the 'priority' parameter
        if cursor.execute("SHOW TABLES LIKE 'PermissionType'") == 0:
            return False

        return cursor.execute("SELECT PermissionType.id FROM PermissionType, PermissionTypeParameter WHERE PermissionType.name = 'experiment_allowed' AND  PermissionType.id = PermissionTypeParameter.permission_type_id AND PermissionTypeParameter.name = 'priority'") == 0

    def apply(self, session):
        # TODO: pass this to SQL
        experiment_allowed = session.query(Model.DbPermissionType).filter_by(name = 'experiment_allowed').first()
        parameter = Model.DbPermissionTypeParameter(permission_type = experiment_allowed, name = 'priority' , datatype = 'int', description = 'Priority (the lower value the higher priority)')
        session.add(parameter)

class AddingInitializationInAccountingToPermissionParameterPatch(Patch):

    APPLY_FORMAT = Patch.SQLALCHEMY_FORMAT

    def check(self, cursor):
        # Check if the 'experiment_allowed' permission type has the 'initialization_in_accounting' parameter
        if cursor.execute("SHOW TABLES LIKE 'PermissionType'") == 0:
            return False

        return cursor.execute("SELECT PermissionType.id FROM PermissionType, PermissionTypeParameter WHERE PermissionType.name = 'experiment_allowed' AND  PermissionType.id = PermissionTypeParameter.permission_type_id AND PermissionTypeParameter.name = 'initialization_in_accounting'") == 0

    def apply(self, session):
        # TODO: pass this to SQL
        experiment_allowed = session.query(Model.DbPermissionType).filter_by(name = 'experiment_allowed').first()
        parameter = Model.DbPermissionTypeParameter(permission_type = experiment_allowed, name = 'initialization_in_accounting' , datatype = 'bool', description = 'time_allowed, should count with the initialization time or not?')
        session.add(parameter)

class AddingAccessForwardToPermissionsPatch(Patch):

    APPLY_FORMAT = Patch.SQLALCHEMY_FORMAT

    def check(self, cursor):
        # Check if the 'experiment_allowed' permission type has the 'initialization_in_accounting' parameter
        if cursor.execute("SHOW TABLES LIKE 'PermissionType'") == 0:
            return False

        return cursor.execute("SELECT PermissionType.id FROM PermissionType WHERE PermissionType.name = 'access_forward'") == 0

    def apply(self, session):
        # TODO: pass this to SQL
        permission_type = Model.DbPermissionType('access_forward',"Users with this permission will be allowed to forward reservations to other external users.")
        session.add(permission_type)


class AddingFederationRole(Patch):

    CHECK_FORMAT = Patch.SQLALCHEMY_FORMAT
    APPLY_FORMAT = Patch.SQLALCHEMY_FORMAT

    def check(self, session):
        return session.query(Model.DbRole).filter_by(name = 'federated').first() is None

    def apply(self, session):
        federated = Model.DbRole("federated")
        session.add(federated)


class AddingAccessForwardToFederatedPatch(Patch):

    APPLY_FORMAT = Patch.SQLALCHEMY_FORMAT

    def check(self, cursor):
        return cursor.execute("SELECT id FROM RolePermission WHERE permanent_id = 'federated_role::access_forward'") == 0

    def apply(self, session):
        # TODO: pass this to SQL
        federated = session.query(Model.DbRole).filter_by(name='federated').one()

        federated_access_forward = Model.DbRolePermission(
            federated,
            permissions.ACCESS_FORWARD,
            "federated_role::access_forward",
            datetime.datetime.utcnow(),
            "Access to forward external accesses to all users with role 'federated'"
        )
        session.add(federated_access_forward)

class AddingAdminPanelToAdministratorsPatch(Patch):

    APPLY_FORMAT = Patch.SQLALCHEMY_FORMAT

    def check(self, cursor):
        return cursor.execute("SELECT id FROM RolePermission WHERE permanent_id = 'administrator_role::admin_panel_access'") == 0

    def apply(self, session):
        # TODO: pass this to SQL
        administrator = session.query(Model.DbRole).filter_by(name='administrator').one()

        administrator_admin_panel_access = Model.DbRolePermission(
            administrator,
            permissions.ADMIN_PANEL_ACCESS,
            "administrator_role::admin_panel_access",
            datetime.datetime.utcnow(),
            "Access to the admin panel for administrator role with full_privileges"
        )
        session.add(administrator_admin_panel_access)
        administrator_admin_panel_access_p1 = Model.DbRolePermissionParameter(administrator_admin_panel_access, permissions.FULL_PRIVILEGES, True)
        session.add(administrator_admin_panel_access_p1)


class AddingReservationIdToUserUsedExperiment(Patch):

    table_name = 'UserUsedExperiment'

    def check(self, cursor):
        return cursor.execute("DESC %s reservation_id" % self.table_name) == 0

    def apply(self, cursor):
        cursor.execute("ALTER TABLE %s ADD COLUMN reservation_id CHAR(50)" % self.table_name)

class AddingFinishReasonToUserUsedExperiment(Patch):

    table_name = 'UserUsedExperiment'

    def check(self, cursor):
        return cursor.execute("DESC %s finish_reason" % self.table_name) == 0

    def apply(self, cursor):
        cursor.execute("ALTER TABLE %s ADD COLUMN finish_reason Integer" % self.table_name)

class AddingMaxErrorInMillisToUserUsedExperiment(Patch):

    table_name = 'UserUsedExperiment'

    def check(self, cursor):
        return cursor.execute("DESC %s max_error_in_millis" % self.table_name) == 0

    def apply(self, cursor):
        cursor.execute("ALTER TABLE %s ADD COLUMN max_error_in_millis Integer" % self.table_name)

class AddingPermissionIdToUserUsedExperiment(Patch):

    table_name = 'UserUsedExperiment'

    def check(self, cursor):
        return cursor.execute("DESC %s permission_permanent_id" % self.table_name) == 0

    def apply(self, cursor):
        cursor.execute("ALTER TABLE %s ADD COLUMN permission_permanent_id Integer" % self.table_name)

class RemoveExternalEntityFromPermissionType(Patch):

    table_name = 'PermissionType'

    def check(self, cursor):
        if cursor.execute("SHOW TABLES LIKE 'PermissionType'") == 0:
            return False
 
        return cursor.execute("DESC %s ee_applicable_id" % self.table_name) == 1

    def apply(self, cursor):
        cursor.execute("ALTER TABLE %s DROP FOREIGN KEY PermissionType_ibfk_4" % self.table_name)
        cursor.execute("ALTER TABLE %s DROP COLUMN ee_applicable_id" % self.table_name)


class RemoveTable(Patch):

    ABSTRACT = True

    def check(self, cursor):
        return cursor.execute("SHOW TABLES LIKE '%s'" % self.table_name) != 0

    def apply(self, cursor):
        cursor.execute("DROP TABLE %s" % self.table_name)


class RemoveApplicablePermissionType(RemoveTable):

    ABSTRACT = True

    def apply(self, cursor):
        # 
        # First, create a direct reference from UserPermission to PermissionType
        # 
        cursor.execute("ALTER TABLE %sPermission ADD COLUMN permission_type_id Integer" % self.level)

        # Populate that column with the proper indexes.
        cursor.execute("SELECT %(level)sPermission.id, PermissionType.id FROM %(level)sPermission, PermissionType WHERE %(level)sPermission.applicable_permission_type_id = PermissionType.%(level_low)s_applicable_id" % {'level' : self.level, 'level_low' : self.level.lower() })
        for level_permission_id, permission_type_id in cursor.fetchall():
            cursor.execute("UPDATE " + self.level + "Permission SET permission_type_id = %s WHERE id = %s", (permission_type_id, level_permission_id))

        # Then, drop the old applicable_permission_type_id column from UserPermission
        cursor.execute("ALTER TABLE %(level)sPermission DROP FOREIGN KEY %(level)sPermission_ibfk_2" % {'level' : self.level})
        cursor.execute("ALTER TABLE %(level)sPermission DROP COLUMN applicable_permission_type_id" % {'level' : self.level})

        # Then, make that column not nullable and make it a foreign key
        cursor.execute("ALTER TABLE %sPermission MODIFY COLUMN permission_type_id Integer NOT NULL" % self.level)
        cursor.execute("ALTER TABLE %sPermission ADD CONSTRAINT %sPermission_ibfk_2 FOREIGN KEY (`permission_type_id`) REFERENCES `PermissionType` (`id`)" % (self.level, self.level))

        # Then, drop the references from PermissionType to UserApplicablePermissionType 
        cursor.execute("ALTER TABLE PermissionType DROP FOREIGN KEY %s" % self.key)
        cursor.execute("ALTER TABLE PermissionType DROP COLUMN %s_applicable_id" % self.level.lower())

        # And finally, drop the table
        cursor.execute("DROP TABLE %s" % self.table_name)

class RemoveUserApplicablePermissionType(RemoveApplicablePermissionType):
    
    ABSTRACT = False
    level = 'User'
    key = 'PermissionType_ibfk_1'
    table_name = 'UserApplicablePermissionType'

class RemoveRoleApplicablePermissionType(RemoveApplicablePermissionType):
    
    ABSTRACT = False
    level = 'Role'
    key = 'PermissionType_ibfk_2'
    table_name = 'RoleApplicablePermissionType'

class RemoveGroupApplicablePermissionType(RemoveApplicablePermissionType):
    
    ABSTRACT = False
    level = 'Group'
    key = 'PermissionType_ibfk_3'
    table_name = 'GroupApplicablePermissionType'


class RemoveTable_ExternalEntityIsMemberOf(RemoveTable):
    ABSTRACT = False
    table_name = 'ExternalEntityIsMemberOf'

class RemoveTable_ExternalEntityPermissionParameter(RemoveTable):
    ABSTRACT = False
    table_name = 'ExternalEntityPermissionParameter'

class RemoveTable_ExternalEntityPermission(RemoveTable):
    ABSTRACT = False
    table_name = 'ExternalEntityPermission'

class RemoveTable_ExternalEntityCommand(RemoveTable):
    ABSTRACT = False
    table_name = 'ExternalEntityCommand'

class RemoveTable_ExternalEntityFile(RemoveTable):
    ABSTRACT = False
    table_name = 'ExternalEntityFile'

class RemoveTable_ExternalEntityUsedExperiment(RemoveTable):
    ABSTRACT = False
    table_name = 'ExternalEntityUsedExperiment'

class RemoveTable_ExternalEntity(RemoveTable):
    ABSTRACT = False
    table_name = 'ExternalEntity'

class RemoveTable_ExternalEntityApplicablePermissionType(RemoveTable):
    ABSTRACT = False
    table_name = 'ExternalEntityApplicablePermissionType'

class Migrate_Permissions(Patch):

    ABSTRACT = True

    def check(self, cursor):
        return cursor.execute("DESC %sPermission permission_type_id" % self.level) != 0

    def apply(self, cursor):
        # 
        # First, create a 
        # 
        cursor.execute("ALTER TABLE %sPermission ADD COLUMN permission_type VARCHAR(255)" % self.level)

        # Populate that column with the proper names
        cursor.execute("SELECT %(level)sPermission.id, PermissionType.name FROM %(level)sPermission, PermissionType WHERE %(level)sPermission.permission_type_id = PermissionType.id" % {'level' : self.level })
        for level_permission_id, permission_type_name in cursor.fetchall():
            cursor.execute("UPDATE " + self.level + "Permission SET permission_type = %s WHERE id = %s", (permission_type_name, level_permission_id))
 
        # Then, drop the permission_type_id
        cursor.execute("ALTER TABLE %(level)sPermission DROP FOREIGN KEY %(level)sPermission_ibfk_2" % {'level' : self.level})
        cursor.execute("ALTER TABLE %(level)sPermission DROP COLUMN permission_type_id" % {'level' : self.level})

        cursor.execute("CREATE INDEX ix_%(level)sPermission_permission_type ON %(level)sPermission(permission_type)" % {'level' : self.level})

        # Then, make that column not nullable
        cursor.execute("ALTER TABLE %sPermission MODIFY COLUMN permission_type VARCHAR(255) NOT NULL" % self.level)

class UserMigrate_Permissions(Migrate_Permissions):
    ABSTRACT = False
    level = 'User'

class GroupMigrate_Permissions(Migrate_Permissions):
    ABSTRACT = False
    level = 'Group'

class RoleMigrate_Permissions(Migrate_Permissions):
    ABSTRACT = False
    level = 'Role'

class Migrate_PermissionParameters(Patch):

    ABSTRACT = True

    def check(self, cursor):
        return cursor.execute("DESC %sPermissionParameter permission_type_parameter_id" % self.level) != 0

    def apply(self, cursor):
        # 
        # First, create a 
        # 
        cursor.execute("ALTER TABLE %sPermissionParameter ADD COLUMN permission_type_parameter VARCHAR(255)" % self.level)

        # Populate that column with the proper names
        cursor.execute("SELECT %(level)sPermissionParameter.id, PermissionTypeParameter.name FROM %(level)sPermissionParameter, PermissionTypeParameter WHERE %(level)sPermissionParameter.permission_type_parameter_id = PermissionTypeParameter.id" % {'level' : self.level })
        for level_permission_parameter_id, permission_type_parameter_name in cursor.fetchall():
            cursor.execute("UPDATE " + self.level + "PermissionParameter SET permission_type_parameter = %s WHERE id = %s", (permission_type_parameter_name, level_permission_parameter_id))
 
        # Then, drop the permission_type_id
        cursor.execute("ALTER TABLE %(level)sPermissionParameter DROP FOREIGN KEY %(level)sPermissionParameter_ibfk_1" % {'level' : self.level})
        cursor.execute("ALTER TABLE %(level)sPermissionParameter DROP FOREIGN KEY %(level)sPermissionParameter_ibfk_2" % {'level' : self.level})
        cursor.execute("ALTER TABLE %(level)sPermissionParameter DROP INDEX permission_id" % {'level' : self.level})
        cursor.execute("ALTER TABLE %(level)sPermissionParameter DROP COLUMN permission_type_parameter_id" % {'level' : self.level})

        cursor.execute("ALTER TABLE %(level)sPermissionParameter ADD CONSTRAINT %(level)sPermissionParameter_ibfk_1 FOREIGN KEY (`permission_id`) REFERENCES `%(level)sPermission` (`id`)" % {'level' : self.level})
        cursor.execute("CREATE INDEX ix_%(level)sPermissionParameter_permission_type_parameter ON %(level)sPermissionParameter(permission_type_parameter)" % {'level' : self.level})

        # Then, make that column not nullable
        cursor.execute("ALTER TABLE %sPermissionParameter MODIFY COLUMN permission_type_parameter VARCHAR(255) NOT NULL" % self.level)

class UserMigrate_PermissionParameters(Migrate_PermissionParameters):
    ABSTRACT = False
    level = 'User'

class GroupMigrate_PermissionParameters(Migrate_PermissionParameters):
    ABSTRACT = False
    level = 'Group'

class RoleMigrate_PermissionParameters(Migrate_PermissionParameters):
    ABSTRACT = False
    level = 'Role'

class RemoveTable_PermissionTypeParameter(RemoveTable):
    ABSTRACT = False
    table_name = 'PermissionTypeParameter'

class RemoveTable_PermissionType(RemoveTable):
    ABSTRACT = False
    table_name = 'PermissionType'

if __name__ == '__main__':
    dbs = ["WebLabTests", "WebLabTests2", "WebLabTests3"]
    # dbs = ["WebLabTests"]
    applier = PatchApplier("weblab", "weblab", dbs, [
                                RemoveUserApplicablePermissionType,
                                RemoveRoleApplicablePermissionType,
                                RemoveGroupApplicablePermissionType,

                                AddingPriorityToPermissionParameterPatch, 
                                AddingInitializationInAccountingToPermissionParameterPatch,
                                AddingAccessForwardToPermissionsPatch,
                                AddingReservationIdToUserUsedExperiment,
                                AddingFederationRole,
                                AddingAdminPanelToAdministratorsPatch,
                                AddingAccessForwardToFederatedPatch,
                                AddingFinishReasonToUserUsedExperiment,
                                AddingMaxErrorInMillisToUserUsedExperiment,
                                AddingPermissionIdToUserUsedExperiment,

                                RemoveExternalEntityFromPermissionType,
                                RemoveTable_ExternalEntityIsMemberOf,
                                RemoveTable_ExternalEntityPermissionParameter,
                                RemoveTable_ExternalEntityPermission,
                                RemoveTable_ExternalEntityCommand,
                                RemoveTable_ExternalEntityFile,
                                RemoveTable_ExternalEntityUsedExperiment,
                                RemoveTable_ExternalEntity,
                                RemoveTable_ExternalEntityApplicablePermissionType,

                                UserMigrate_Permissions,
                                RoleMigrate_Permissions,
                                GroupMigrate_Permissions,

                                UserMigrate_PermissionParameters,
                                RoleMigrate_PermissionParameters,
                                GroupMigrate_PermissionParameters,

                                RemoveTable_PermissionTypeParameter,
                                RemoveTable_PermissionType,
                            ])
    applier.execute()

