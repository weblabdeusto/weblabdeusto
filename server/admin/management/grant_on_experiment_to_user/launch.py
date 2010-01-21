#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2005-2009 University of Deusto
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#
# This software consists of contributions made by many individuals, 
# listed below:
#
# Author: Jaime Irurzun <jaime.irurzun@gmail.com>
#

import sys

try:
    from configuration import DATABASE_NAME, USER_LOGIN, EXPERIMENT_NAME, EXPERIMENT_CATEGORY, UPI_NAME, UPI_OWNER_ID, UPI_COMMENTS, OUTPUT_FILE
except Exception, e:
    print "File configuration.py not found. See configuration.py.dist. Error:", str(e)
    sys.exit(1)

if __name__ == "__main__":
    
    sql_insert = """
    START TRANSACTION;
    
    USE %(DATABASE_NAME)s;
    
    INSERT INTO wl_v_a_rw_UserPermissionInstance(
            upi_user_id,
            upi_user_permission_type_id,
            upi_owner_id,
            upi_date,
            upi_name,
            upi_comments
    )VALUES(
            GetUserIDByName('%(USER_LOGIN)s'),
            GetUserPermissionTypeID('experiment_allowed'),
            GetUserIDByName('%(UPI_OWNER_ID)s'),
            NOW(),
            '%(UPI_NAME)s',
            '%(UPI_COMMENTS)s'
    );

    UPDATE wl_v_a_rw_UserPermissionParameter
    SET upp_value = '%(EXPERIMENT_NAME)s'
    WHERE upp_id = GetUserPermissionParameterID(
            GetUserPermissionInstanceID(
                    GetUserIDByName('%(USER_LOGIN)s'),
                    '%(UPI_NAME)s'
            ),
            'experiment_allowed',
            'experiment_permanent_id'
    );

    UPDATE wl_v_a_rw_UserPermissionParameter
    SET upp_value = '%(EXPERIMENT_CATEGORY)s'
    WHERE upp_id = GetUserPermissionParameterID(
            GetUserPermissionInstanceID(
                    GetUserIDByName('%(USER_LOGIN)s'),
                    '%(UPI_NAME)s'
            ),
            'experiment_allowed',
            'experiment_category_id'
    );

    UPDATE wl_v_a_rw_UserPermissionParameter
    SET upp_value = '150'
    WHERE upp_id = GetUserPermissionParameterID(
            GetUserPermissionInstanceID(
                    GetUserIDByName('%(USER_LOGIN)s'),
                    '%(UPI_NAME)s'
            ),
            'experiment_allowed',
            'time_allowed'
    );
    
    COMMIT;
    """ % {"DATABASE_NAME": DATABASE_NAME,
           "USER_LOGIN": USER_LOGIN,
           "EXPERIMENT_NAME": EXPERIMENT_NAME,
           "EXPERIMENT_CATEGORY": EXPERIMENT_CATEGORY,
           "UPI_NAME": UPI_NAME,
           "UPI_OWNER_ID": UPI_OWNER_ID,
           "UPI_COMMENTS": UPI_COMMENTS}
    
    try:
        open('%s' % (OUTPUT_FILE), 'w').write(sql_insert)
        print "[ok] SQL file generated. Now insert it into MySQL ( mysql -uroot -p < %s )" % (OUTPUT_FILE)
    except Exception, e:
        print "[fail]", e
