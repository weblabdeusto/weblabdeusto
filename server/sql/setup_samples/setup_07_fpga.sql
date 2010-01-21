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

INSERT INTO wl_v_a_rw_ExperimentCategory(
	experiment_category_name
) VALUES (
	'FPGA experiments'
);

INSERT INTO wl_v_a_rw_Experiment(
	experiment_owner_id,
	experiment_category_id,
	experiment_start_date,
	experiment_end_date,
	experiment_name
) VALUES (
	GetUserIDByName('prof1'),
	GetExperimentCategoryIDByName('FPGA experiments'),
	CURDATE(),
	ADDDATE(CURDATE(), INTERVAL 10 YEAR),
	'ud-fpga'
);

INSERT INTO wl_v_a_rw_GroupPermissionInstance(
	gpi_group_id,
	gpi_group_permission_type_id,
	gpi_owner_id,
	gpi_date,
	gpi_name,
	gpi_comments
)VALUES(
	GetGroupIDByName('5A'),
	GetGroupPermissionTypeID('experiment_allowed'),
	GetUserIDByName('prof1'),
	NOW(),
	'5A::weblab-fpga',
	'Permission for group 5A to use WebLab-FPGA'
);

UPDATE wl_v_a_rw_GroupPermissionParameter
SET gpp_value = 'ud-fpga'
WHERE gpp_id = GetGroupPermissionParameterID(
	GetGroupPermissionInstanceID(
		GetGroupIDByName('5A'),
		'5A::weblab-fpga'
	),
	'experiment_allowed',
	'experiment_permanent_id'
);

UPDATE wl_v_a_rw_GroupPermissionParameter
SET gpp_value = 'FPGA experiments'
WHERE gpp_id = GetGroupPermissionParameterID(
	GetGroupPermissionInstanceID(
		GetGroupIDByName('5A'),
		'5A::weblab-fpga'
	),
	'experiment_allowed',
	'experiment_category_id'
);


UPDATE wl_v_a_rw_GroupPermissionParameter
SET gpp_value = '30'
WHERE gpp_id = GetGroupPermissionParameterID(
	GetGroupPermissionInstanceID(
		GetGroupIDByName('5A'),
		'5A::weblab-fpga'
	),
	'experiment_allowed',
	'time_allowed'
);

