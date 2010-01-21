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
	'student1',
	'Name of student 1',
	'weblab@deusto.es',
-- password: aaaapassword in sha1
	'aaaa{sha}a776159c8c7ff8b73e43aa54d081979e72511474',
-- password: password in md5
	'5f4dcc3b5aa765d61d8327deb882cf99',
	GetRoleID('student')
);

INSERT INTO wl_v_a_rw_User (
	user_login,
	user_full_name,
	user_email,
	user_password,
	web_password,
	user_role_id
) VALUES (
	'student2',
	'Name of student 2',
	'weblab@deusto.es',
-- password: aaaapassword in sha1
	'aaaa{sha}a776159c8c7ff8b73e43aa54d081979e72511474',
-- password: password in md5
	'5f4dcc3b5aa765d61d8327deb882cf99',
	GetRoleID('student')
);

INSERT INTO wl_v_a_rw_User (
	user_login,
	user_full_name,
	user_email,
	user_password,
	web_password,
	user_role_id
) VALUES (
	'student3',
	'Name of student 3',
	'weblab@deusto.es',
-- password: aaaapassword in sha1
	'aaaa{sha}a776159c8c7ff8b73e43aa54d081979e72511474',
-- password: password in md5
	'5f4dcc3b5aa765d61d8327deb882cf99',
	GetRoleID('student')
);

INSERT INTO wl_v_a_rw_User (
	user_login,
	user_full_name,
	user_email,
	user_password,
	web_password,
	user_role_id
) VALUES (
	'student4',
	'Name of student 4',
	'weblab@deusto.es',
-- password: aaaapassword in sha1
	'aaaa{sha}a776159c8c7ff8b73e43aa54d081979e72511474',
-- password: password in md5
	'5f4dcc3b5aa765d61d8327deb882cf99',
	GetRoleID('student')
);

INSERT INTO wl_v_a_rw_User (
	user_login,
	user_full_name,
	user_email,
	user_password,
	web_password,
	user_role_id
) VALUES (
	'student5',
	'Name of student 5',
	'weblab@deusto.es',
-- password: aaaapassword in sha1
	'aaaa{sha}a776159c8c7ff8b73e43aa54d081979e72511474',
-- password: password in md5
	'5f4dcc3b5aa765d61d8327deb882cf99',
	GetRoleID('student')
);

INSERT INTO wl_v_a_rw_User (
	user_login,
	user_full_name,
	user_email,
	user_password,
	web_password,
	user_role_id
) VALUES (
	'student6',
	'Name of student 6',
	'weblab@deusto.es',
-- password: aaaapassword in sha1
	'aaaa{sha}a776159c8c7ff8b73e43aa54d081979e72511474',
-- password: password in md5
	'5f4dcc3b5aa765d61d8327deb882cf99',
	GetRoleID('student')
);

INSERT INTO wl_v_a_rw_User (
	user_login,
	user_full_name,
	user_email,
	user_password,
	web_password,
	user_role_id
) VALUES (
	'student7',
	'Name of student 7',
	'weblab@deusto.es',
	'aaaa{thishashdoesnotexist}a776159c8c7ff8b73e43aa54d081979e72511474',
	'5f4dcc3b5aa765d61d8327deb882cf99',
	GetRoleID('student')
);

INSERT INTO wl_v_a_rw_User (
	user_login,
	user_full_name,
	user_email,
	user_password,
	web_password,
	user_role_id
) VALUES (
	'student8',
	'Name of student 8',
	'weblab@deusto.es',
	'this.format.is.not.valid.for.the.password',
	'',
	GetRoleID('student')
);

