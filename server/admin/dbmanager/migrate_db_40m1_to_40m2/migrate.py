from migrationlib import Patch, PatchApplier

import weblab.db.Model as Model

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
                                AddingReservationIdToUserUsedExperiment, 
                                AddingReservationIdToEntityUsedExperiment
                            ])
    applier.execute()

