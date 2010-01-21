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
    from configuration import *
except Exception, e:
    print "File configuration.py not found. See configuration.py.dist. Error:", str(e)
    sys.exit(1)
    
    
if __name__ == "__main__":
    
    sql_insert = """
    START TRANSACTION;
    
    USE %(DATABASE_NAME)s;
    
    INSERT INTO wl_v_a_rw_GroupPermissionInstance(
            gpi_group_id,
            gpi_group_permission_type_id,
            gpi_owner_id,
            gpi_date,
            gpi_name,
            gpi_comments
    )VALUES(
            GetGroupIDByName('%(GROUP_NAME)s'),
            GetGroupPermissionTypeID('experiment_allowed'),
            GetUserIDByName('%(GPI_OWNER_ID)s'),
            NOW(),
            '%(GPI_NAME)s',
            '%(GPI_COMMENTS)s'
    );

    UPDATE wl_v_a_rw_GroupPermissionParameter
    SET gpp_value = '%(EXPERIMENT_NAME)s'
    WHERE gpp_id = GetGroupPermissionParameterID(
            GetGroupPermissionInstanceID(
                    GetGroupIDByName('%(GROUP_NAME)s'),
                    '%(GPI_NAME)s'
            ),
            'experiment_allowed',
            'experiment_permanent_id'
    );

    UPDATE wl_v_a_rw_GroupPermissionParameter
    SET gpp_value = '%(EXPERIMENT_CATEGORY)s'
    WHERE gpp_id = GetGroupPermissionParameterID(
            GetGroupPermissionInstanceID(
                    GetGroupIDByName('%(GROUP_NAME)s'),
                    '%(GPI_NAME)s'
            ),
            'experiment_allowed',
            'experiment_category_id'
    );

    UPDATE wl_v_a_rw_GroupPermissionParameter
    SET gpp_value = '150'
    WHERE gpp_id = GetGroupPermissionParameterID(
            GetGroupPermissionInstanceID(
                    GetGroupIDByName('%(GROUP_NAME)s'),
                    '%(GPI_NAME)s'
            ),
            'experiment_allowed',
            'time_allowed'
    );
    
    COMMIT;
    """ % {"DATABASE_NAME":       DATABASE_NAME,
           "GROUP_NAME":          GROUP_NAME,
           "EXPERIMENT_NAME":     EXPERIMENT_NAME,
           "EXPERIMENT_CATEGORY": EXPERIMENT_CATEGORY,
           "GPI_NAME":            GPI_NAME,
           "GPI_OWNER_ID":        GPI_OWNER_ID,
           "GPI_COMMENTS":        GPI_COMMENTS}
    
    try:
        open('%s' % (OUTPUT_FILE), 'w').write(sql_insert)
        print "[ok] SQL file generated. Now insert it into MySQL ( mysql -uroot -p < %s )" % (OUTPUT_FILE)
    except Exception, e:
        print "[fail]", e

