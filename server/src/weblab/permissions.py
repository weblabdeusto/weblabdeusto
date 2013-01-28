"""
This module includes all the possible permissions. Whenever the application is upgraded,
it can include new permissions, and no change in the database is required (except for granting
groups, roles or users with the new permission).
"""

class PermissionType(object):
    def __init__(self, name, description, parameters):
        self.name        = name
        self.description = description
        self.parameters  = parameters

class PermissionTypeParameter(object):
    def __init__(self, name, datatype, description):
        self.name        = name
        self.datatype    = datatype
        self.description = description


permission_types = {}
PERMISSION_TYPES = permission_types

#############################################################
# 
#                Experiment allowed
# 
EXPERIMENT_ALLOWED = 'experiment_allowed'
EXPERIMENT_ALLOWED_DESC = "This type has a parameter which is the permanent ID (not a INT) of an Experiment. Users which have this permission will have access to the experiment defined in this parameter"

EXPERIMENT_PERMANENT_ID            = 'experiment_permanent_id'
EXPERIMENT_PERMANENT_ID_DTYPE      = 'string'
EXPERIMENT_PERMANENT_ID_DESC       = 'the unique name of the experiment'

EXPERIMENT_CATEGORY_ID             = 'experiment_category_id'
EXPERIMENT_CATEGORY_ID_DTYPE       = 'string'
EXPERIMENT_CATEGORY_ID_DESC        = 'the unique name of the category of experiment'

TIME_ALLOWED                       = 'time_allowed'
TIME_ALLOWED_DTYPE                 = 'float'
TIME_ALLOWED_DESC                  = 'Time allowed (in seconds)'

PRIORITY                           = 'priority'
PRIORITY_DTYPE                     = 'int'
PRIORITY_DESC                      = 'Priority (the lower value the higher priority)'

INITIALIZATION_IN_ACCOUNTING       = 'initialization_in_accounting'
INITIALIZATION_IN_ACCOUNTING_DTYPE = 'bool'
INITIALIZATION_IN_ACCOUNTING_DESC  = 'time_allowed, should count with the initialization time or not?'

experiment_allowed = PermissionType(EXPERIMENT_ALLOWED, EXPERIMENT_ALLOWED_DESC, 
                                    [ PermissionTypeParameter(EXPERIMENT_PERMANENT_ID,      EXPERIMENT_PERMANENT_ID_DTYPE,      EXPERIMENT_PERMANENT_ID_DESC      ),
                                      PermissionTypeParameter(EXPERIMENT_CATEGORY_ID,       EXPERIMENT_CATEGORY_ID_DTYPE,       EXPERIMENT_CATEGORY_ID_DESC       ),
                                      PermissionTypeParameter(TIME_ALLOWED,                 TIME_ALLOWED_DTYPE,                 TIME_ALLOWED_DESC                 ),
                                      PermissionTypeParameter(PRIORITY,                     PRIORITY_DTYPE,                     PRIORITY_DESC                     ),
                                      PermissionTypeParameter(INITIALIZATION_IN_ACCOUNTING, INITIALIZATION_IN_ACCOUNTING_DTYPE, INITIALIZATION_IN_ACCOUNTING_DESC ) ])

permission_types[experiment_allowed.name] = experiment_allowed

#############################################################
# 
#                Admin panel access
# 


ADMIN_PANEL_ACCESS      = 'admin_panel_access'
ADMIN_PANEL_ACCESS_DESC = "Users with this permission will be allowed to access the administration panel. The only parameter determines if the user has full_privileges to use the admin panel."

FULL_PRIVILEGES       = 'full_privileges'
FULL_PRIVILEGES_DTYPE = 'bool'
FULL_PRIVILEGES_DESC  = 'full privileges (True) or not (False)'

admin_panel_access = PermissionType(ADMIN_PANEL_ACCESS, ADMIN_PANEL_ACCESS_DESC, 
                                    [ PermissionTypeParameter(FULL_PRIVILEGES,      FULL_PRIVILEGES_DTYPE,      FULL_PRIVILEGES_DESC ) ])

permission_types[admin_panel_access.name] = admin_panel_access

#############################################################
# 
#                Access forward
# 


ACCESS_FORWARD      = 'access_forward'
ACCESS_FORWARD_DESC = "Users with this permission will be allowed to forward reservations to other external users."

access_forward = PermissionType(ACCESS_FORWARD, ACCESS_FORWARD_DESC, [] )

permission_types[access_forward.name] = access_forward


