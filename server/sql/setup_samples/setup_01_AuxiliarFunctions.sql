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
-- ------------------             AUXILIAR FUNCTIONS          -------------------------
-- ------------------------------------------------------------------------------------

-- These functions will be used along the different tests

DELIMITER $

CREATE FUNCTION GetAdministratorID()
RETURNS INT
READS SQL DATA
BEGIN
	DECLARE variable INT;
	SELECT role_id INTO variable 
		FROM wl_Role WHERE role_name = 'administrator';
	RETURN variable;
END$

CREATE FUNCTION GetUserPermissionIDByName(name VARCHAR(255))
RETURNS INT
READS SQL DATA
BEGIN
	DECLARE variable INT;
	SELECT upt_id INTO variable
		FROM wl_UserPermissionType WHERE upt_name = name;
	RETURN variable;
END$

CREATE FUNCTION GetUserPermissionParameterTypeIDByName(permission_name VARCHAR(255), parameter_name VARCHAR(255))
RETURNS INT
READS SQL DATA
BEGIN
	DECLARE variable INT;
	SELECT uppt_id INTO variable
		FROM wl_UserPermissionParameterType, wl_UserPermissionType
		WHERE uppt_name = parameter_name AND uppt_user_permission_type_id = upt_id AND upt_name = permission_name;
	RETURN variable;
END$

CREATE FUNCTION GetUserPermissionInstanceID(user_id INT, name VARCHAR(255))
RETURNS INT
READS SQL DATA
BEGIN
	DECLARE variable INT;
	SELECT upi_id INTO variable
		FROM wl_UserPermissionInstance 
		WHERE upi_name = name AND upi_user_id = user_id;
	RETURN variable;
END$

CREATE FUNCTION GetUserPermissionParameterID(permission_instance_id INT, permission_name VARCHAR(255), parameter_name VARCHAR(255))
RETURNS INT
READS SQL DATA
BEGIN
	DECLARE variable INT;
	SELECT upp_id INTO variable
		FROM wl_UserPermissionParameter 
		WHERE upp_user_permission_instance_id = permission_instance_id AND upp_user_permission_param_id = GetUserPermissionParameterTypeIDByName(permission_name,parameter_name);
	RETURN variable;
END$

CREATE FUNCTION GetGroupPermissionIDByName(name VARCHAR(255))
RETURNS INT
READS SQL DATA
BEGIN
	DECLARE variable INT;
	SELECT gpt_id INTO variable
		FROM wl_GroupPermissionType WHERE gpt_name = name;
	RETURN variable;
END$

CREATE FUNCTION GetGroupPermissionParameterTypeIDByName(permission_name VARCHAR(255), parameter_name VARCHAR(255))
RETURNS INT
READS SQL DATA
BEGIN
	DECLARE variable INT;
	SELECT gppt_id INTO variable
		FROM wl_GroupPermissionParameterType, wl_GroupPermissionType
		WHERE gppt_name = parameter_name AND gppt_group_permission_type_id = gpt_id AND gpt_name = permission_name;
	RETURN variable;
END$

CREATE FUNCTION GetGroupPermissionInstanceID(Group_id INT, name VARCHAR(255))
RETURNS INT
READS SQL DATA
BEGIN
	DECLARE variable INT;
	SELECT gpi_id INTO variable
		FROM wl_GroupPermissionInstance 
		WHERE gpi_name = name AND gpi_group_id = group_id;
	RETURN variable;
END$

CREATE FUNCTION GetGroupPermissionParameterID(permission_instance_id INT, permission_name VARCHAR(255), parameter_name VARCHAR(255))
RETURNS INT
READS SQL DATA
BEGIN
	DECLARE variable INT;
	SELECT gpp_id INTO variable
		FROM wl_GroupPermissionParameter 
		WHERE gpp_group_permission_instance_id = permission_instance_id AND gpp_group_permission_param_id = GetGroupPermissionParameterTypeIDByName(permission_name,parameter_name);
	RETURN variable;
END$

CREATE FUNCTION GetExternalEntityPermissionIDByName(name VARCHAR(255))
RETURNS INT
READS SQL DATA
BEGIN
	DECLARE variable INT;
	SELECT eept_id INTO variable
		FROM wl_ExternalEntityPermissionType WHERE eept_name = name;
	RETURN variable;
END$

CREATE FUNCTION GetUserAuthID(name VARCHAR(20))
RETURNS INT
READS SQL DATA
BEGIN
	DECLARE variable INT;
	SELECT user_auth_id INTO variable 
		FROM wl_UserAuth WHERE auth_name = name;
	RETURN variable;
END$

CREATE FUNCTION GetUserAuthInstanceID(par_name TEXT)
RETURNS INT
READS SQL DATA
BEGIN
	DECLARE variable INT;
	SELECT user_auth_instance_id INTO variable 
		FROM wl_UserAuthInstance WHERE uai_name = par_name;
	RETURN variable;
END$

CREATE FUNCTION GetRoleID(name VARCHAR(20))
RETURNS INT
READS SQL DATA
BEGIN
	DECLARE variable INT;
	SELECT role_id INTO variable 
		FROM wl_Role WHERE role_name = name;
	RETURN variable;
END$

CREATE FUNCTION GetUserIDByName(name VARCHAR(32))
RETURNS INT
READS SQL DATA
BEGIN
	DECLARE variable INT;
	SELECT user_id INTO variable
		FROM wl_User WHERE user_login = name;
	RETURN variable;
END$

CREATE FUNCTION GetGroupIDByName(name VARCHAR(255))
RETURNS INT
READS SQL DATA
BEGIN
	DECLARE variable INT;
	SELECT group_id INTO variable
		FROM wl_Group WHERE group_name = name;
	RETURN variable;
