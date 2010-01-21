#!/usr/bin/env python
#-*-*- encoding: utf-8 -*-*-

import random
import sha
import md5
import sys

try:
    from configuration import DATABASE_NAME, USERNAME, USER_MAIL, USER_FULLNAME, USER_PASSWORD
except Exception, e:
    print "File configuration.py not found. See configuration.py.dist. Error:", str(e)
    sys.exit(1)

SQL_CODE ="""-- This file should be run under admin privileges

use %(database_name)s;

-- --------------------------------------------------------------------------------
-- ------------------             ADDING USER          ----------------------------
-- --------------------------------------------------------------------------------

INSERT INTO wl_v_a_rw_User (
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
    '%(shapassword)s',
    '%(md5password)s',
    GetRoleID('student')
);
"""
 
randomstuff = ""

for i in range(4):
    c = chr(ord('a') + random.randint(0,25))
    randomstuff += c

shapasswd = randomstuff + "{sha}" + sha.new(randomstuff + USER_PASSWORD).hexdigest()
md5passwd = md5.new(randomstuff + USER_PASSWORD).hexdigest()

sql_code = SQL_CODE % {
            'database_name'      : DATABASE_NAME,
            'login' : USERNAME,
            'full_name' : USER_FULLNAME,
            'email_account' : USER_MAIL,
            'md5password'   : md5passwd,
            'shapassword'   : shapasswd
        }

filename = 'output.%s.sql' % USERNAME

open(filename,'w').write(sql_code)

print "File %s successfully created. Now mysql -uUSERNAME -p < %s" % (filename,filename)

