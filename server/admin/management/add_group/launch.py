#!/usr/bin/env python
#-*-*- encoding: utf-8 -*-*-

import sys

try:
    from configuration import DATABASE_NAME, GROUP_OWNER_ID, GROUP_NAME, USERS
except Exception, e:
    print "File configuration.py not found. See configuration.py.dist. Error:", str(e)
    sys.exit(1)

sql_code ="""-- This file should be run under admin privileges

use %(DATABASE_NAME)s;

-- --------------------------------------------------------------------------------
-- -----------------             ADDING GROUP          ----------------------------
-- --------------------------------------------------------------------------------

START TRANSACTION;

INSERT INTO wl_v_a_rw_Group (
    group_name,
    group_owner_id
) VALUES (
    '%(GROUP_NAME)s',
    GetUserIDByName('%(GROUP_OWNER_ID)s')
);

""" % {
            'DATABASE_NAME'      : DATABASE_NAME,
            'GROUP_NAME'         : GROUP_NAME,
            'GROUP_OWNER_ID'     : GROUP_OWNER_ID
        }

for user in USERS:
    sql_code += """
    INSERT INTO wl_v_a_rw_UserIsMemberOf( user_id, group_id )
    VALUES (GetUserIDByName('%(USER_LOGIN)s'), GetGroupIDByName('%(GROUP_NAME)s'));
    
    """ % {
        'USER_LOGIN' : user,
        'GROUP_NAME' : GROUP_NAME
    }

sql_code += """

COMMIT;
"""

filename = 'output.%s.sql' % GROUP_NAME

open(filename,'w').write(sql_code)

print "File %s successfully created. Now mysql -uUSERNAME -p < %s" % (filename,filename)