END$

CREATE FUNCTION GetExperimentCategoryIDByName(name VARCHAR(255))
RETURNS INT
READS SQL DATA
BEGIN
	DECLARE variable INT;
	SELECT experiment_category_id INTO variable
		FROM wl_ExperimentCategory WHERE experiment_category_name = name;
	RETURN variable;
END$

CREATE FUNCTION GetExperimentIDByName(name VARCHAR(255), category_name VARCHAR(255))
RETURNS INT
READS SQL DATA
BEGIN
	DECLARE variable INT;
	SELECT experiment_id INTO variable
		FROM wl_Experiment WHERE experiment_name = name 
		AND experiment_category_id = GetExperimentCategoryIDByName(category_name);
	RETURN variable;
END$

DELIMITER ;

-- ------------------------------------------------------------------------------------
-- ------------             ADDING USER PERMISSION TYPES          --------------------
-- ------------------------------------------------------------------------------------

DELIMITER $

CREATE PROCEDURE AddUserPermissionType(permission_number INT, number_of_parameters INT)
BEGIN
	DECLARE i INT DEFAULT 0;
	DECLARE j INT;
	WHILE i < permission_number DO
		INSERT INTO wl_UserPermissionType(
			upt_name,
			upt_description
		) VALUES (
			CONCAT('permission',i),
			CONCAT('description of permission',i)
		);
		SET j = 0;
		WHILE j < number_of_parameters DO
			INSERT INTO wl_UserPermissionParameterType(
				uppt_name,
				uppt_type,
				uppt_description,
				uppt_user_permission_type_id
			) VALUES (
				CONCAT('parameter',j),
				CONCAT('type of parameter',j),
				CONCAT('description of parameter',j,' of permission',i),
				GetUserPermissionIDByName(CONCAT('permission',i))
			);
			SET j = j + 1;
		END WHILE;
		SET i = i + 1;
	END WHILE;
END$

DELIMITER ;

-- ------------------------------------------------------------------------------------
-- ------------             ADDING GROUP PERMISSION TYPES          --------------------
-- ------------------------------------------------------------------------------------

DELIMITER $

CREATE PROCEDURE AddGroupPermissionType(permission_number INT, number_of_parameters INT)
BEGIN
	DECLARE i INT DEFAULT 0;
	DECLARE j INT;
	WHILE i < permission_number DO
		INSERT INTO wl_GroupPermissionType(
			gpt_name,
			gpt_description
		) VALUES (
			CONCAT('permission',i),
			CONCAT('description of permission',i)
		);
		SET j = 0;
		WHILE j < number_of_parameters DO
			INSERT INTO wl_GroupPermissionParameterType(
				gppt_name,
				gppt_type,
				gppt_description,
				gppt_group_permission_type_id
			) VALUES (
				CONCAT('parameter',j),
				CONCAT('type of parameter',j),
				CONCAT('description of parameter',j,' of permission',i),
				GetGroupPermissionIDByName(CONCAT('permission',i))
			);
			SET j = j + 1;
		END WHILE;
		SET i = i + 1;
	END WHILE;
END$

DELIMITER ;

-- ------------------------------------------------------------------------------------
-- ---------           ADDING EXTERNAL ENTITY PERMISSION TYPES        -----------------
-- ------------------------------------------------------------------------------------

DELIMITER $

CREATE PROCEDURE AddExternalEntityPermissionType(permission_number INT, number_of_parameters INT)
BEGIN
	DECLARE i INT DEFAULT 0;
	DECLARE j INT;
	WHILE i < permission_number DO
		INSERT INTO wl_ExternalEntityPermissionType(
			eept_name,
			eept_description
		) VALUES (
			CONCAT('permission',i),
			CONCAT('description of permission',i)
		);
		SET j = 0;
		WHILE j < number_of_parameters DO
			INSERT INTO wl_ExternalEntityPermissionParameterType(
				eeppt_name,
				eeppt_type,
				eeppt_description,
				eeppt_ext_ent_permission_type_id
			) VALUES (
				CONCAT('parameter',j),
				CONCAT('type of parameter',j),
				CONCAT('description of parameter',j,' of permission',i),
				GetExternalEntityPermissionIDByName(CONCAT('permission',i))
			);
			SET j = j + 1;
		END WHILE;
		SET i = i + 1;
	END WHILE;
END$

DELIMITER ;



-- There is no stored process in the main file, this
-- shouldn't generate any additional error to the tests

GRANT EXECUTE ON WebLab.*
	TO wl_admin_read@localhost IDENTIFIED BY 'wl_admin_read_password';

GRANT EXECUTE ON WebLab.*
	TO wl_admin_write@localhost IDENTIFIED BY 'wl_admin_write_password';

GRANT EXECUTE ON WebLab.*
	TO wl_student_read@localhost IDENTIFIED BY 'wl_student_read_password';

GRANT EXECUTE ON WebLab.*
	TO wl_student_write@localhost IDENTIFIED BY 'wl_student_write_password';

GRANT EXECUTE ON WebLab.*
	TO wl_prof_read@localhost IDENTIFIED BY 'wl_prof_read_password';

GRANT EXECUTE ON WebLab.*
	TO wl_prof_write@localhost IDENTIFIED BY 'wl_prof_write_password';

GRANT EXECUTE ON WebLab.*
	TO wl_exter_read@localhost IDENTIFIED BY 'wl_exter_read_password';

GRANT EXECUTE ON WebLab.*
	TO wl_exter_write@localhost IDENTIFIED BY 'wl_exter_write_password';


