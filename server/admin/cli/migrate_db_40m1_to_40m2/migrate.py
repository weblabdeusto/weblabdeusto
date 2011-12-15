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
        ee_applicable_permission    = Model.DbExternalEntityApplicablePermissionType()

        session.add(user_applicable_permission)
        session.add(group_applicable_permission)
        session.add(role_applicable_permission)
        session.add(ee_applicable_permission)

        permission_type = Model.DbPermissionType('access_forward',"Users with this permission will be allowed to forward reservations to other external users.", user_applicable_permission, role_applicable_permission, group_applicable_permission, ee_applicable_permission)
        session.add(permission_type)

class AddingReservationIdToUserUsedExperiment(Patch):

    table_name = 'UserUsedExperiment'

    def check(self, cursor):
        return cursor.execute("DESC %s reservation_id" % self.table_name) == 0

    def apply(self, cursor):
        cursor.execute("ALTER TABLE %s ADD COLUMN reservation_id CHAR(50)" % self.table_name)

class AddingReservationIdToEntityUsedExperiment(AddingReservationIdToUserUsedExperiment):
    
    table_name = 'ExternalEntityUsedExperiment'


if __name__ == '__main__':
    applier = PatchApplier("weblab", "weblab", "WebLabTests", [
                                AddingPriorityToPermissionParameterPatch, 
                                AddingInitializationInAccountingToPermissionParameterPatch,
                                AddingAccessForwardToPermissionsPatch,
                                AddingReservationIdToUserUsedExperiment, 
                                AddingReservationIdToEntityUsedExperiment
                            ])
    applier.execute()

