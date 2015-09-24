from __future__ import print_function, unicode_literals
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

    def get_parameter(self, name):
        for parameter in self.parameters:
            if parameter.name == name:
                return parameter

class PermissionTypeParameter(object):
    def __init__(self, name, datatype, description):
        self.name        = name
        self.datatype    = datatype
        self.description = description


permission_types = {}
PERMISSION_TYPES = permission_types

def _register(permission_type):
    permission_types[permission_type.name] = permission_type

#############################################################
# 
#                Experiment allowed
# 
EXPERIMENT_ALLOWED = u'experiment_allowed'
EXPERIMENT_ALLOWED_DESC = u"Users with this permission will be able to use a particular laboratory during an amount of time. The amount of time will contain or not the initialization time."

EXPERIMENT_PERMANENT_ID            = u'experiment_permanent_id'
EXPERIMENT_PERMANENT_ID_DTYPE      = u'string'
EXPERIMENT_PERMANENT_ID_DESC       = u'the unique name of the experiment'

EXPERIMENT_CATEGORY_ID             = u'experiment_category_id'
EXPERIMENT_CATEGORY_ID_DTYPE       = u'string'
EXPERIMENT_CATEGORY_ID_DESC        = u'the unique name of the category of experiment'

TIME_ALLOWED                       = u'time_allowed'
TIME_ALLOWED_DTYPE                 = u'float'
TIME_ALLOWED_DESC                  = u'Time allowed (in seconds)'

PRIORITY                           = u'priority'
PRIORITY_DTYPE                     = u'int'
PRIORITY_DESC                      = u'Priority (the lower value the higher priority)'

INITIALIZATION_IN_ACCOUNTING       = u'initialization_in_accounting'
INITIALIZATION_IN_ACCOUNTING_DTYPE = u'bool'
INITIALIZATION_IN_ACCOUNTING_DESC  = u'time_allowed, should count with the initialization time or not?'

experiment_allowed = PermissionType(EXPERIMENT_ALLOWED, EXPERIMENT_ALLOWED_DESC, 
                                    [ PermissionTypeParameter(EXPERIMENT_PERMANENT_ID,      EXPERIMENT_PERMANENT_ID_DTYPE,      EXPERIMENT_PERMANENT_ID_DESC      ),
                                      PermissionTypeParameter(EXPERIMENT_CATEGORY_ID,       EXPERIMENT_CATEGORY_ID_DTYPE,       EXPERIMENT_CATEGORY_ID_DESC       ),
                                      PermissionTypeParameter(TIME_ALLOWED,                 TIME_ALLOWED_DTYPE,                 TIME_ALLOWED_DESC                 ),
                                      PermissionTypeParameter(PRIORITY,                     PRIORITY_DTYPE,                     PRIORITY_DESC                     ),
                                      PermissionTypeParameter(INITIALIZATION_IN_ACCOUNTING, INITIALIZATION_IN_ACCOUNTING_DTYPE, INITIALIZATION_IN_ACCOUNTING_DESC ) ])

_register(experiment_allowed)

#############################################################
# 
#                Admin panel access
# 


ADMIN_PANEL_ACCESS      = u'admin_panel_access'
ADMIN_PANEL_ACCESS_DESC = u"Users with this permission will be allowed to access the administration panel. The only parameter determines if the user has full_privileges to use the admin panel."

FULL_PRIVILEGES       = u'full_privileges'
FULL_PRIVILEGES_DTYPE = u'bool'
FULL_PRIVILEGES_DESC  = u'full privileges (True) or not (False)'

admin_panel_access = PermissionType(ADMIN_PANEL_ACCESS, ADMIN_PANEL_ACCESS_DESC, 
                                    [ PermissionTypeParameter(FULL_PRIVILEGES,      FULL_PRIVILEGES_DTYPE,      FULL_PRIVILEGES_DESC ) ])

_register(admin_panel_access)

#############################################################
# 
#                Access forward
# 


ACCESS_FORWARD      = u'access_forward'
ACCESS_FORWARD_DESC = u"Users with this permission will be allowed to forward reservations to other external users."

access_forward = PermissionType(ACCESS_FORWARD, ACCESS_FORWARD_DESC, [] )

_register(access_forward)

###############################################################
# 
#             Profile editing disabled
# 

CANT_CHANGE_PROFILE      = u'profile_editing_disabled'
CANT_CHANGE_PROFILE_DESC = u"Disable profile editing. Useful for demo accounts, for instance"

cant_change_profile = PermissionType(CANT_CHANGE_PROFILE, CANT_CHANGE_PROFILE_DESC, [])

_register(cant_change_profile)

###############################################################
# 
#             Access all labs
# 

ACCESS_ALL_LABS = u'access_all_labs'
ACCESS_ALL_LABS_DESC = u"Enable access to all labs, with a fixed amount of time and super-low priority"

access_all_labs = PermissionType(ACCESS_ALL_LABS, ACCESS_ALL_LABS_DESC, [])

_register(access_all_labs)


###############################################################
# 
#            Instrutor is a teacher of a group
# 

INSTRUCTOR_OF_GROUP      = u'instructor_of_group'
INSTRUCTOR_OF_GROUP_DESC = u'Users with this permission will see these groups'

TARGET_GROUP       = u'target_group'
TARGET_GROUP_DTYPE = u'int'
TARGET_GROUP_DESC  = u'Identifier of the group to be instructed.'

instructor_of_group = PermissionType(INSTRUCTOR_OF_GROUP, INSTRUCTOR_OF_GROUP_DESC, 
                                                    [ PermissionTypeParameter(TARGET_GROUP, TARGET_GROUP_DTYPE, TARGET_GROUP_DESC) ])

_register(instructor_of_group)

