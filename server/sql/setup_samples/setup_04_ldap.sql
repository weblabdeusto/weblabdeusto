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
	'studentLDAP1',
	'Name of student LDAP1',
	'weblab@deusto.es',
	NULL,
	NULL,
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
	'studentLDAP2',
	'Name of student LDAP2',
	'weblab@deusto.es',
	NULL,
	NULL,
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
	'studentLDAP3',
	'Name of student LDAP3',
	'weblab@deusto.es',
	NULL,
	NULL,
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
	'studentLDAPwithoutUserAuth',
	'Name of student LDAPwithoutUserAuth',
	'weblab@deusto.es',
	NULL,
	NULL,
	GetRoleID('student')
);

INSERT INTO wl_v_a_rw_UserAuthInstance(
	uai_user_auth_id,
	uai_name,
	uai_configuration
) VALUES (
	GetUserAuthID('LDAP'),
	'Configuration of CDK at Deusto',
	'domain=cdk.deusto.es;ldap_uri=ldaps://castor.cdk.deusto.es'
);

INSERT INTO wl_v_a_rw_UserAuthInstance(
	uai_user_auth_id,
	uai_name,
	uai_configuration
) VALUES (
	GetUserAuthID('LDAP'),
	'Configuration of DEUSTO at Deusto',
	'domain=deusto.es;ldap_uri=ldaps://altair.cdk.deusto.es'
);

INSERT INTO wl_v_a_rw_UserAuthUserRelation(
	uaur_user_id,
	uaur_user_auth_instance_id
) VALUES (
	GetUserIDByName('studentLDAP1'),
	GetUserAuthInstanceID('Configuration of CDK at Deusto')
);

INSERT INTO wl_v_a_rw_UserAuthUserRelation(
	uaur_user_id,
	uaur_user_auth_instance_id
) VALUES (
	GetUserIDByName('studentLDAP2'),
	GetUserAuthInstanceID('Configuration of CDK at Deusto')
);

INSERT INTO wl_v_a_rw_UserAuthUserRelation(
	uaur_user_id,
	uaur_user_auth_instance_id
) VALUES (
	GetUserIDByName('studentLDAP3'),
	GetUserAuthInstanceID('Configuration of DEUSTO at Deusto')
);


