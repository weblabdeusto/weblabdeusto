import datetime
from migrationlib import Patch, PatchApplier

import weblab.db.model as Model

class AddingPriorityToPermissionParameterPatch(Patch):

    CHECK_FORMAT = Patch.SQLALCHEMY_FORMAT
    APPLY_FORMAT = Patch.SQLALCHEMY_FORMAT

    def check(self, session):
        # Check if the 'experiment_allowed' permission type has the 'priority' parameter
        return len([ parameter 
                    for parameter in session.query(Model.DbPermissionType).filter_by(name = 'experiment_allowed').first().parameters
                    if parameter.name == 'priority']) == 0

    def apply(self, session):
        experiment_allowed = session.query(Model.DbPermissionType).filter_by(name = 'experiment_allowed').first()
        parameter = Model.DbPermissionTypeParameter(permission_type = experiment_allowed, name = 'priority' , datatype = 'int', description = 'Priority (the lower value the higher priority)')
        session.add(parameter)

class AddingInitializationInAccountingToPermissionParameterPatch(Patch):

    CHECK_FORMAT = Patch.SQLALCHEMY_FORMAT
    APPLY_FORMAT = Patch.SQLALCHEMY_FORMAT

    def check(self, session):
        # Check if the 'experiment_allowed' permission type has the 'initialization_in_accounting' parameter
        return len([ parameter 
                    for parameter in session.query(Model.DbPermissionType).filter_by(name = 'experiment_allowed').first().parameters
                    if parameter.name == 'initialization_in_accounting']) == 0

    def apply(self, session):
        experiment_allowed = session.query(Model.DbPermissionType).filter_by(name = 'experiment_allowed').first()
        parameter = Model.DbPermissionTypeParameter(permission_type = experiment_allowed, name = 'initialization_in_accounting' , datatype = 'bool', description = 'time_allowed, should count with the initialization time or not?')
        session.add(parameter)

class AddingAccessForwardToPermissionsPatch(Patch):

    CHECK_FORMAT = Patch.SQLALCHEMY_FORMAT
    APPLY_FORMAT = Patch.SQLALCHEMY_FORMAT

    def check(self, session):
        # Check if the 'experiment_allowed' permission type has the 'initialization_in_accounting' parameter
        return session.query(Model.DbPermissionType).filter_by(name = 'access_forward').first() is None

    def apply(self, session):
        
        user_applicable_permission  = Model.DbUserApplicablePermissionType()
        group_applicable_permission = Model.DbGroupApplicablePermissionType()
        role_applicable_permission  = Model.DbRoleApplicablePermissionType()

        session.add(user_applicable_permission)
        session.add(group_applicable_permission)
        session.add(role_applicable_permission)

        permission_type = Model.DbPermissionType('access_forward',"Users with this permission will be allowed to forward reservations to other external users.", user_applicable_permission, role_applicable_permission, group_applicable_permission, ee_applicable_permission)
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

    CHECK_FORMAT = Patch.SQLALCHEMY_FORMAT
    APPLY_FORMAT = Patch.SQLALCHEMY_FORMAT

    def check(self, session):
        return session.query(Model.DbRolePermission).filter_by(permanent_id = 'federated_role::access_forward').first() is None

    def apply(self, session):
        federated = session.query(Model.DbRole).filter_by(name='federated').one()

        access_forward = session.query(Model.DbPermissionType).filter_by(name="access_forward").one()
        role_applicable_permission  = Model.DbRoleApplicablePermissionType()
        access_forward.role_applicable = role_applicable_permission

        federated_access_forward = Model.DbRolePermission(
            federated,
            access_forward.role_applicable,
            "federated_role::access_forward",
            datetime.datetime.utcnow(),
            "Access to forward external accesses to all users with role 'federated'"
        )
        session.add(federated_access_forward)

class AddingAdminPanelToAdministratorsPatch(Patch):

    CHECK_FORMAT = Patch.SQLALCHEMY_FORMAT
    APPLY_FORMAT = Patch.SQLALCHEMY_FORMAT

    def check(self, session):
        return session.query(Model.DbRolePermission).filter_by(permanent_id = 'administrator_role::admin_panel_access').first() is None

    def apply(self, session):
        administrator = session.query(Model.DbRole).filter_by(name='administrator').one()

        admin_panel_access = session.query(Model.DbPermissionType).filter_by(name="admin_panel_access").one()
        admin_panel_access_p1 = [ p for p in admin_panel_access.parameters if p.name == "full_privileges" ][0]

        role_applicable_permission  = Model.DbRoleApplicablePermissionType()
        admin_panel_access.role_applicable = role_applicable_permission

        administrator_admin_panel_access = Model.DbRolePermission(
            administrator,
            admin_panel_access.role_applicable,
            "administrator_role::admin_panel_access",
            datetime.datetime.utcnow(),
            "Access to the admin panel for administrator role with full_privileges"
        )
        session.add(administrator_admin_panel_access)
        administrator_admin_panel_access_p1 = Model.DbRolePermissionParameter(administrator_admin_panel_access, admin_panel_access_p1, True)
        session.add(administrator_admin_panel_access_p1)


class AddingReservationIdToUserUsedExperiment(Patch):

    table_name = 'UserUsedExperiment'

    def check(self, cursor):
        return cursor.execute("DESC %s reservation_id" % self.table_name) == 0

    def apply(self, cursor):
        cursor.execute("ALTER TABLE %s ADD COLUMN reservation_id CHAR(50)" % self.table_name)

class RemoveExternalEntityFromPermissionType(Patch):

    table_name = 'PermissionType'

    def check(self, cursor):
        return cursor.execute("DESC %s ee_applicable_id" % self.table_name) == 1

    def apply(self, cursor):
        cursor.execute("ALTER TABLE %s DROP FOREIGN KEY PermissionType_ibfk_4" % self.table_name)
        cursor.execute("ALTER TABLE %s DROP COLUMN ee_applicable_id" % self.table_name)


class RemoveTable(Patch):

    ABSTRACT = True

    def check(self, cursor):
        try:
            return cursor.execute("DESC %s" % self.table_name) != 0
        except Exception as e:
            if 'exist' in str(e):
                return False
            raise

    def apply(self, cursor):
        cursor.execute("DROP TABLE %s" % self.table_name)

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


if __name__ == '__main__':
    applier = PatchApplier("weblab", "weblab", "WebLabTests", [
                                AddingPriorityToPermissionParameterPatch, 
                                AddingInitializationInAccountingToPermissionParameterPatch,
                                AddingAccessForwardToPermissionsPatch,
                                AddingReservationIdToUserUsedExperiment,
                                AddingFederationRole,
                                AddingAdminPanelToAdministratorsPatch,
                                AddingAccessForwardToFederatedPatch,
                                RemoveExternalEntityFromPermissionType,
                                RemoveTable_ExternalEntityIsMemberOf,
                                RemoveTable_ExternalEntityPermissionParameter,
                                RemoveTable_ExternalEntityPermission,
                                RemoveTable_ExternalEntityCommand,
                                RemoveTable_ExternalEntityFile,
                                RemoveTable_ExternalEntityUsedExperiment,
                                RemoveTable_ExternalEntity,
                                RemoveTable_ExternalEntityApplicablePermissionType,
                            ])
    applier.execute()

