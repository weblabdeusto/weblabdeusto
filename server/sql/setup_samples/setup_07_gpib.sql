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
	'student.gpib',
	'Name of student Gpib',
	'weblab@deusto.es',
-- password: aaaapassword in sha1
	'aaaa{sha}a776159c8c7ff8b73e43aa54d081979e72511474',
-- password: password in md5
	'5f4dcc3b5aa765d61d8327deb882cf99',
	GetRoleID('student')
);

INSERT INTO wl_v_a_rw_Group (
	group_name,
	group_owner_id
) VALUES (
	'class-of-gpib',
	GetUserIDByName('prof1')
);

INSERT INTO wl_v_a_rw_UserIsMemberOf (
	user_id,
	group_id
) VALUES ( 
	GetUserIDByName('student.gpib'),
	GetGroupIDByName('class-of-gpib')
);

INSERT INTO wl_v_a_rw_ExperimentCategory(
	experiment_category_name
) VALUES (
	'GPIB experiments'
);

INSERT INTO wl_v_a_rw_Experiment(
	experiment_owner_id,
	experiment_category_id,
	experiment_start_date,
	experiment_end_date,
	experiment_name
) VALUES (
	GetUserIDByName('prof1'),
	GetExperimentCategoryIDByName('GPIB experiments'),
	CURDATE(),
	ADDDATE(CURDATE(), INTERVAL 10 YEAR),
	'ud-gpib'
);

INSERT INTO wl_v_a_rw_UserPermissionInstance(
	upi_user_id,
	upi_user_permission_type_id,
	upi_owner_id,
	upi_date,
	upi_name,
	upi_comments
)VALUES(
	GetUserIDByName('student2'),
	GetUserPermissionTypeID('experiment_allowed'),
	GetUserIDByName('prof1'),
	NOW(),
	'student2::ud-gpib',
	'Permission for student2 to use WebLab-GPIB'
);

UPDATE wl_v_a_rw_UserPermissionParameter
SET upp_value = 'ud-gpib'
WHERE upp_id = GetUserPermissionParameterID(
	GetUserPermissionInstanceID(
		GetUserIDByName('student2'),
		'student2::ud-gpib'
	),
	'experiment_allowed',
	'experiment_permanent_id'
);

UPDATE wl_v_a_rw_UserPermissionParameter
SET upp_value = 'GPIB experiments'
WHERE upp_id = GetUserPermissionParameterID(
	GetUserPermissionInstanceID(
		GetUserIDByName('student2'),
		'student2::ud-gpib'
	),
	'experiment_allowed',
	'experiment_category_id'
);

UPDATE wl_v_a_rw_UserPermissionParameter
SET upp_value = '150'
WHERE upp_id = GetUserPermissionParameterID(
	GetUserPermissionInstanceID(
		GetUserIDByName('student2'),
		'student2::ud-gpib'
	),
	'experiment_allowed',
	'time_allowed'
);

INSERT INTO wl_v_a_rw_GroupPermissionInstance(
	gpi_group_id,
	gpi_group_permission_type_id,
	gpi_owner_id,
	gpi_date,
	gpi_name,
	gpi_comments
)VALUES(
	GetGroupIDByName('class-of-gpib'),
	GetGroupPermissionTypeID('experiment_allowed'),
	GetUserIDByName('prof1'),
	NOW(),
	'class-of-gpib::ud-gpib',
	'Permission for group class-of-gpib to use WebLab-GPIB'
);

UPDATE wl_v_a_rw_GroupPermissionParameter
SET gpp_value = 'ud-gpib'
WHERE gpp_id = GetGroupPermissionParameterID(
	GetGroupPermissionInstanceID(
		GetGroupIDByName('class-of-gpib'),
		'class-of-gpib::ud-gpib'
	),
	'experiment_allowed',
	'experiment_permanent_id'
);


UPDATE wl_v_a_rw_GroupPermissionParameter
SET gpp_value = 'GPIB experiments'
WHERE gpp_id = GetGroupPermissionParameterID(
	GetGroupPermissionInstanceID(
		GetGroupIDByName('class-of-gpib'),
		'class-of-gpib::ud-gpib'
	),
	'experiment_allowed',
	'experiment_category_id'
);


UPDATE wl_v_a_rw_GroupPermissionParameter
SET gpp_value = '100'
WHERE gpp_id = GetGroupPermissionParameterID(
	GetGroupPermissionInstanceID(
		GetGroupIDByName('class-of-gpib'),
		'class-of-gpib::ud-gpib'
	),
	'experiment_allowed',
	'time_allowed'
);


