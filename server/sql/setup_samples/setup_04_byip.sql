--
-- Copyright (C) 2005-2009 University of Deusto
-- All rights reserved.
--
-- This software is licensed as described in the file COPYING, which
-- you should have received as part of this distribution.
--
-- This software consists of contributions made by many individuals, 
-- listed below:
--
-- Author: Pablo Orduña <pablo@ordunya.com>
-- 

use WebLab;

INSERT INTO wl_v_a_rw_User (
	user_login,
	user_full_name,
	user_email,
	user_password,
	web_password,
	user_role_id
) VALUES (
	'student.byip',
	'Name of student by IP',
	'weblab@deusto.es',
-- password: aaaapassword in sha1
	'aaaa{sha}a776159c8c7ff8b73e43aa54d081979e72511474',
-- password: password in md5
	'5f4dcc3b5aa765d61d8327deb882cf99',
	GetRoleID('student')
);

INSERT INTO wl_v_a_rw_UserAuthInstance(
	uai_user_auth_id,
	uai_name,
	uai_configuration
) VALUES (
	GetUserAuthID('TRUSTED-IP-ADDRESSES'),
	'trusting in localhost',
	'127.0.0.1'
);

INSERT INTO wl_v_a_rw_UserAuthUserRelation(
	uaur_user_id,
	uaur_user_auth_instance_id
) VALUES (
	GetUserIDByName('student.byip'),
	GetUserAuthInstanceID('trusting in localhost')
);

