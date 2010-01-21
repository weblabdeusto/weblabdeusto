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

-- ------------------------------------------------------------------------------------
-- ----------------             ADDING ADMINISTRATORS          ------------------------
-- ------------------------------------------------------------------------------------

INSERT INTO wl_User (
	user_login,
	user_full_name,
	user_email,
	user_password,
	web_password,
	user_role_id
) VALUES (
	'admin1',
	'Name of administrator 1',
	'weblab@deusto.es',
-- password: aaaapassword in sha1
	'aaaa{sha}a776159c8c7ff8b73e43aa54d081979e72511474',
-- password: password in md5
	'5f4dcc3b5aa765d61d8327deb882cf99',
	GetAdministratorID()
);

INSERT INTO wl_User (
	user_login,
	user_full_name,
	user_email,
	user_password,
	web_password,
	user_role_id
) VALUES (
	'admin2',
	'Name of administrator 2',
	'weblab@deusto.es',
-- password: aaaapassword in sha1
	'aaaa{sha}a776159c8c7ff8b73e43aa54d081979e72511474',
-- password: password in md5
	'5f4dcc3b5aa765d61d8327deb882cf99',
	GetAdministratorID()
);

-- We add 3 permission types, with 4 parameters each
CALL AddUserPermissionType(3,4);

-- We add 3 permission types, with 4 parameters each
CALL AddGroupPermissionType(3,4);

-- We add 3 permission types, with 4 parameters each
CALL AddExternalEntityPermissionType(3,4);

-- -----------------------------------------------------------------------------------
-- --------------------             ADDING USERS          ----------------------------
-- -----------------------------------------------------------------------------------

INSERT INTO wl_v_a_rw_User (
	user_login,
	user_full_name,
	user_email,
	user_password,
	web_password,
	user_role_id
) VALUES (
	'admin3',
	'Name of administrator 3',
	'weblab@deusto.es',
-- password: aaaapassword in sha1
	'aaaa{sha}a776159c8c7ff8b73e43aa54d081979e72511474',
-- password: password in md5
	'5f4dcc3b5aa765d61d8327deb882cf99',
	GetRoleID('administrator')
);

INSERT INTO wl_v_a_rw_User (
	user_login,
	user_full_name,
	user_email,
	user_password,
	web_password,
	user_role_id
) VALUES (
	'prof1',
	'Name of professor 1',
	'weblab@deusto.es',
-- password: aaaapassword in sha1
	'aaaa{sha}a776159c8c7ff8b73e43aa54d081979e72511474',
-- password: password in md5
	'5f4dcc3b5aa765d61d8327deb882cf99',
	GetRoleID('professor')
);

INSERT INTO wl_v_a_rw_User (
	user_login,
	user_full_name,
	user_email,
	user_password,
	web_password,
	user_role_id
) VALUES (
	'prof2',
	'Name of professor 2',
	'weblab@deusto.es',
-- password: aaaapassword in sha1
	'aaaa{sha}a776159c8c7ff8b73e43aa54d081979e72511474',
-- password: password in md5
	'5f4dcc3b5aa765d61d8327deb882cf99',
	GetRoleID('professor')
);

INSERT INTO wl_v_a_rw_User (
	user_login,
	user_full_name,
	user_email,
	user_password,
	web_password,
	user_role_id
) VALUES (
	'prof3',
	'Name of professor 3',
	'weblab@deusto.es',
-- password: aaaapassword in sha1
	'aaaa{sha}a776159c8c7ff8b73e43aa54d081979e72511474',
-- password: password in md5
	'5f4dcc3b5aa765d61d8327deb882cf99',
	GetRoleID('professor')
);


