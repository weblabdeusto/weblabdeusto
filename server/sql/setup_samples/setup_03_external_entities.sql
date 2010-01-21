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
-- --------------             ADDING EXTERNAL ENTITIES          -----------------------
-- ------------------------------------------------------------------------------------

INSERT INTO wl_v_a_rw_ExternalEntity (
	external_entity_name,
	external_entity_country,
	external_entity_description,
	external_entity_password,
	external_entity_public_key
) VALUES (
	'external1',
	'Spain',
	'This is External Entity #1',
-- password: aaaapassword in sha1
	'aaaa{sha}a776159c8c7ff8b73e43aa54d081979e72511474',
	'BLABLABLA'
);

INSERT INTO wl_v_a_rw_ExternalEntity (
	external_entity_name,
	external_entity_country,
	external_entity_description,
	external_entity_password,
	external_entity_public_key
) VALUES (
	'external2',
	'Spain',
	'This is External Entity #2',
-- password: aaaapassword in sha1
	'aaaa{sha}a776159c8c7ff8b73e43aa54d081979e72511474',
	'BLABLABLA'
);


