#!/usr/bin/env python
#-*-*- encoding: utf-8 -*-*-

import StringIO
import sys

from DbManager import DbManager

try:
    from configuration import GROUP_NAME, GROUP_OWNER, EXPERIMENT_NAME_ID, EXPERIMENT_ID, EXPERIMENT_NAME, EXPERIMENT_TYPE, EXPERIMENT_TIME, DATABASE_NAME, AUTH_INSTANCE_ID
except Exception, e:
    print "File configuration.py not found. See configuration.py.dist. Error:", str(e)
    sys.exit(1)

USE_DATABASE_TEMPLATE = """-- This file should be run under admin privileges

use %(database_name)s;

-----------------------------------------------------------------------------------
--------------------             ADDING USERS          ----------------------------
-----------------------------------------------------------------------------------


"""

INSERT_USER_TEMPLATE = """INSERT INTO wl_v_a_rw_User (
    user_login,
    user_full_name,
    user_email,
    user_password,
    web_password,
    user_role_id
) VALUES (
    '%(login)s',
    '%(full_name)s',
    '%(email_account)s',
    NULL,
    NULL,
    GetRoleID('student')
);
"""

REMOVE_USER_PASSWORD_TEMPLATE = """UPDATE wl_v_a_rw_User
SET user_password=null, web_password=null
WHERE user_login='%(login)s';
"""

INSERT_LDAP_TEMPLATE = """INSERT INTO wl_v_a_rw_UserAuthUserRelation(
    uaur_user_id,
    uaur_user_auth_instance_id
) VALUES (
    GetUserIDByName('%(login)s'),
    GetUserAuthInstanceID('%(auth_instance_id)s')
);
"""

INSERT_GROUP_TEMPLATE="""
------------------------------------------------------------------------------------
-------------             ADDIN TO GROUP          -----------------------
------------------------------------------------------------------------------------

INSERT INTO wl_v_a_rw_Group (
    group_name,
    group_owner_id
) VALUES (
    '%(group_name)s',
    GetUserIDByName('%(group_owner)s')
);


"""

ADD_USER_TO_GROUP_TEMPLATE = """INSERT INTO wl_v_a_rw_UserIsMemberOf (
    user_id,
    group_id
) VALUES ( 
    GetUserIDByName('%(username)s'),
    GetGroupIDByName('%(group_name)s')
);

"""

ADD_PERMISSION_TO_GROUP_TEMPLATE = """---------------------------------------------------------------------------------------------------
----------------             ADDING PERMISSIONS ON EXPERIMENTS          ---------------------------
---------------------------------------------------------------------------------------------------

INSERT INTO wl_v_a_rw_GroupPermissionInstance(
    gpi_group_id,
    gpi_group_permission_type_id,
    gpi_owner_id,
    gpi_date,
    gpi_name,
    gpi_comments
)VALUES(
    GetGroupIDByName('%(group_name)s'),
    GetGroupPermissionTypeID('experiment_allowed'),
    GetUserIDByName('%(group_owner)s'),
    NOW(),
    '%(group_name)s::%(experiment_id)s',
    'Permission for group %(group_name)s to use %(experiment_name)s'
);

UPDATE wl_v_a_rw_GroupPermissionParameter
SET gpp_value = '%(experiment_name_id)s'
WHERE gpp_id = GetGroupPermissionParameterID(
    GetGroupPermissionInstanceID(
        GetGroupIDByName('%(group_name)s'),
        '%(group_name)s::%(experiment_id)s'
    ),
    'experiment_allowed',
    'experiment_permanent_id'
);

UPDATE wl_v_a_rw_GroupPermissionParameter
SET gpp_value = '%(experiment_type)s'
WHERE gpp_id = GetGroupPermissionParameterID(
    GetGroupPermissionInstanceID(
        GetGroupIDByName('%(group_name)s'),
        '%(group_name)s::%(experiment_id)s'
    ),
    'experiment_allowed',
    'experiment_category_id'
);


UPDATE wl_v_a_rw_GroupPermissionParameter
SET gpp_value = '%(experiment_time)s'
WHERE gpp_id = GetGroupPermissionParameterID(
    GetGroupPermissionInstanceID(
        GetGroupIDByName('%(group_name)s'),
        '%(group_name)s::%(experiment_id)s'
    ),
    'experiment_allowed',
    'time_allowed'
);

"""
 
def generate_sql_code(users):
    keys = {
        'group_name'         : GROUP_NAME,
        'group_owner'        : GROUP_OWNER,
        'experiment_id'      : EXPERIMENT_ID,
        'experiment_type'    : EXPERIMENT_TYPE,
        'experiment_time'    : EXPERIMENT_TIME,
        'experiment_name'    : EXPERIMENT_NAME,
        'experiment_name_id' : EXPERIMENT_NAME_ID,
        'database_name'      : DATABASE_NAME,
        'auth_instance_id'   : AUTH_INSTANCE_ID,

        'username'           : '%(username)s',
        'login'              : '%(login)s',
        'full_name'          : '%(full_name)s',
        'email_account'      : '%(email_account)s'
    }


    f = StringIO.StringIO()

    f.write(USE_DATABASE_TEMPLATE % keys)
    
    for user in users:
        if user.exists:         
            f.write(
                (REMOVE_USER_PASSWORD_TEMPLATE % keys) % {
                    'login' : user.login
                }
            )            
            print "has_auth?:",
            print user.has_auth
            if not user.has_auth:
                f.write(
                    (INSERT_LDAP_TEMPLATE % keys) % {
                        'login' : user.login
                    }
                )
        else:
            f.write(
                (INSERT_USER_TEMPLATE % keys) % {
                    'login' : user.login,
                    'full_name' : user.full_name,
                    'email_account' : user.email
                }
            )   

    db = DbManager()
    if not db.group_exists(GROUP_NAME):
        f.write(INSERT_GROUP_TEMPLATE % keys)

    # TODO: Check if the user is already a member of the group
    for user in users:
        f.write(
            (ADD_USER_TO_GROUP_TEMPLATE % keys) % {
            'username' : user.login
            }
        )

    f.write(ADD_PERMISSION_TO_GROUP_TEMPLATE % keys)
    return f.getvalue()