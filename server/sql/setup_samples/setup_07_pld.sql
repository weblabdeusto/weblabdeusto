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

INSERT INTO wl_v_a_rw_Experiment(
	experiment_owner_id,
	experiment_category_id,
	experiment_start_date,
	experiment_end_date,
	experiment_name
) VALUES (
	GetUserIDByName('prof1'),
	GetExperimentCategoryIDByName('PLD experiments'),
	CURDATE(),
	ADDDATE(CURDATE(), INTERVAL 10 YEAR),
	'ud-pld'
);

INSERT INTO wl_v_a_rw_Experiment(
	experiment_owner_id,
	experiment_category_id,
	experiment_start_date,
	experiment_end_date,
	experiment_name
) VALUES (
	GetUserIDByName('prof1'),
	GetExperimentCategoryIDByName('PLD experiments'),
	CURDATE(),
	ADDDATE(CURDATE(), INTERVAL 10 YEAR),
	'ud-pld2'
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
	'student2::weblab-pld',
	'Permission for student2 to use WebLab-PLD'
);

UPDATE wl_v_a_rw_UserPermissionParameter
SET upp_value = 'ud-pld'
WHERE upp_id = GetUserPermissionParameterID(
	GetUserPermissionInstanceID(
		GetUserIDByName('student2'),
		'student2::weblab-pld'
	),
	'experiment_allowed',
	'experiment_permanent_id'
);

UPDATE wl_v_a_rw_UserPermissionParameter
SET upp_value = 'PLD experiments'
WHERE upp_id = GetUserPermissionParameterID(
	GetUserPermissionInstanceID(
		GetUserIDByName('student2'),
		'student2::weblab-pld'
	),
	'experiment_allowed',
	'experiment_category_id'
);

UPDATE wl_v_a_rw_UserPermissionParameter
SET upp_value = '100'
WHERE upp_id = GetUserPermissionParameterID(
	GetUserPermissionInstanceID(
		GetUserIDByName('student2'),
		'student2::weblab-pld'
	),
	'experiment_allowed',
	'time_allowed'
);


INSERT INTO wl_v_a_rw_UserPermissionInstance(
	upi_user_id,
	upi_user_permission_type_id,
	upi_owner_id,
	upi_date,
	upi_name,
	upi_comments
)VALUES(
	GetUserIDByName('student6'),
	GetUserPermissionTypeID('experiment_allowed'),
	GetUserIDByName('prof1'),
	NOW(),
	'student6::weblab-pld',
	'Permission for student6 to use WebLab-PLD'
);

UPDATE wl_v_a_rw_UserPermissionParameter
SET upp_value = 'ud-pld'
WHERE upp_id = GetUserPermissionParameterID(
	GetUserPermissionInstanceID(
		GetUserIDByName('student6'),
		'student6::weblab-pld'
	),
	'experiment_allowed',
	'experiment_permanent_id'
);

UPDATE wl_v_a_rw_UserPermissionParameter
SET upp_value = 'PLD experiments'
WHERE upp_id = GetUserPermissionParameterID(
	GetUserPermissionInstanceID(
		GetUserIDByName('student6'),
		'student6::weblab-pld'
	),
	'experiment_allowed',
	'experiment_category_id'
);

UPDATE wl_v_a_rw_UserPermissionParameter
SET upp_value = '140'
WHERE upp_id = GetUserPermissionParameterID(
	GetUserPermissionInstanceID(
		GetUserIDByName('student6'),
		'student6::weblab-pld'
	),
	'experiment_allowed',
	'time_allowed'
);


