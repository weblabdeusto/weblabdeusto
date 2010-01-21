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
-- -------------             ADDING A COUPLE OF GROUPS          -----------------------
-- ------------------------------------------------------------------------------------

-- Prof 1 and 2 will be member of group "professors1and2"

INSERT INTO wl_v_a_rw_Group (
	group_name,
	group_owner_id
) VALUES (
	'professors1and2',
	GetUserIDByName('admin1')
);

INSERT INTO wl_v_a_rw_UserIsMemberOf (
	user_id,
	group_id
) VALUES ( 
	GetUserIDByName('prof1'),
	GetGroupIDByName('professors1and2')
);

INSERT INTO wl_v_a_rw_UserIsMemberOf (
	user_id,
	group_id
) VALUES ( 
	GetUserIDByName('prof2'),
	GetGroupIDByName('professors1and2')
);

-- prof3 will be member of professor3

INSERT INTO wl_v_a_rw_Group (
	group_name,
	group_owner_id
) VALUES (
	'professor3',
	GetUserIDByName('admin1')
);

INSERT INTO wl_v_a_rw_UserIsMemberOf (
	user_id,
	group_id
) VALUES ( 
	GetUserIDByName('prof3'),
	GetGroupIDByName('professor3')
);

-- Groups professors1and2 and professor3 will be members of group:
-- 'groups_professors1and2_and_professor3'

INSERT INTO wl_v_a_rw_Group (
	group_name,
	group_owner_id
) VALUES (
	'groups_professors1and2_and_professor3',
	GetUserIDByName('admin1')
);

INSERT INTO wl_v_a_rw_GroupIsMemberOf (
	group_id,
	group_owner_id
) VALUES (
	GetGroupIDByName('professors1and2'),
	GetGroupIDByName('groups_professors1and2_and_professor3')
);

INSERT INTO wl_v_a_rw_GroupIsMemberOf (
	group_id,
	group_owner_id
) VALUES (
	GetGroupIDByName('professor3'),
	GetGroupIDByName('groups_professors1and2_and_professor3')
);

-- student1 and student2 are members of a new group "students"

INSERT INTO wl_v_a_rw_Group (
	group_name,
	group_owner_id
) VALUES (
	'5A',
	GetUserIDByName('prof1')
);

INSERT INTO wl_v_a_rw_UserIsMemberOf (
	user_id,
	group_id
) VALUES ( 
	GetUserIDByName('student1'),
	GetGroupIDByName('5A')
);

INSERT INTO wl_v_a_rw_UserIsMemberOf (
	user_id,
	group_id
) VALUES ( 
	GetUserIDByName('student2'),
	GetGroupIDByName('5A')
);

INSERT INTO wl_v_a_rw_UserIsMemberOf (
	user_id,
	group_id
) VALUES ( 
	GetUserIDByName('student3'),
	GetGroupIDByName('5A')
);

INSERT INTO wl_v_a_rw_UserIsMemberOf (
	user_id,
	group_id
) VALUES ( 
	GetUserIDByName('student4'),
	GetGroupIDByName('5A')
);

INSERT INTO wl_v_a_rw_UserIsMemberOf (
	user_id,
	group_id
) VALUES ( 
	GetUserIDByName('student5'),
	GetGroupIDByName('5A')
);

INSERT INTO wl_v_a_rw_UserIsMemberOf (
	user_id,
	group_id
) VALUES ( 
	GetUserIDByName('student6'),
	GetGroupIDByName('5A')
);


