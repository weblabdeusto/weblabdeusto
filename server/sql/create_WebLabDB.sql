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

-- SQL for creating the database in a MySQL server
-- $ mysql -uroot -p < createDB_MySQL.sql
--

-- TODO list:
-- * all TODOs during the whole file
-- 
-- > Now they're all complaining about documentation. Until this TODO list not
--	completed, updating documentation makes no sense.
-- 
-- * owner IDs... should there be any kind of trigger to check that they must 
-- 	have some "level" (a student shouldn't be owner of a group, for example)
-- 
-- > Right now, nobody except for root can avoid the permissions, so this kind
--	of situation should not happen. Anyway, I leave it in the TODO list.
-- > A more important point is, before UPDATing a wl_User, check that if the user
--	is professor and he owns some groups (for example), something is wrong.
-- 
-- * Optimization in subqueries in the views
--
-- > Need more time and knowledge 0:-)
--
-- * Consider: GroupPermissionInstance... can owner_id be different from the
--      group's owner_id?
-- * Can multiple teachers administrate a group? how? 
-- * Should anybody be able to update a date? Should anybody even be able to 
--   add a start_date instead of being the database engine the one who inserts
--   this information?
-- * Consider, when inserting into a table a new experiment for example, checking
--   if the experiment's finish_date is still NULL. (Trigger)
-- * Check better administrator and USER permissions, no where condition
-- * No DELETE operation granted.
-- * Tests, Tests, Tests...

DROP DATABASE IF EXISTS `WebLab`;
CREATE DATABASE `WebLab` ;

use `WebLab`;

--
-- The database is defined as a set of tables to store the information, and, 
-- on top of them, a set of views. The users of the database will not have 
-- access to the tables themselves, because they will only be able to access 
-- the views.
--
-- The database is designed to have several users:
--
-- *) wl_student_read, wl_student_write
-- *) wl_prof_read, wl_prof_write
-- *) wl_exter_read, wl_exter_write
-- *) wl_admin_read, wl_admin_write
-- *) wl_auth_read
--
-- The _read users can only access with read operations to the views, while the 
-- _write users might be able to access with some write operations (such as 
-- UPDATE or INSERT depending on the case). Each user will have access only to 
-- the information which is strictly needed. Students are not allowed to access 
-- any view designed to get or modify information of the External Entities, or 
-- students will be able to see a view of the Users table (without the password)
-- , and students will be able to modify another view of the Users table where 
-- only students are displayed, being only possible to modify a couple of fields
-- (INSERT will not be available). The "student" user might be able to see the 
-- commands from students, and the administrator might be able too see any 
-- command from anybody, but even the administrator will not be able to execute
-- an UPDATE sentence on the commands.
--
-- This design just adds a new layer of security in the database. In case 
-- someone achieves to perform an SQL Injection attack on some server, the 
-- problem will be the fact is that there is an SQL Injection vulnerability on 
-- the server, and it should be removed. But, if he achieves it in an operation 
-- performed by a wl_student_read, he will not be able to see any password, neither 
-- any information about external entities, etc. This design just reduces a 
-- little the impact of the attack. And this allows the WebLab database server 
-- to run the commands some servers ask to be executed with the very lowest 
-- permissions needed (and even discarding commands from servers which shouldn't
-- be allowed to run in other permissions).
-- 

-- ------------------------------------------------------------------------------------
-- ------------------------------------------------------------------------------------
-- ------------------------------------------------------------------------------------
-- ------------             T A B L E S     D E F I N I T I O N            ------------
-- ------------------------------------------------------------------------------------
-- ------------------------------------------------------------------------------------
-- ------------------------------------------------------------------------------------



-- ------------------------------------------------------------------------------------
-- ----------------             USER AND GROUP DEFINITION            ------------------
-- ------------------------------------------------------------------------------------


CREATE TABLE wl_Role (
	role_id				INT		NOT NULL	AUTO_INCREMENT PRIMARY KEY 
						COMMENT 'ROLE id',
	role_name 			VARCHAR( 20 )	NOT NULL	
						COMMENT 'Role name: professor, administrator, student...',

	UNIQUE (
		role_name
	)
) ENGINE = InnoDB ;

-- The default roles: both the application and the database
-- are designed for them. Any change on this table might
-- imply several changes
INSERT INTO wl_Role ( role_name ) VALUES ( 'administrator' ) ;
INSERT INTO wl_Role ( role_name ) VALUES ( 'professor' ) ;
INSERT INTO wl_Role ( role_name ) VALUES ( 'student' ) ;

CREATE TABLE wl_User (
	user_id 			INT 		NOT NULL 	AUTO_INCREMENT PRIMARY KEY 
						COMMENT 'User ID',
	user_login 			VARCHAR( 32 ) 	NOT NULL 	
						COMMENT 'User''s login',
	user_full_name 			VARCHAR( 200 ) 	NOT NULL 	
						COMMENT 'User''s full name',
	user_email 			VARCHAR( 255 ) 	NOT NULL 	
						COMMENT 'User''s e-mail ',
	user_password 			VARCHAR( 255 ) 
						COMMENT 'User''s hashed password. Format: 
						XXXX{format}YYYYYYYY 
						being XXXX a random number of random characters 
						added to the password, 	and "format" the hash 
						algorithm (MD5, SHA...)',
	web_password			VARCHAR( 255 ) 
						COMMENT 'User''s hashed password.
						The format is defined by the web application.
						Moodle, for example, uses MD5',
	user_role_id			INT		NOT NULL	
						COMMENT 'User role',
	
	FOREIGN KEY (user_role_id)	REFERENCES wl_Role ( role_id )	ON DELETE CASCADE,
	UNIQUE (
		user_login
	)
) ENGINE = InnoDB ;

-- TODO: add to the doc
CREATE TABLE wl_UserAuth (
	user_auth_id			INT 		NOT NULL	AUTO_INCREMENT PRIMARY KEY
						COMMENT 'User Auth ID',
	auth_name			VARCHAR(200)	NOT NULL
						COMMENT 'User Auth Name (ldap, for example)'
) ENGINE = InnoDB ;

INSERT INTO wl_UserAuth( auth_name )  VALUES ('LDAP');
INSERT INTO wl_UserAuth( auth_name )  VALUES ('TRUSTED-IP-ADDRESSES');

-- TODO: add to the doc
CREATE TABLE wl_UserAuthInstance (
	user_auth_instance_id 		INT 		NOT NULL	AUTO_INCREMENT PRIMARY KEY
						COMMENT 'User Auth Instance ID',
	uai_user_auth_id		INT		NOT NULL
						COMMENT 'User Auth ID',
	uai_name			VARCHAR(200)	NOT NULL
						COMMENT 'Name of the instance',
	uai_configuration		TEXT		NOT NULL
						COMMENT 'Configuration of the UserAuth',
	FOREIGN KEY (uai_user_auth_id)	REFERENCES wl_UserAuth ( user_auth_id ) ON DELETE CASCADE,
	UNIQUE (
		uai_name
	) 
) ENGINE = InnoDB ;

-- TODO: add to the doc
CREATE TABLE wl_UserAuthUserRelation(
	uaur_user_id				INT		NOT NULL
						COMMENT 'The user ID reference',
	uaur_user_auth_instance_id		INT		NOT NULL
						COMMENT 'The user auth ID reference',
	FOREIGN KEY (uaur_user_id)			REFERENCES wl_User ( user_id ) ON DELETE CASCADE,
	FOREIGN KEY (uaur_user_auth_instance_id)	REFERENCES wl_UserAuthInstance ( user_auth_instance_id ) ON DELETE CASCADE,
	UNIQUE (
		uaur_user_id,
		uaur_user_auth_instance_id
	)
) ENGINE = InnoDB ;

CREATE TABLE wl_ExternalEntity (
	external_entity_id		INT		NOT NULL	AUTO_INCREMENT PRIMARY KEY 
						COMMENT 'External Entity''s id',
	external_entity_name		VARCHAR(255)	NOT NULL	
						COMMENT 'External Entity''s name',
	external_entity_country		VARCHAR(20)	NOT NULL	
						COMMENT 'External Entity''s country',
	external_entity_description	text		NOT NULL	
						COMMENT 'External Entity''s description',
	external_entity_password	VARCHAR(255)	NOT NULL	
						COMMENT 'External Entity''s password, same format as in wl_User',
	external_entity_public_key	VARCHAR(255)	NOT NULL	
						COMMENT 'External Entity''s public key to check they''re who they say',

	UNIQUE (
		external_entity_name
	)
) ENGINE = InnoDB ;


CREATE TABLE wl_Group (
	group_id 			INT 		NOT NULL 	AUTO_INCREMENT PRIMARY KEY 
						COMMENT 'Group''s id',
	group_name 			VARCHAR( 250 ) 	NOT NULL 	
						COMMENT 'Group''s name',
	group_owner_id 			INT 		NOT NULL 	
						COMMENT 'Group''s owner''s ID',

	FOREIGN KEY (group_owner_id) 	REFERENCES wl_User(user_id) 	ON DELETE CASCADE,

	UNIQUE (
		group_name
	)
) ENGINE = InnoDB ;

-- ------------------------------------------------------------------------------------
-- ---------------             GROUP MEMBERSHIP DEFINITION            -----------------
-- ------------------------------------------------------------------------------------


CREATE TABLE wl_UserIsMemberOf (
	user_id 			INT 		NOT NULL 	
						COMMENT 'User''s id',
	group_id 			INT 		NOT NULL 	
						COMMENT 'Group''s id',

	FOREIGN KEY (user_id) 		REFERENCES wl_User(user_id) 	ON DELETE CASCADE,
	FOREIGN KEY (group_id) 		REFERENCES wl_Group(group_id) 	ON DELETE CASCADE
) ENGINE = InnoDB ;

CREATE TABLE wl_GroupIsMemberOf (
	group_id			INT		NOT NULL	
						COMMENT 'Group with this id is member of the other group',
	group_owner_id			INT		NOT NULL	
						COMMENT 'Group with this id has as member the other group',

	FOREIGN KEY (group_id)		REFERENCES wl_Group(group_id)	ON DELETE CASCADE,
	FOREIGN KEY (group_owner_id)	REFERENCES wl_Group(group_id)	ON DELETE CASCADE
) ENGINE = InnoDB ;

CREATE TABLE wl_ExternalEntityIsMemberOf (
	external_entity_id		INT		NOT NULL	
						COMMENT 'External Entity''s id',
	group_id			INT		NOT NULL	
						COMMENT 'Group''s id',

	FOREIGN KEY (
		external_entity_id
	)				REFERENCES wl_ExternalEntity (
						external_entity_id
					)				ON DELETE CASCADE,
	FOREIGN KEY (
		group_id
	)				REFERENCES wl_Group (
						group_id
					)				ON DELETE CASCADE
) ENGINE = InnoDB ;

-- -------------------------------------------------------------------
-- ----------             EXPERIMENTS DEFINITION            ----------
-- -------------------------------------------------------------------

CREATE TABLE wl_ExperimentCategory (
	experiment_category_id		INT		NOT NULL	AUTO_INCREMENT PRIMARY KEY 
						COMMENT 'Table key',
	experiment_category_name	VARCHAR(255)	NOT NULL	
						COMMENT 'Name of the experiment category',

	UNIQUE (
		experiment_category_name
	)
) ENGINE = InnoDB ;

CREATE TABLE wl_Experiment (
	experiment_id			INT		NOT NULL	AUTO_INCREMENT PRIMARY KEY 
						COMMENT 'Table key',
	experiment_owner_id		INT		NOT NULL	
						COMMENT 'The ID of the owner of the Experiment',
	experiment_category_id		INT		NOT NULL	
						COMMENT 'The ID of the category of the Experiment',
	experiment_start_date		DATE		NOT NULL	
						COMMENT 'When did the experiment started?',
	experiment_end_date		DATE				
						COMMENT 'When did the experiment finished?',
	experiment_name			VARCHAR(255)	NOT NULL	
						COMMENT 'The name of the experiment',
	FOREIGN KEY ( 
		experiment_owner_id
	)				REFERENCES wl_User (
						user_id
					)				ON DELETE CASCADE,
	FOREIGN KEY (
		experiment_category_id
	)				REFERENCES wl_ExperimentCategory(
						experiment_category_id
					)				ON DELETE CASCADE,
	UNIQUE (
		experiment_name,
		experiment_category_id
	)
) ENGINE = InnoDB ;

-- ------------------------------------------------------------------------------------
-- --------             EXPERIMENT INSTANCE MEMBERSHIP DEFINITION            ----------
-- ------------------------------------------------------------------------------------

CREATE TABLE wl_UserUsedExperiment (
	uue_user_experiment_use_id 	INT 		NOT NULL 	AUTO_INCREMENT PRIMARY KEY 
						COMMENT 'Table key',
	uue_user_id 			INT 		NOT NULL 	
						COMMENT 'User''s id',
	uue_start_date 			DATETIME	NOT NULL 	
						COMMENT 'When did the user start the experiment?',
	uue_start_date_micro		INT		NOT NULL
						COMMENT 'The microseconds of that date',
	uue_finish_date			DATETIME 		 		
						COMMENT 'When did the user finish the experiment?',
	uue_finish_date_micro		INT		NOT NULL
						COMMENT 'The microseconds of that date',
	uue_from			VARCHAR(255)	NOT NULL
						COMMENT 'Where did the user connect from? (IP/whatever)',
	uue_experiment_id		INT		NOT NULL
						COMMENT 'Experiment ID (ud-pld@PLD Experiments)',
	uue_coord_address		VARCHAR(255)	NOT NULL
						COMMENT 'Coordinator address of the server used (server:instance@machine)',
	FOREIGN KEY (uue_user_id)	
			REFERENCES wl_User(user_id)	
				ON DELETE CASCADE,
	FOREIGN KEY (uue_experiment_id)	
			REFERENCES wl_Experiment(experiment_id)	
				ON DELETE CASCADE
) ENGINE = InnoDB ;

CREATE TABLE wl_UserFile (
	user_file_id			INT 		NOT NULL	AUTO_INCREMENT PRIMARY KEY
						COMMENT 'Table key',
	experiment_use_id		INT		NOT NULL
						COMMENT 'Experiment use ID',			
	file_sent			VARCHAR(255)	NOT NULL
						COMMENT 'Path to the file (/path/to/file)',
	file_hash			VARCHAR(255)	NOT NULL
						COMMENT 'Hash of the sent file',
	file_info			TEXT
						COMMENT 'A description about the file itself',
	response			TEXT
						COMMENT 'The response to sending that file',
	timestamp_before		DATETIME	NOT NULL
						COMMENT 'Timestamp before sending the file',
	timestamp_before_micro		INT		NOT NULL
						COMMENT 'The microseconds of that time',
	timestamp_after			DATETIME	
						COMMENT 'Timestamp after sending the file',
	timestamp_after_micro		INT	
						COMMENT 'The microseconds of that time',
	FOREIGN KEY (
		experiment_use_id
	)				REFERENCES wl_UserUsedExperiment (
						uue_user_experiment_use_id
					)				ON DELETE CASCADE
) ENGINE = InnoDB ;

CREATE TABLE wl_UserCommand (
	user_command_id			INT		NOT NULL	AUTO_INCREMENT PRIMARY KEY 
						COMMENT 'Table key',
	experiment_use_id		INT		NOT NULL	
						COMMENT 'Experiment use ID',
	command				text		NOT NULL	
						COMMENT 'Command serialized',
	response			text		
						COMMENT 'Response serialized',
	timestamp_before		DATETIME	NOT NULL
						COMMENT 'When was the command sent',
	timestamp_before_micro		INT		NOT NULL
						COMMENT 'The microseconds of that datetime',
	timestamp_after			DATETIME
						COMMENT 'When the command was finished',
	timestamp_after_micro		INT		
						COMMENT 'The microseconds of that datetime',
	FOREIGN KEY (
		experiment_use_id
	)				REFERENCES wl_UserUsedExperiment (
						uue_user_experiment_use_id
					)				ON DELETE CASCADE
) ENGINE = InnoDB ;

-- TODO: this should be the same as UserUsedExperiment
CREATE TABLE wl_ExternalEntityUsedExperiment (
	eeue_ext_ent_experiment_use_id 	INT 		NOT NULL 	AUTO_INCREMENT PRIMARY KEY 
						COMMENT 'Table key',
	eeue_ext_ent_id			INT 		NOT NULL 	
						COMMENT 'External Entity''s id',
	eeue_start_date 		DATETIME	NOT NULL 	
						COMMENT 'When did the external entity start the experiment?',
	eeue_finish_date		DATETIME			 	
						COMMENT 'When did the external entity finish the experiment?',
	eeue_from			VARCHAR(255)	NOT NULL
						COMMENT 'Where did the external entity connected from? 
							This should not be needed, but added just in case',
	eeue_file_sent			VARCHAR(255)	NOT NULL	
						COMMENT 'Path to the file (/path/to/file@machine1,machine2)',
	eeue_file_sent_hash		VARCHAR(255)	NOT NULL
						COMMENT 'Hash of the file',

	eeue_commands_file_sent		VARCHAR(255)
						COMMENT 'Path to the file sent with commands. Optional',
	eeue_commands_file_sent_hash	VARCHAR(255)
						COMMENT 'Hash of the commands file. Optional',
	eeue_result_output		VARCHAR(255)
						COMMENT 'Path to the file with the output of the experiment. Optional',
	eeue_result_output_hash		VARCHAR(255)
						COMMENT 'Hash of the file with the output of the experiment. Optional',

	FOREIGN KEY (
		eeue_ext_ent_id
	)				REFERENCES wl_ExternalEntity (
						external_entity_id
					)				ON DELETE CASCADE
) ENGINE = InnoDB ;

CREATE TABLE wl_ExternalEntityCommand (
	ee_command_id			INT		NOT NULL	AUTO_INCREMENT PRIMARY KEY 
						COMMENT 'Table key',
	experiment_use_id		INT		NOT NULL	
						COMMENT 'Experiment use ID',
	command				text		NOT NULL	
						COMMENT 'Command serialized',

	FOREIGN KEY (
		experiment_use_id
	)				REFERENCES wl_ExternalEntityUsedExperiment (
						eeue_ext_ent_experiment_use_id
					)				ON DELETE CASCADE
) ENGINE = InnoDB ;


-- ------------------------------------------------------------------------------------
-- ---------------------             USER PERMISSIONS            ----------------------
-- ------------------------------------------------------------------------------------

CREATE TABLE wl_UserPermissionType (
	upt_id				INT		NOT NULL	AUTO_INCREMENT PRIMARY KEY 
						COMMENT 'Key',
	upt_name			VARCHAR(255)	NOT NULL	
						COMMENT 'Name of the permission',
	upt_description			text		NOT NULL	
						COMMENT 'Description of the permission',

	UNIQUE (
		upt_name
	)
) ENGINE = InnoDB ;

CREATE TABLE wl_UserPermissionParameterType (
	uppt_id				INT 		NOT NULL	AUTO_INCREMENT PRIMARY KEY 
						COMMENT 'Key',
	uppt_name			VARCHAR(255)	NOT NULL	
						COMMENT 'Name of the type of the parameter',
	uppt_type			VARCHAR(255)	NOT NULL	
						COMMENT 'Data type of the parameter',
	uppt_description		text		NOT NULL	
						COMMENT 'Description of the parameter',
	uppt_user_permission_type_id	INT		NOT NULL	
						COMMENT 'ID of the user permission',

	FOREIGN KEY (
		uppt_user_permission_type_id
	)				REFERENCES wl_UserPermissionType(
						upt_id
					)				ON DELETE CASCADE,

	UNIQUE (
		uppt_name,
		uppt_user_permission_type_id
	)

) ENGINE = InnoDB ;

CREATE TABLE wl_UserPermissionInstance (
	upi_id				INT		NOT NULL	AUTO_INCREMENT PRIMARY KEY 
						COMMENT 'Key',
	upi_user_id			INT 		NOT NULL	
						COMMENT 'The ID of the user it refers to',
	upi_user_permission_type_id	INT		NOT NULL	
						COMMENT 'The type of permission',
	upi_owner_id			INT		NOT NULL	
						COMMENT 'Who has created this permission?',
	upi_date			DATETIME	NOT NULL	
						COMMENT 'When was this instance created?',
	upi_name			VARCHAR(255)	NOT NULL	
						COMMENT 'The name of the instance',
	upi_comments			text		NOT NULL	
						COMMENT 'Aditional comments to the instance',

	FOREIGN KEY ( 
		upi_user_id
	)				REFERENCES wl_User (
						user_id
					)				ON DELETE CASCADE,
	FOREIGN KEY (
		upi_owner_id
	)				REFERENCES wl_User (
						user_id
					)				ON DELETE CASCADE,
	FOREIGN KEY (
		upi_user_permission_type_id
	)				REFERENCES wl_UserPermissionType (
						upt_id
					)				ON DELETE CASCADE,

	UNIQUE (
		upi_name,
		upi_user_id
	)

) ENGINE = InnoDB ;

CREATE TABLE wl_UserPermissionParameter (
	upp_id				INT		NOT NULL	AUTO_INCREMENT PRIMARY KEY 
						COMMENT 'Key',
	upp_user_permission_instance_id	INT		NOT NULL	
						COMMENT 'The ID of the User Permission Instance',
	upp_user_permission_param_id	INT		NOT NULL	
						COMMENT 'The ID of the parameter type',
	upp_value			text			
						COMMENT 'The value of the parameter',

	FOREIGN KEY (
		upp_user_permission_instance_id
	) 				REFERENCES wl_UserPermissionInstance (
						upi_id
					)				ON DELETE CASCADE,
	FOREIGN KEY (
		upp_user_permission_param_id
	)				REFERENCES wl_UserPermissionParameterType (
						uppt_id
					)				ON DELETE CASCADE,

	UNIQUE (
		upp_user_permission_instance_id,
		upp_user_permission_param_id
	)

) ENGINE = InnoDB ;

-- ------------------------------------------------------------------------------------
-- --------------------             GROUP PERMISSIONS            ----------------------
-- ------------------------------------------------------------------------------------


CREATE TABLE wl_GroupPermissionType (
	gpt_id				INT		NOT NULL	AUTO_INCREMENT PRIMARY KEY 
						COMMENT 'Key',
	gpt_name			VARCHAR(255)	NOT NULL	
						COMMENT 'Name of the permission',
	gpt_description			text		NOT NULL	
						COMMENT 'Description of the permission',

	UNIQUE (
		gpt_name
	)
) ENGINE = InnoDB ;

CREATE TABLE wl_GroupPermissionParameterType (
	gppt_id				INT 		NOT NULL	AUTO_INCREMENT PRIMARY KEY 
						COMMENT 'Key',
	gppt_name			VARCHAR(255)	NOT NULL	
						COMMENT 'Name of the type of the parameter',
	gppt_type			VARCHAR(255)	NOT NULL	
						COMMENT 'Data type of the parameter',
	gppt_description		text		NOT NULL	
						COMMENT 'Description of the parameter',
	gppt_group_permission_type_id	INT		NOT NULL	
						COMMENT 'ID of the group permission',

	FOREIGN KEY (
		gppt_group_permission_type_id
	)				REFERENCES wl_GroupPermissionType(
						gpt_id
					)				ON DELETE CASCADE,
	
	UNIQUE (
		gppt_name,
		gppt_group_permission_type_id
	)
) ENGINE = InnoDB ;

CREATE TABLE wl_GroupPermissionInstance (
	gpi_id				INT		NOT NULL	AUTO_INCREMENT PRIMARY KEY 
						COMMENT 'Key',
	gpi_group_id			INT 		NOT NULL	
						COMMENT 'The ID of the group it refers to',
	gpi_group_permission_type_id	INT		NOT NULL	
						COMMENT 'The type of permission',
	gpi_owner_id			INT		NOT NULL	
						COMMENT 'Who has created this permission?',
	gpi_date			DATETIME	NOT NULL	
						COMMENT 'When was this instance created?',
	gpi_name			VARCHAR(255)	NOT NULL	
						COMMENT 'The name of the instance',
	gpi_comments			text		NOT NULL	
						COMMENT 'Aditional comments to the instance',

	FOREIGN KEY ( 
		gpi_group_id
	)				REFERENCES wl_Group (
						group_id
					)				ON DELETE CASCADE,
	FOREIGN KEY (
		gpi_owner_id
	)				REFERENCES wl_User (
						user_id
					)				ON DELETE CASCADE,
	FOREIGN KEY (
		gpi_group_permission_type_id
	)				REFERENCES wl_GroupPermissionType (
						gpt_id
					)				ON DELETE CASCADE,
	UNIQUE (
		gpi_name,
		gpi_group_id
	)

) ENGINE = InnoDB ;

CREATE TABLE wl_GroupPermissionParameter (
	gpp_id				INT		NOT NULL	AUTO_INCREMENT PRIMARY KEY 
						COMMENT 'Key',
	gpp_group_permission_instance_id INT		NOT NULL	
						COMMENT 'The ID of the group Permission Instance',
	gpp_group_permission_param_id	INT		NOT NULL	
						COMMENT 'The ID of the parameter type',
	gpp_value			text
						COMMENT 'The value of the parameter',

	FOREIGN KEY (
		gpp_group_permission_instance_id
	) 				REFERENCES wl_GroupPermissionInstance (
						gpi_id
					)				ON DELETE CASCADE,
	FOREIGN KEY (
		gpp_group_permission_param_id
	)				REFERENCES wl_GroupPermissionParameterType (
						gppt_id
					)				ON DELETE CASCADE,

	UNIQUE (
		gpp_group_permission_instance_id,
		gpp_group_permission_param_id
	)

) ENGINE = InnoDB ;

-- ------------------------------------------------------------------------------------
-- ---------------             EXTERNAL ENTITY PERMISSIONS            -----------------
-- ------------------------------------------------------------------------------------

CREATE TABLE wl_ExternalEntityPermissionType (
	eept_id				INT		NOT NULL	AUTO_INCREMENT PRIMARY KEY 
						COMMENT 'Key',
	eept_name			VARCHAR(255)	NOT NULL	
						COMMENT 'Name of the permission',
	eept_description		text		NOT NULL	
						COMMENT 'Description of the permission',

	UNIQUE (
		eept_name
	)
) ENGINE = InnoDB ;

CREATE TABLE wl_ExternalEntityPermissionParameterType (
	eeppt_id			INT 		NOT NULL	AUTO_INCREMENT PRIMARY KEY 
						COMMENT 'Key',
	eeppt_name			VARCHAR(255)	NOT NULL	
						COMMENT 'Name of the type of the parameter',
	eeppt_type			VARCHAR(255)	NOT NULL	
						COMMENT 'Data type of the parameter',
	eeppt_description		text		NOT NULL	
						COMMENT 'Description of the parameter',
	eeppt_ext_ent_permission_type_id INT		NOT NULL	
						COMMENT 'ID of the ext_ent permission',

	FOREIGN KEY (
		eeppt_ext_ent_permission_type_id
	)				REFERENCES wl_ExternalEntityPermissionType(
						eept_id
					)				ON DELETE CASCADE,
	UNIQUE (
		eeppt_name,
		eeppt_id
	)
) ENGINE = InnoDB ;

CREATE TABLE wl_ExternalEntityPermissionInstance (
	eepi_id				INT		NOT NULL	AUTO_INCREMENT PRIMARY KEY 
						COMMENT 'Key',
	eepi_ext_ent_id			INT 		NOT NULL	
						COMMENT 'The ID of the ext_ent it refers to',
	eepi_ext_ent_permission_type_id	INT		NOT NULL	
						COMMENT 'The type of permission',
	eepi_owner_id			INT		NOT NULL	
						COMMENT 'Who has created this permission?',
	eepi_date			DATETIME	NOT NULL	
						COMMENT 'When was this instance created?',
	eepi_name			VARCHAR(255)	NOT NULL	
						COMMENT 'The name of the instance',
	eepi_comments			text		NOT NULL	
						COMMENT 'Aditional comments to the instance',

	FOREIGN KEY ( 
		eepi_ext_ent_id
	)				REFERENCES wl_ExternalEntity (
						external_entity_id
					)				ON DELETE CASCADE,
	FOREIGN KEY (
		eepi_owner_id
	)				REFERENCES wl_User (
						user_id
					)				ON DELETE CASCADE,
	FOREIGN KEY (
		eepi_ext_ent_permission_type_id
	)				REFERENCES wl_ExternalEntityPermissionParameterType (
						eeppt_id
					)				ON DELETE CASCADE,
	UNIQUE (
		eepi_name,
		eepi_ext_ent_id
	)
) ENGINE = InnoDB ;

CREATE TABLE wl_ExternalEntityPermissionParameter (
	eepp_id				INT		NOT NULL	AUTO_INCREMENT PRIMARY KEY 
						COMMENT 'Key',
	eepp_ext_ent_permission_instance_id INT		NOT NULL	
						COMMENT 'The ID of the ext_ent Permission Instance',
	eepp_ext_ent_permission_param_id INT		NOT NULL	
						COMMENT 'The ID of the parameter type',
	eepp_value			text		NOT NULL	
						COMMENT 'The value of the parameter',

	FOREIGN KEY (
		eepp_ext_ent_permission_instance_id
	) 				REFERENCES wl_ExternalEntityPermissionInstance (
						eepi_id
					)				ON DELETE CASCADE,
	FOREIGN KEY (
		eepp_ext_ent_permission_param_id
	)				REFERENCES wl_ExternalEntityPermissionParameterType (
						eeppt_id
					)				ON DELETE CASCADE,

	UNIQUE (
		eepp_ext_ent_permission_instance_id,
		eepp_ext_ent_permission_param_id
	)

) ENGINE = InnoDB ;

-- ------------------------------------------------------------------------------------
-- -----------------             ERROR MANAGEMENT TABLES            -------------------
-- ------------------------------------------------------------------------------------

CREATE TABLE wl_Error_InvalidOwnerID (
	invalid_owner_id		INT		NOT NULL
) ENGINE = InnoDB;

CREATE TABLE wl_Error_HashFileMissing (
	hash_file_missing		INT		NOT NULL
) ENGINE = InnoDB;

CREATE TABLE wl_Error_WebPasswordMissing (
	web_password_missing		INT		NOT NULL
) ENGINE = InnoDB;

-- ------------------------------------------------------------------------------------
-- ------------------------------------------------------------------------------------
-- ------------------------------------------------------------------------------------
-- -------------             V I E W S     D E F I N I T I O N            -------------
-- ------------------------------------------------------------------------------------
-- ------------------------------------------------------------------------------------
-- ------------------------------------------------------------------------------------

-- 
-- Format of the names:
-- wl_v_ + [ a | e | p | s | auth ] + name of table
-- Optionally:
-- wl_v_ + [ a | e | p | s | auth ] + _ + [ rw_ + [ update_ |  insert_ ] + name of table
-- 
-- Being:
-- 	a: administrator
-- 	e: external entity
-- 	p: professor
-- 	s: student
-- 	auth: auth (only user enabled to check passwords)

-- ------------------------------------------------------------------------------------
-- ---------------------             STUDENT'S VIEWs             ----------------------
-- ------------------------------------------------------------------------------------

-- ------------------------------------
-- ----  USER AND GROUP DEFINITION ----
-- ------------------------------------

-- Read only
CREATE VIEW wl_v_s_Role
AS SELECT
--	*
	role_id,
	role_name
FROM wl_Role;

-- Read only
-- TODO: update documentation: user_password removed, WHERE different: at least he can see PROFESSORs
CREATE VIEW wl_v_s_User 
AS SELECT
--	* except for user_role_id and user_password and web_password
	user_id,
	user_login,
	user_full_name,
	user_email,
	user_role_id
FROM wl_User, wl_Role
WHERE 	user_role_id = role_id
	AND role_name IN ('student','professor');

-- The user can execute an UPDATE sentence
CREATE VIEW wl_v_s_rw_User
AS SELECT
--	Only the needed changes
	user_id,
	user_email,
	user_password,
	web_password
FROM wl_User, wl_Role
WHERE role_name = 'student' AND user_role_id = role_id
WITH CHECK OPTION;

-- Read only
-- Can't make a WHERE condition like "only if a student is
-- in the group", since a student could be in a group, and
-- that group could be in another group, and this group 
-- might not be listed.
CREATE VIEW wl_v_s_Group
AS SELECT
--	*
	group_id,
	group_name,
	group_owner_id
FROM wl_Group;

-- --------------------------------------
-- ----  GROUP MEMBERSHIP DEFINITION ----
-- --------------------------------------

-- Read only
CREATE VIEW wl_v_s_UserIsMemberOf
AS SELECT
--	*
	wl_UserIsMemberOf.user_id,
	group_id
FROM 	wl_UserIsMemberOf, wl_Role, wl_User
WHERE 	wl_UserIsMemberOf.user_id = wl_User.user_id
	AND user_role_id = role_id
	AND role_name = 'student';

-- Read only
-- No condition, see wl_v_s_Group
CREATE VIEW wl_v_s_GroupIsMemberOf
AS SELECT
--	*
	group_id,
	group_owner_id
FROM wl_GroupIsMemberOf;

-- ---------------------------------
-- ----  EXPERIMENTS DEFINITION ----
-- ---------------------------------

-- Read only
CREATE VIEW wl_v_s_ExperimentCategory 
AS SELECT
--	*
	experiment_category_id,
	experiment_category_name
FROM wl_ExperimentCategory;

-- Read only
CREATE VIEW wl_v_s_Experiment
AS SELECT
--	*
	experiment_id,
	experiment_owner_id,
	experiment_category_id,
	experiment_start_date,
	experiment_end_date,
	experiment_name
FROM wl_Experiment;

-- ----------------------------------------------------
-- ----  EXPERIMENT INSTANCE MEMBERSHIP DEFINITION ----
-- ----------------------------------------------------

-- Read only
-- TODO: update documentation: start_date, finish_date
CREATE VIEW wl_v_s_UserUsedExperiment
AS SELECT
--	*
	uue_user_experiment_use_id,
	uue_user_id,
	uue_start_date,
	uue_start_date_micro,
	uue_finish_date,
	uue_finish_date_micro,
	uue_from,
	uue_experiment_id,
	uue_coord_address
FROM 	wl_UserUsedExperiment, wl_User, wl_Role
WHERE 	uue_user_id = user_id
	AND user_role_id = role_id
	AND role_name = 'student';

-- INSERT
CREATE VIEW wl_v_s_rw_insert_UserUsedExperiment
AS SELECT
--	*
	uue_user_experiment_use_id,
	uue_user_id,
	uue_start_date,
	uue_start_date_micro,
	uue_finish_date,
	uue_finish_date_micro,
	uue_from,
	uue_experiment_id,
	uue_coord_address
FROM 	wl_UserUsedExperiment, wl_User, wl_Role
WHERE 	uue_user_id = user_id
	AND user_role_id = role_id
	AND role_name = 'student'
-- TODO: We have a problem that we were not able to complete here
-- It's explained here: http://forums.mysql.com/read.php?100,246120,246120#msg-246120
-- WITH CHECK OPTION;
;

-- Read
CREATE VIEW wl_v_s_UserFile
AS SELECT
--	*
	user_file_id,
	experiment_use_id,
	file_sent,
	file_hash,
	file_info,
	response,
	timestamp_before,
	timestamp_before_micro,
	timestamp_after,
	timestamp_after_micro
FROM 	wl_UserFile, wl_UserUsedExperiment, wl_User, wl_Role
WHERE	experiment_use_id = uue_user_experiment_use_id
	AND uue_user_id = user_id
	AND user_role_id = role_id
	AND role_name = 'student';

-- INSERT
CREATE VIEW wl_v_s_rw_UserFile
AS SELECT
--	*
	user_file_id,
	experiment_use_id,
	file_sent,
	file_hash,
	file_info,
	response,
	timestamp_before,
	timestamp_before_micro,
	timestamp_after,
	timestamp_after_micro
FROM 	wl_UserFile, wl_UserUsedExperiment, wl_User, wl_Role
WHERE	experiment_use_id = uue_user_experiment_use_id
	AND uue_user_id = user_id
	AND user_role_id = role_id
	AND role_name = 'student'
-- TODO: We have a problem that we were not able to complete here
-- It's explained here: http://forums.mysql.com/read.php?100,246120,246120#msg-246120
-- WITH CHECK OPTION;
;

-- Read
CREATE VIEW wl_v_s_UserCommand
AS SELECT
--	*
	user_command_id,
	experiment_use_id,
	command,
	response,
	timestamp_before,
	timestamp_before_micro,
	timestamp_after,
	timestamp_after_micro
FROM 	wl_UserCommand, wl_UserUsedExperiment, wl_User, wl_Role
WHERE	experiment_use_id = uue_user_experiment_use_id
	AND uue_user_id = user_id
	AND user_role_id = role_id
	AND role_name = 'student';

-- INSERT
CREATE VIEW wl_v_s_rw_UserCommand
AS SELECT
--	*
	user_command_id,
	experiment_use_id,
	command,
	response,
	timestamp_before,
	timestamp_before_micro,
	timestamp_after,
	timestamp_after_micro
FROM 	wl_UserCommand, wl_UserUsedExperiment, wl_User, wl_Role
WHERE	experiment_use_id = uue_user_experiment_use_id
	AND uue_user_id = user_id
	AND user_role_id = role_id
	AND role_name = 'student'
-- TODO: We have a problem that we were not able to complete here
-- It's explained here: http://forums.mysql.com/read.php?100,246120,246120#msg-246120
-- WITH CHECK OPTION;
;

-- ---------------------------
-- ----  USER PERMISSIONS ----
-- ---------------------------

-- Read only
CREATE VIEW wl_v_s_UserPermissionType
AS SELECT
--	*
	upt_id,
	upt_name,
	upt_description
FROM wl_UserPermissionType;

-- Read only
CREATE VIEW wl_v_s_UserPermissionParameterType
AS SELECT
--	*
	uppt_id,
	uppt_name,
	uppt_type,
	uppt_description,
	uppt_user_permission_type_id
FROM wl_UserPermissionParameterType;

-- Read only
CREATE VIEW wl_v_s_UserPermissionInstance
AS SELECT
--	*
	upi_id,
	upi_user_id,
	upi_user_permission_type_id,
	upi_owner_id,
	upi_date,
	upi_name,
	upi_comments
FROM 	wl_UserPermissionInstance, wl_User, wl_Role
WHERE 	upi_user_id = user_id
	AND user_role_id = role_id
	AND role_name = 'student';

-- Read only
CREATE VIEW wl_v_s_UserPermissionParameter
AS SELECT
--	*
	upp_id,
	upp_user_permission_instance_id,
	upp_user_permission_param_id,
	upp_value
FROM 	wl_UserPermissionParameter, wl_UserPermissionInstance, wl_User, wl_Role
WHERE	upp_user_permission_instance_id = upi_id
	AND upi_user_id = user_id
	AND user_role_id = role_id
	AND role_name = 'student';

-- -----------------------------
-- ----  GROUP PERMISSIONS  ----
-- -----------------------------

-- Read only
CREATE VIEW wl_v_s_GroupPermissionType
AS SELECT
--	*
	gpt_id,
	gpt_name,
	gpt_description
FROM wl_GroupPermissionType;

-- Read only
CREATE VIEW wl_v_s_GroupPermissionParameterType
AS SELECT
--	*
	gppt_id,
	gppt_name,
	gppt_type,
	gppt_description,
	gppt_group_permission_type_id
FROM wl_GroupPermissionParameterType;

-- Read only
CREATE VIEW wl_v_s_GroupPermissionInstance
AS SELECT
--	*
	gpi_id,
	gpi_group_id,
	gpi_group_permission_type_id,
	gpi_owner_id,
	gpi_date,
	gpi_name,
	gpi_comments
FROM wl_GroupPermissionInstance;

-- Read only
CREATE VIEW wl_v_s_GroupPermissionParameter
AS SELECT
--	*
	gpp_id,
	gpp_group_permission_instance_id,
	gpp_group_permission_param_id,
	gpp_value
FROM wl_GroupPermissionParameter;

-- ------------------------------------------------------------------------------------
-- --------------------             PROFESSOR'S VIEWs             ---------------------
-- ------------------------------------------------------------------------------------

-- ------------------------------------
-- ----  USER AND GROUP DEFINITION ----
-- ------------------------------------

-- Read only
CREATE VIEW wl_v_p_Role
AS SELECT
--	*
	role_id,
	role_name
FROM wl_Role;

-- Read only
-- TODO: update documentation: no password field
CREATE VIEW wl_v_p_User
AS SELECT
	user_id,
	user_login,
	user_full_name,
	user_email,
	user_role_id
FROM wl_User;

-- INSERT
CREATE VIEW wl_v_p_rw_insert_User
AS SELECT
	user_id,
	user_login,
	user_full_name,
	user_email,
	user_password,
	web_password,
	user_role_id
FROM wl_User, wl_Role
WHERE 	user_role_id = role_id
	AND role_name = 'student'
WITH CHECK OPTION;

-- UPDATE
CREATE VIEW wl_v_p_rw_update_User
AS SELECT
	user_id,
	user_email,
	user_password,
	web_password
FROM wl_User, wl_Role
WHERE	user_role_id = role_id
	AND role_name = 'professor'
WITH CHECK OPTION;

-- Read only
CREATE VIEW wl_v_p_Group
AS SELECT
--	*
	group_id,
	group_name,
	group_owner_id
FROM wl_Group;

-- UPDATE and INSERT available
CREATE VIEW wl_v_p_rw_Group
AS SELECT
	group_id,
	group_name,
	group_owner_id
FROM wl_Group, wl_User, wl_Role
WHERE	user_id = group_owner_id 
	AND user_role_id = role_id
	AND role_name = 'professor'
WITH CHECK OPTION;

-- --------------------------------------
-- ----  GROUP MEMBERSHIP DEFINITION ----
-- --------------------------------------

-- Read only
CREATE VIEW wl_v_p_UserIsMemberOf
AS SELECT
	wl_UserIsMemberOf.user_id,
	wl_UserIsMemberOf.group_id
FROM 	wl_UserIsMemberOf, wl_User, wl_Role
WHERE	wl_UserIsMemberOf.user_id = wl_User.user_id
	AND user_role_id = role_id
	AND role_name IN ('professor','student');

-- INSERT
CREATE VIEW wl_v_p_rw_UserIsMemberOf
AS SELECT
	wl_UserIsMemberOf.user_id,
	wl_UserIsMemberOf.group_id
FROM	wl_UserIsMemberOf, wl_Group, wl_User, wl_Role
WHERE	wl_UserIsMemberOf.group_id = wl_Group.group_id
	AND wl_User.user_id = wl_Group.group_owner_id
	AND user_role_id = role_id
	AND role_name = 'professor'
	AND wl_UserIsMemberOf.user_id IN (
		SELECT 
			user_id 
		FROM	wl_User, wl_Role
		WHERE	user_role_id = role_id
			AND role_name = 'student'
	)
WITH CHECK OPTION;

-- Read only
CREATE VIEW wl_v_p_GroupIsMemberOf
AS SELECT
--	*
	group_id,
	group_owner_id
FROM wl_GroupIsMemberOf;

-- INSERT
CREATE VIEW wl_v_p_rw_GroupIsMemberOf
AS SELECT
	group_id,
	group_owner_id
FROM wl_GroupIsMemberOf, wl_User, wl_Role
WHERE	user_id = group_owner_id
	AND user_role_id = role_id
	AND role_name = 'professor'
WITH CHECK OPTION;

-- ---------------------------------
-- ----  EXPERIMENTS DEFINITION ----
-- ---------------------------------

-- Read only
CREATE VIEW wl_v_p_ExperimentCategory 
AS SELECT
--	*
	experiment_category_id,
	experiment_category_name
FROM wl_ExperimentCategory;

-- Read only
CREATE VIEW wl_v_p_Experiment
AS SELECT
--	*
	experiment_id,
	experiment_owner_id,
	experiment_category_id,
	experiment_start_date,
	experiment_end_date,
	experiment_name
FROM wl_Experiment;

-- ----------------------------------------------------
-- ----  EXPERIMENT INSTANCE MEMBERSHIP DEFINITION ----
-- ----------------------------------------------------

-- Read only
CREATE VIEW wl_v_p_UserUsedExperiment
AS SELECT
--	*
	uue_user_experiment_use_id,
	uue_user_id,
	uue_start_date,
	uue_start_date_micro,
	uue_finish_date,
	uue_finish_date_micro,
	uue_from,
	uue_experiment_id,
	uue_coord_address
FROM wl_UserUsedExperiment, wl_User, wl_Role
WHERE	user_id = uue_user_id
	AND user_role_id = role_id
	AND role_name in ('professor','student');

-- INSERT
CREATE VIEW wl_v_p_rw_insert_UserUsedExperiment
AS SELECT
--	*
	uue_user_experiment_use_id,
	uue_user_id,
	uue_start_date,
	uue_start_date_micro,
	uue_finish_date,
	uue_finish_date_micro,
	uue_from,
	uue_experiment_id,
	uue_coord_address
FROM wl_UserUsedExperiment, wl_User, wl_Role
WHERE	user_id = uue_user_id
	AND user_role_id = role_id
	AND role_name = 'professor'
-- TODO: We have a problem that we were not able to complete here
-- It's explained here: http://forums.mysql.com/read.php?100,246120,246120#msg-246120
-- WITH CHECK OPTION;
;

-- Read only
CREATE VIEW wl_v_p_UserFile
AS SELECT
--	*
	user_file_id,
	experiment_use_id,
	file_sent,
	file_hash,
	file_info,
	response,
	timestamp_before,
	timestamp_before_micro,
	timestamp_after,
	timestamp_after_micro
FROM 	wl_UserFile, wl_UserUsedExperiment, wl_User, wl_Role
WHERE	experiment_use_id = uue_user_experiment_use_id
	AND uue_user_id = user_id
	AND user_role_id = role_id
	AND role_name IN ('professor','student')
-- TODO: We have a problem that we were not able to complete here
-- It's explained here: http://forums.mysql.com/read.php?100,246120,246120#msg-246120
-- WITH CHECK OPTION;
;

-- INSERT
CREATE VIEW wl_v_p_rw_UserFile
AS SELECT
--	*
	user_file_id,
	experiment_use_id,
	file_sent,
	file_hash,
	file_info,
	response,
	timestamp_before,
	timestamp_before_micro,
	timestamp_after,
	timestamp_after_micro
FROM 	wl_UserFile, wl_UserUsedExperiment, wl_User, wl_Role
WHERE	experiment_use_id = uue_user_experiment_use_id
	AND uue_user_id = user_id
	AND user_role_id = role_id
	AND role_name = 'professor'
-- TODO: We have a problem that we were not able to complete here
-- It's explained here: http://forums.mysql.com/read.php?100,246120,246120#msg-246120
-- WITH CHECK OPTION;
;

-- Read only
CREATE VIEW wl_v_p_UserCommand
AS SELECT
--	*
	user_command_id,
	experiment_use_id,
	command,
	response,
	timestamp_before,
	timestamp_before_micro,
	timestamp_after,
	timestamp_after_micro
FROM 	wl_UserCommand, wl_UserUsedExperiment, wl_User, wl_Role
WHERE	experiment_use_id = uue_user_experiment_use_id
	AND uue_user_id = user_id
	AND user_role_id = role_id
	AND role_name IN ('professor','student')
-- TODO: We have a problem that we were not able to complete here
-- It's explained here: http://forums.mysql.com/read.php?100,246120,246120#msg-246120
-- WITH CHECK OPTION;
;

-- INSERT
CREATE VIEW wl_v_p_rw_UserCommand
AS SELECT
--	*
	user_command_id,
	experiment_use_id,
	command,
	response,
	timestamp_before,
	timestamp_before_micro,
	timestamp_after,
	timestamp_after_micro
FROM 	wl_UserCommand, wl_UserUsedExperiment, wl_User, wl_Role
WHERE	experiment_use_id = uue_user_experiment_use_id
	AND uue_user_id = user_id
	AND user_role_id = role_id
	AND role_name = 'professor'
-- TODO: We have a problem that we were not able to complete here
-- It's explained here: http://forums.mysql.com/read.php?100,246120,246120#msg-246120
-- WITH CHECK OPTION;
;

-- ---------------------------
-- ----  USER PERMISSIONS ----
-- ---------------------------

-- Read only
CREATE VIEW wl_v_p_UserPermissionType
AS SELECT
--	*
	upt_id,
	upt_name,
	upt_description
FROM wl_UserPermissionType;

-- Read only
CREATE VIEW wl_v_p_UserPermissionParameterType
AS SELECT
--	*
	uppt_id,
	uppt_name,
	uppt_type,
	uppt_description,
	uppt_user_permission_type_id
FROM wl_UserPermissionParameterType;

-- Read only
CREATE VIEW wl_v_p_UserPermissionInstance
AS SELECT
--	*
	upi_id,
	upi_user_id,
	upi_user_permission_type_id,
	upi_owner_id,
	upi_date,
	upi_name,
	upi_comments
FROM 	wl_UserPermissionInstance, wl_User, wl_Role
WHERE 	upi_user_id = user_id
	AND user_role_id = role_id
	AND role_name IN ('student','professor');

-- INSERT, UPDATE
CREATE VIEW wl_v_p_rw_UserPermissionInstance
AS SELECT
--	*
	upi_id,
	upi_user_id,
	upi_user_permission_type_id,
	upi_owner_id,
	upi_date,
	upi_name,
	upi_comments
FROM 	wl_UserPermissionInstance, wl_User, wl_Role
WHERE 	upi_user_id = user_id
	AND user_role_id = role_id
	AND role_name = 'student'
	AND upi_owner_id IN (
		SELECT
			user_id
		FROM	wl_User, wl_Role
		WHERE	user_role_id = role_id
			AND role_name = 'professor'
	)
WITH CHECK OPTION;

-- Read only
CREATE VIEW wl_v_p_UserPermissionParameter
AS SELECT
--	*
	upp_id,
	upp_user_permission_instance_id,
	upp_user_permission_param_id,
	upp_value
FROM 	wl_UserPermissionParameter, wl_UserPermissionInstance, wl_User, wl_Role
WHERE	upp_user_permission_instance_id = upi_id
	AND upi_user_id = user_id
	AND user_role_id = role_id
	AND role_name IN ('student','professor');

-- A user permission has a number of parameters (0-*). This number of
-- parameters is defined in a table called wl_UserPermissionParameterType.
-- And for an instance of a parameter, the parameters are related with
-- the rows in the wl_UserPermissionParameterType table, giving them values.
-- The problem is that there is no way to ensure that for a user permission
-- instance, there will be the exact number of parameters defined (there could
-- be less).

-- For example, we could have:
-- 'myPermissionType' in wl_UserPermissionType
-- 'myParameterType1' and 'myParameterType2' in wl_UserPermissionParameterType
-- and then we insert an instance of this parameter:
-- 'myPermission' in wl_UserPermissionInstance
-- Then, I'm suppossed to insert something like:
-- 'myPermissionParameterValue1' and 'myPermissionParameterValue2'
-- but nobody ensures that this will happen. It could happen that nobody inserts
-- any parameter, and even worse: someone later could add a now missing parameter.

-- To solve this, we will not allow any user to insert any row into
-- wl_UserPermissionParameter, and, at the same time, we will have a trigger
-- AFTER INSERT in wl_UserPermissionInstance that will make the INSERTs
-- necessary, assigning NULL as value. Later, the user will have to UPDATE
-- the values of the parameters.

-- UPDATE
CREATE VIEW wl_v_p_rw_UserPermissionParameter
AS SELECT
--	*
	upp_id,
	upp_user_permission_instance_id,
	upp_user_permission_param_id,
	upp_value
FROM 	wl_UserPermissionParameter, wl_UserPermissionInstance, wl_User, wl_Role
WHERE	upp_user_permission_instance_id = upi_id
	AND upi_user_id = user_id
	AND user_role_id = role_id
	AND role_name = 'student'
	AND upi_owner_id IN (
		SELECT user_id
		FROM wl_User, wl_Role
		WHERE 	user_role_id = role_id
			AND role_name = 'professor'
	)
WITH CHECK OPTION;

-- -----------------------------
-- ----  GROUP PERMISSIONS  ----
-- -----------------------------

-- Read only
CREATE VIEW wl_v_p_GroupPermissionType
AS SELECT
--	*
	gpt_id,
	gpt_name,
	gpt_description
FROM wl_GroupPermissionType;

-- Read only
CREATE VIEW wl_v_p_GroupPermissionParameterType
AS SELECT
--	*
	gppt_id,
	gppt_name,
	gppt_type,
	gppt_description,
	gppt_group_permission_type_id
FROM wl_GroupPermissionParameterType;

-- Read only
CREATE VIEW wl_v_p_GroupPermissionInstance
AS SELECT
--	*
	gpi_id,
	gpi_group_id,
	gpi_group_permission_type_id,
	gpi_owner_id,
	gpi_date,
	gpi_name,
	gpi_comments
FROM 	wl_GroupPermissionInstance;

-- INSERT, UPDATE
CREATE VIEW wl_v_p_rw_GroupPermissionInstance
AS SELECT
--	*
	gpi_id,
	gpi_group_id,
	gpi_group_permission_type_id,
	gpi_owner_id,
	gpi_date,
	gpi_name,
	gpi_comments
FROM wl_GroupPermissionInstance, wl_User, wl_Role, wl_Group
WHERE	gpi_owner_id = user_id
	AND user_role_id = role_id
	AND role_name = 'professor'
	AND gpi_group_id IN (
		SELECT 
			group_id
		FROM 	wl_Group, wl_User, wl_Role
		WHERE 	group_owner_id = user_id
			AND user_role_id = role_id
			AND role_name = 'professor'
	)
WITH CHECK OPTION;

-- Read only
CREATE VIEW wl_v_p_GroupPermissionParameter
AS SELECT
--	*
	gpp_id,
	gpp_group_permission_instance_id,
	gpp_group_permission_param_id,
	gpp_value
FROM wl_GroupPermissionParameter;

-- UPDATE (no INSERT: same explanation as the one in wl_v_p_rw_UserPermissionParameter)
CREATE VIEW wl_v_p_rw_GroupPermissionParameter
AS SELECT
--	*
	gpp_id,
	gpp_group_permission_instance_id,
	gpp_group_permission_param_id,
	gpp_value
FROM	wl_GroupPermissionParameter, wl_GroupPermissionInstance, wl_Group, wl_User, wl_Role
WHERE	gpp_group_permission_instance_id = gpi_id
	AND gpi_group_id = group_id
	AND group_owner_id = user_id
	AND user_role_id = role_id
	AND role_name = 'student'
	AND gpi_owner_id IN (
		SELECT user_id
		FROM wl_User, wl_Role
		WHERE 	user_role_id = role_id
			AND role_name = 'professor'
	)
WITH CHECK OPTION;

-- ------------------------------------------------------------------------------------
-- -----------------             EXTERNAL ENTITY'S VIEWs             ------------------
-- ------------------------------------------------------------------------------------

-- -------------------------------------
-- ----  USER AND GROUP DEFINITION  ----
-- -------------------------------------

-- TODO: update the documentation: external entity's can't see wl_User neither
-- wl_Role, while Group Permission Instances and External Entity Permission 
-- Instance have owner_id fields.

-- Read only
CREATE VIEW wl_v_e_User
AS SELECT
	user_login,
	user_full_name,
	user_email
FROM wl_User, wl_Role
WHERE	user_role_id = role_id
	AND role_name = 'administrator';

-- Read only
CREATE VIEW wl_v_e_ExternalEntity
AS SELECT
--	* but password
	external_entity_id,
	external_entity_name,
	external_entity_country,
	external_entity_description,
	external_entity_public_key
FROM wl_ExternalEntity;

-- UPDATE
CREATE VIEW wl_v_e_rw_ExternalEntity
AS SELECT
	external_entity_id,
	external_entity_password
FROM wl_ExternalEntity;

-- Read only
CREATE VIEW wl_v_e_Group
AS SELECT
--	*
	group_id,
	group_name,
	group_owner_id
FROM	wl_Group;

-- --------------------------------------
-- ----  GROUP MEMBERSHIP DEFINITION ----
-- --------------------------------------

-- TODO: update in doc
-- Read only
CREATE VIEW wl_v_e_GroupIsMemberOf
AS SELECT
--	*
	group_id,
	group_owner_id
FROM	wl_GroupIsMemberOf;

-- Read only
CREATE VIEW wl_v_e_ExternalEntityIsMemberOf
AS SELECT
--	*
	external_entity_id,
	group_id
FROM wl_ExternalEntityIsMemberOf;

-- ---------------------------------
-- ----  EXPERIMENTS DEFINITION ----
-- ---------------------------------

-- Read only
CREATE VIEW wl_v_e_ExperimentCategory
AS SELECT
--	*
	experiment_category_id, 
	experiment_category_name
FROM wl_ExperimentCategory;

-- Read only
CREATE VIEW wl_v_e_Experiment
AS SELECT
--	*
	experiment_id,
	experiment_owner_id,
	experiment_category_id,
	experiment_start_date,
	experiment_end_date,
	experiment_name
FROM wl_Experiment; 

-- ----------------------------------------------------
-- ----  EXPERIMENT INSTANCE MEMBERSHIP DEFINITION ----
-- ----------------------------------------------------

-- Read only
CREATE VIEW wl_v_e_ExternalEntityUsedExperiment
AS SELECT
--	*
	eeue_ext_ent_experiment_use_id,
	eeue_ext_ent_id,
	eeue_start_date,
	eeue_finish_date,
	eeue_from,
	eeue_file_sent,
	eeue_file_sent_hash,
	eeue_commands_file_sent,
	eeue_commands_file_sent_hash,
	eeue_result_output,
	eeue_result_output_hash
FROM wl_ExternalEntityUsedExperiment;

-- INSERT
CREATE VIEW wl_v_e_rw_insert_ExternalEntityUsedExperiment
AS SELECT
--	*
	eeue_ext_ent_experiment_use_id,
	eeue_ext_ent_id,
	eeue_start_date,
	eeue_finish_date,
	eeue_from,
	eeue_file_sent,
	eeue_file_sent_hash,
	eeue_commands_file_sent,
	eeue_commands_file_sent_hash,
	eeue_result_output,
	eeue_result_output_hash
FROM wl_ExternalEntityUsedExperiment;

-- UPDATE
CREATE VIEW wl_v_e_rw_update_ExternalEntityUsedExperiment
AS SELECT
	eeue_ext_ent_experiment_use_id,
	eeue_finish_date,
	eeue_result_output
FROM wl_ExternalEntityUsedExperiment;

-- Read
CREATE VIEW wl_v_e_ExternalEntityCommand
AS SELECT
	ee_command_id,
	experiment_use_id,
	command
FROM wl_ExternalEntityCommand;

-- INSERT
CREATE VIEW wl_v_e_rw_ExternalEntityCommand
AS SELECT
	ee_command_id,
	experiment_use_id,
	command
FROM wl_ExternalEntityCommand;

-- ----------------------------
-- ----  GROUP PERMISSIONS ----
-- ----------------------------

-- Read only
CREATE VIEW wl_v_e_GroupPermissionType
AS SELECT
--	*
	gpt_id,
	gpt_name,
	gpt_description
FROM wl_GroupPermissionType;

-- Read only
CREATE VIEW wl_v_e_GroupPermissionParameterType
AS SELECT
--	*
	gppt_id,
	gppt_name,
	gppt_type,
	gppt_description,
	gppt_group_permission_type_id
FROM wl_GroupPermissionParameterType;

-- Read only
CREATE VIEW wl_v_e_GroupPermissionInstance
AS SELECT
--	*
	gpi_id,
	gpi_group_id,
	gpi_group_permission_type_id,
	gpi_owner_id,
	gpi_date,
	gpi_name,
	gpi_comments
FROM wl_GroupPermissionInstance;

-- Read only
CREATE VIEW wl_v_e_GroupPermissionParameter
AS SELECT
--	*
	gpp_id,
	gpp_group_permission_instance_id,
	gpp_group_permission_param_id,
	gpp_value
FROM wl_GroupPermissionParameter;

-- ----------------------------------------
-- ----  EXTERNAL ENTITIES PERMISSIONS ----
-- ----------------------------------------

-- Read only
CREATE VIEW wl_v_e_ExternalEntityPermissionType
AS SELECT
--	*
	eept_id,
	eept_name,
	eept_description
FROM wl_ExternalEntityPermissionType;

-- Read only
CREATE VIEW wl_v_e_ExternalEntityPermissionParameterType
AS SELECT
--	*
	eeppt_id,
	eeppt_name,
	eeppt_type,
	eeppt_description,
	eeppt_ext_ent_permission_type_id
FROM wl_ExternalEntityPermissionParameterType;

-- Read only
CREATE VIEW wl_v_e_ExternalEntityPermissionInstance
AS SELECT
--	*
	eepi_id,
	eepi_ext_ent_id,
	eepi_owner_id,
	eepi_date,
	eepi_name,
	eepi_comments
FROM wl_ExternalEntityPermissionInstance;

-- Read only
CREATE VIEW wl_v_e_ExternalEntityPermissionParameter
AS SELECT
--	*
	eepp_id,
	eepp_ext_ent_permission_instance_id,
	eepp_ext_ent_permission_param_id,
	eepp_value
FROM wl_ExternalEntityPermissionParameter;

-- ------------------------------------------------------------------------------------
-- ------------------             ADMINISTRATOR'S VIEWs             -------------------
-- ------------------------------------------------------------------------------------

-- ------------------------------------
-- ---- USER AND GROUP DEFINITION  ----
-- ------------------------------------

-- Read only
CREATE VIEW wl_v_a_Role
AS SELECT
--	*
	role_id,
	role_name
FROM wl_Role;

-- Read only
CREATE VIEW wl_v_a_User
AS SELECT
--	*
	user_id,
	user_login,
	user_full_name,
	user_email,
	user_role_id
FROM wl_User;

-- INSERT, UPDATE
CREATE VIEW wl_v_a_rw_User
AS SELECT
--	*
	user_id,
	user_login,
	user_full_name,
	user_email,
	user_password,
	web_password,
	user_role_id
FROM wl_User;

-- Read only
CREATE VIEW wl_v_a_UserAuth
AS SELECT
--	*
	user_auth_id,
	auth_name
FROM wl_UserAuth;

-- Read only
CREATE VIEW wl_v_a_UserAuthInstance
AS SELECT
--	*
	user_auth_instance_id,
	uai_user_auth_id,
	uai_name,
	uai_configuration
FROM wl_UserAuthInstance;

-- INSERT, UPDATE
CREATE VIEW wl_v_a_rw_UserAuthInstance
AS SELECT
--	*
	user_auth_instance_id,
	uai_user_auth_id,
	uai_name,
	uai_configuration
FROM wl_UserAuthInstance;

-- Read only
CREATE VIEW wl_v_a_UserAuthUserRelation
AS SELECT
--	*
	uaur_user_id,
	uaur_user_auth_instance_id
FROM wl_UserAuthUserRelation;

-- INSERT, UPDATE
CREATE VIEW wl_v_a_rw_UserAuthUserRelation
AS SELECT
--	*
	uaur_user_id,
	uaur_user_auth_instance_id
FROM wl_UserAuthUserRelation;

-- Read only
CREATE VIEW wl_v_a_ExternalEntity
AS SELECT
--	*
	external_entity_id,
	external_entity_name,
	external_entity_country,
	external_entity_description,
	external_entity_public_key
FROM wl_ExternalEntity;

-- INSERT, UPDATE
CREATE VIEW wl_v_a_rw_ExternalEntity
AS SELECT
--	*
	external_entity_id,
	external_entity_name,
	external_entity_country,
	external_entity_description,
	external_entity_password,
	external_entity_public_key
FROM wl_ExternalEntity;

-- Read only
CREATE VIEW wl_v_a_Group
AS SELECT
--	*
	group_id,
	group_name,
	group_owner_id
FROM wl_Group;

-- INSERT, UPDATE
CREATE VIEW wl_v_a_rw_Group
AS SELECT
--	*
	group_id,
	group_name,
	group_owner_id
FROM wl_Group;

-- --------------------------------------
-- ----  GROUP MEMBERSHIP DEFINITION ----
-- --------------------------------------

-- Read only
CREATE VIEW wl_v_a_UserIsMemberOf
AS SELECT
--	*
	user_id,
	group_id
FROM wl_UserIsMemberOf;

-- INSERT
CREATE VIEW wl_v_a_rw_UserIsMemberOf
AS SELECT
--	*
	user_id,
	group_id
FROM wl_UserIsMemberOf;

-- Read only
CREATE VIEW wl_v_a_GroupIsMemberOf
AS SELECT
--	*
	group_id,
	group_owner_id
FROM wl_GroupIsMemberOf;

-- INSERT
CREATE VIEW wl_v_a_rw_GroupIsMemberOf
AS SELECT
--	*
	group_id,
	group_owner_id
FROM wl_GroupIsMemberOf;

-- Read only
CREATE VIEW wl_v_a_ExternalEntityIsMemberOf
AS SELECT
--	*
	external_entity_id,
	group_id
FROM wl_ExternalEntityIsMemberOf;

-- INSERT
CREATE VIEW wl_v_a_rw_ExternalEntityIsMemberOf
AS SELECT
--	*
	external_entity_id,
	group_id
FROM wl_ExternalEntityIsMemberOf;

-- --------------------------------------
-- ----  GROUP MEMBERSHIP DEFINITION ----
-- --------------------------------------

-- Read only
CREATE VIEW wl_v_a_ExperimentCategory
AS SELECT
--	*
	experiment_category_id,
	experiment_category_name
FROM wl_ExperimentCategory;

-- INSERT, UPDATE
CREATE VIEW wl_v_a_rw_ExperimentCategory
AS SELECT
--	*
	experiment_category_id,
	experiment_category_name
FROM wl_ExperimentCategory;

-- Read only
CREATE VIEW wl_v_a_Experiment
AS SELECT
--	*
	experiment_id,
	experiment_owner_id,
	experiment_category_id,
	experiment_start_date,
	experiment_end_date,
	experiment_name
FROM wl_Experiment;

-- INSERT, UPDATE
CREATE VIEW wl_v_a_rw_Experiment
AS SELECT
--	*
	experiment_id,
	experiment_owner_id,
	experiment_category_id,
	experiment_start_date,
	experiment_end_date,
	experiment_name
FROM wl_Experiment;

-- ----------------------------------------------------
-- ----  EXPERIMENT INSTANCE MEMBERSHIP DEFINITION ----
-- ----------------------------------------------------

-- Read only
CREATE VIEW wl_v_a_UserUsedExperiment
AS SELECT
--	*
	uue_user_experiment_use_id,
	uue_user_id,
	uue_start_date,
	uue_start_date_micro,
	uue_finish_date,
	uue_finish_date_micro,
	uue_from,
	uue_experiment_id,
	uue_coord_address
FROM wl_UserUsedExperiment;

-- INSERT
CREATE VIEW wl_v_a_rw_insert_UserUsedExperiment
AS SELECT
--	*
	uue_user_experiment_use_id,
	uue_user_id,
	uue_start_date,
	uue_start_date_micro,
	uue_finish_date,
	uue_finish_date_micro,
	uue_from,
	uue_experiment_id,
	uue_coord_address
FROM 	wl_UserUsedExperiment, wl_User, wl_Role
WHERE	uue_user_id = user_id
	AND user_role_id = role_id
	AND role_name = 'administrator'
-- TODO: We have a problem that we were not able to complete here
-- It's explained here: http://forums.mysql.com/read.php?100,246120,246120#msg-246120
-- WITH CHECK OPTION;
;

-- Read only
CREATE VIEW wl_v_a_UserFile
AS SELECT
--	*
	user_file_id,
	experiment_use_id,
	file_sent,
	file_hash,
	file_info,
	response,
	timestamp_before,
	timestamp_before_micro,
	timestamp_after,
	timestamp_after_micro
FROM	wl_UserFile; 

-- INSERT
CREATE VIEW wl_v_a_rw_UserFile
AS SELECT
--	*
	user_file_id,
	experiment_use_id,
	file_sent,
	file_hash,
	file_info,
	response,
	timestamp_before,
	timestamp_before_micro,
	timestamp_after,
	timestamp_after_micro
FROM	wl_UserFile, wl_UserUsedExperiment, wl_User, wl_Role
WHERE	experiment_use_id = uue_user_experiment_use_id
	AND uue_user_id = user_id
	AND user_role_id = role_id
	AND role_name = 'administrator'
-- TODO: We have a problem that we were not able to complete here
-- It's explained here: http://forums.mysql.com/read.php?100,246120,246120#msg-246120
-- WITH CHECK OPTION;
;

-- Read only
CREATE VIEW wl_v_a_UserCommand
AS SELECT
--	*
	user_command_id,
	experiment_use_id,
	command,
	response,
	timestamp_before,
	timestamp_before_micro,
	timestamp_after,
	timestamp_after_micro
FROM	wl_UserCommand; 

-- INSERT
CREATE VIEW wl_v_a_rw_UserCommand
AS SELECT
--	*
	user_command_id,
	experiment_use_id,
	command,
	response,
	timestamp_before,
	timestamp_before_micro,
	timestamp_after,
	timestamp_after_micro
FROM	wl_UserCommand, wl_UserUsedExperiment, wl_User, wl_Role
WHERE	experiment_use_id = uue_user_experiment_use_id
	AND uue_user_id = user_id
	AND user_role_id = role_id
	AND role_name = 'administrator'
-- TODO: We have a problem that we were not able to complete here
-- It's explained here: http://forums.mysql.com/read.php?100,246120,246120#msg-246120
-- WITH CHECK OPTION;
;

-- Read only
CREATE VIEW wl_v_a_ExternalEntityUsedExperiment
AS SELECT
--	*
	eeue_ext_ent_experiment_use_id,
	eeue_ext_ent_id,
	eeue_start_date,
	eeue_finish_date,
	eeue_from,
	eeue_file_sent,
	eeue_file_sent_hash,
	eeue_commands_file_sent,
	eeue_commands_file_sent_hash,
	eeue_result_output,
	eeue_result_output_hash
FROM	wl_ExternalEntityUsedExperiment;

-- Read only
CREATE VIEW wl_v_a_ExternalEntityCommand
AS SELECT
--	*
	ee_command_id,
	experiment_use_id,
	command
FROM 	wl_ExternalEntityCommand;

-- ----------------------------
-- ----  USER PERMISSIONS  ----
-- ----------------------------

-- Read only
CREATE VIEW wl_v_a_UserPermissionType
AS SELECT
--	*
	upt_id,
	upt_name,
	upt_description
FROM wl_UserPermissionType;

-- Read only
CREATE VIEW wl_v_a_UserPermissionParameterType
AS SELECT
--	*
	uppt_id,
	uppt_name,
	uppt_type,
	uppt_description,
	uppt_user_permission_type_id
FROM wl_UserPermissionParameterType;

-- Read only
CREATE VIEW wl_v_a_UserPermissionInstance
AS SELECT
--	*
	upi_id,
	upi_user_id,
	upi_user_permission_type_id,
	upi_owner_id,
	upi_date,
	upi_name,
	upi_comments
FROM wl_UserPermissionInstance;

-- INSERT, UPDATE 
CREATE VIEW wl_v_a_rw_UserPermissionInstance
AS SELECT
--	*
	upi_id,
	upi_user_id,
	upi_user_permission_type_id,
	upi_owner_id,
	upi_date,
	upi_name,
	upi_comments
FROM wl_UserPermissionInstance;

-- Read only
CREATE VIEW wl_v_a_UserPermissionParameter
AS SELECT
--	*
	upp_id,
	upp_user_permission_instance_id,
	upp_user_permission_param_id,
	upp_value
FROM wl_UserPermissionParameter;

-- UPDATE
CREATE VIEW wl_v_a_rw_UserPermissionParameter
AS SELECT
--	*
	upp_id,
	upp_user_permission_instance_id,
	upp_user_permission_param_id,
	upp_value
FROM wl_UserPermissionParameter;

-- ----------------------------
-- ----  GROUP PERMISSIONS  ---
-- ----------------------------

-- Read only
CREATE VIEW wl_v_a_GroupPermissionType
AS SELECT
--	*
	gpt_id,
	gpt_name,
	gpt_description
FROM wl_GroupPermissionType;

-- Read only
CREATE VIEW wl_v_a_GroupPermissionParameterType
AS SELECT
--	*
	gppt_id,
	gppt_name,
	gppt_type,
	gppt_description,
	gppt_group_permission_type_id
FROM wl_GroupPermissionParameterType;

-- Read only
CREATE VIEW wl_v_a_GroupPermissionInstance
AS SELECT
--	*
	gpi_id,
	gpi_group_id,
	gpi_group_permission_type_id,
	gpi_owner_id,
	gpi_date,
	gpi_name,
	gpi_comments
FROM wl_GroupPermissionInstance;

-- INSERT, UPDATE
CREATE VIEW wl_v_a_rw_GroupPermissionInstance
AS SELECT
--	*
	gpi_id,
	gpi_group_id,
	gpi_group_permission_type_id,
	gpi_owner_id,
	gpi_date,
	gpi_name,
	gpi_comments
FROM wl_GroupPermissionInstance;

-- Read only
CREATE VIEW wl_v_a_GroupPermissionParameter
AS SELECT
--	*
	gpp_id,
	gpp_group_permission_instance_id,
	gpp_group_permission_param_id,
	gpp_value
FROM wl_GroupPermissionParameter;

-- UPDATE
CREATE VIEW wl_v_a_rw_GroupPermissionParameter
AS SELECT
--	*
	gpp_id,
	gpp_group_permission_instance_id,
	gpp_group_permission_param_id,
	gpp_value
FROM wl_GroupPermissionParameter;

-- ---------------------------------------
-- ----  EXTERNAL ENTITY PERMISSIONS  ----
-- ---------------------------------------

-- Read only
CREATE VIEW wl_v_a_ExternalEntityPermissionType
AS SELECT
--	*
	eept_id,
	eept_name,
	eept_description
FROM wl_ExternalEntityPermissionType;

-- Read only
CREATE VIEW wl_v_a_ExternalEntityPermissionParameterType
AS SELECT
--	*
	eeppt_id,
	eeppt_name,
	eeppt_type,
	eeppt_description,
	eeppt_ext_ent_permission_type_id
FROM wl_ExternalEntityPermissionParameterType;

-- Read only
CREATE VIEW wl_v_a_ExternalEntityPermissionInstance
AS SELECT
--	*
	eepi_id,
	eepi_ext_ent_id,
	eepi_ext_ent_permission_type_id,
	eepi_owner_id,
	eepi_date,
	eepi_name,
	eepi_comments
FROM wl_ExternalEntityPermissionInstance;

-- INSERT, UPDATE
CREATE VIEW wl_v_a_rw_ExternalEntityPermissionInstance
AS SELECT
--	*
	eepi_id,
	eepi_ext_ent_id,
	eepi_ext_ent_permission_type_id,
	eepi_owner_id,
	eepi_date,
	eepi_name,
	eepi_comments
FROM wl_ExternalEntityPermissionInstance;

-- Read only
CREATE VIEW wl_v_a_ExternalEntityPermissionParameter
AS SELECT
--	*
	eepp_id,
	eepp_ext_ent_permission_instance_id,
	eepp_ext_ent_permission_param_id,
	eepp_value
FROM wl_ExternalEntityPermissionParameter;

-- UPDATE
CREATE VIEW wl_v_a_rw_ExternalEntityPermissionParameter
AS SELECT
--	*
	eepp_id,
	eepp_ext_ent_permission_instance_id,
	eepp_ext_ent_permission_param_id,
	eepp_value
FROM wl_ExternalEntityPermissionParameter;

-- ------------------------------------------------------------------------------------
-- ---------------------             AUTH'S VIEWs             -------------------------
-- ------------------------------------------------------------------------------------

-- Read only
CREATE VIEW wl_v_auth_Role
AS SELECT
--	*
	role_id,
	role_name
FROM wl_Role;

-- Read only
CREATE VIEW wl_v_auth_User
AS SELECT
--	*
	user_id,
	user_login,
	user_password,
	user_role_id
FROM wl_User;

-- Read only
CREATE VIEW wl_v_auth_UserAuth
AS SELECT
--	*
	user_auth_id,
	auth_name
FROM wl_UserAuth;

-- Read only
CREATE VIEW wl_v_auth_UserAuthInstance
AS SELECT
--	*
	user_auth_instance_id,
	uai_user_auth_id,
	uai_name,
	uai_configuration
FROM wl_UserAuthInstance;

-- Read only
CREATE VIEW wl_v_auth_UserAuthUserRelation
AS SELECT
--	*
	uaur_user_id,
	uaur_user_auth_instance_id
FROM wl_UserAuthUserRelation;

-- ------------------------------------------------------------------------------------
-- ------------------------------------------------------------------------------------
-- ------------------------------------------------------------------------------------
-- ----------             T R I G G E R S     D E F I N I T I O N            ----------
-- ------------------------------------------------------------------------------------
-- ------------------------------------------------------------------------------------
-- ------------------------------------------------------------------------------------

DELIMITER $

-- Whenever someone inserts a user permission instance,
-- the database itself will create the needed rows for
-- its parameters

CREATE TRIGGER wl_t_AddUserPermissionParameters
AFTER INSERT ON wl_UserPermissionInstance
FOR EACH ROW BEGIN
	DECLARE done INT DEFAULT 0;
	DECLARE parameter_type_id INT;
	DECLARE parameter_types_ids CURSOR FOR 
		SELECT uppt_id 
		FROM wl_UserPermissionParameterType
		WHERE uppt_user_permission_type_id = 
			NEW.upi_user_permission_type_id;
	DECLARE CONTINUE HANDLER FOR SQLSTATE '02000' SET done = 1;
	OPEN parameter_types_ids;

	REPEAT
		FETCH parameter_types_ids INTO parameter_type_id;
		IF NOT done THEN
			INSERT INTO wl_UserPermissionParameter(
				upp_user_permission_instance_id,
				upp_user_permission_param_id,
				upp_value
			)VALUES(
				NEW.upi_id,
				parameter_type_id,
				NULL
			);
		END IF;
	UNTIL done END REPEAT;	

	CLOSE parameter_types_ids;
END$

-- Whenever someone inserts a group permission instance,
-- the database itself will create the needed rows for
-- its parameters

CREATE TRIGGER wl_t_AddGroupPermissionParameters
AFTER INSERT ON wl_GroupPermissionInstance
FOR EACH ROW BEGIN
	DECLARE done INT DEFAULT 0;
	DECLARE parameter_type_id INT;
	DECLARE parameter_types_ids CURSOR FOR 
		SELECT gppt_id 
		FROM wl_GroupPermissionParameterType
		WHERE gppt_group_permission_type_id = 
			NEW.gpi_group_permission_type_id;
	DECLARE CONTINUE HANDLER FOR SQLSTATE '02000' SET done = 1;
	OPEN parameter_types_ids;

	REPEAT
		FETCH parameter_types_ids INTO parameter_type_id;
		IF NOT done THEN
			INSERT INTO wl_GroupPermissionParameter(
				gpp_group_permission_instance_id,
				gpp_group_permission_param_id,
				gpp_value
			)VALUES(
				NEW.gpi_id,
				parameter_type_id,
				NULL
			);
		END IF;
	UNTIL done END REPEAT;	

	CLOSE parameter_types_ids;
END$

-- Whenever someone inserts an External Entity permission instance,
-- the database itself will create the needed rows for
-- its parameters

CREATE TRIGGER wl_t_AddExternalEntityPermissionParameters
AFTER INSERT ON wl_ExternalEntityPermissionInstance
FOR EACH ROW BEGIN
	DECLARE done INT DEFAULT 0;
	DECLARE parameter_type_id INT;
	DECLARE parameter_types_ids CURSOR FOR 
		SELECT eeppt_id 
		FROM wl_ExternalEntityPermissionParameterType
		WHERE eeppt_ext_ent_permission_type_id = 
			NEW.eepi_ext_ent_permission_type_id;
	DECLARE CONTINUE HANDLER FOR SQLSTATE '02000' SET done = 1;
	OPEN parameter_types_ids;

	REPEAT
		FETCH parameter_types_ids INTO parameter_type_id;
		IF NOT done THEN
			INSERT INTO wl_ExternalEntityPermissionParameter(
				eepp_ext_ent_permission_instance_id,
				eepp_ext_ent_permission_param_id,
				eepp_value
			)VALUES(
				NEW.eepi_id,
				parameter_type_id,
				NULL
			);
		END IF;
	UNTIL done END REPEAT;	

	CLOSE parameter_types_ids;
END$

-- Whenever anybody by error tries to add a new group whose owner ID is
-- a student

CREATE TRIGGER wl_t_CheckGroupOwnerId
BEFORE INSERT ON wl_Group
FOR EACH ROW BEGIN
	DECLARE owners_role_id INT;
	DECLARE owners_role_name VARCHAR( 20 );
	SELECT user_role_id INTO owners_role_id 
		FROM wl_User WHERE user_id = NEW.group_owner_id;
	SELECT role_name INTO owners_role_name
		FROM wl_Role WHERE role_id = owners_role_id;
	IF owners_role_name = 'student' THEN
		-- Error!
		INSERT INTO wl_Error_InvalidOwnerID (invalid_owner_id) 
			VALUES (NULL);
	END IF;
END$

-- Whenever someone updates a wl_UserUsedExperiment file, we require a
-- hash or we will raise an error.
CREATE TRIGGER wl_t_CheckHashFileNotMissingUpdatingUserUsedExperiment
BEFORE UPDATE ON wl_UserFile
FOR EACH ROW BEGIN

	IF OLD.file_sent != NEW.file_sent 
	  AND OLD.file_hash = NEW.file_hash THEN
		INSERT INTO wl_Error_HashFileMissing(hash_file_missing) 
			VALUES (NULL);
	END IF;
END$

-- Whenever someone updates a wl_ExternalEntityUsedExperiment file, we require a
-- hash or we will raise an error.
CREATE TRIGGER wl_t_CheckHashFileNotMissingUpdatingExternalEntityUsedExperiment
BEFORE UPDATE ON wl_ExternalEntityUsedExperiment
FOR EACH ROW BEGIN

	IF OLD.eeue_file_sent != NEW.eeue_file_sent 
	  AND OLD.eeue_file_sent_hash = NEW.eeue_file_sent_hash THEN
		INSERT INTO wl_Error_HashFileMissing(hash_file_missing) 
			VALUES (NULL);
	END IF;

	IF OLD.eeue_commands_file_sent != NEW.eeue_commands_file_sent 
	  AND OLD.eeue_commands_file_sent_hash = NEW.eeue_commands_file_sent_hash THEN
		INSERT INTO wl_Error_HashFileMissing(hash_file_missing) 
			VALUES (NULL);
	END IF;

	IF OLD.eeue_result_output != NEW.eeue_result_output 
	  AND OLD.eeue_result_output_hash = NEW.eeue_result_output_hash THEN
		INSERT INTO wl_Error_HashFileMissing(hash_file_missing) VALUES (NULL);
	END IF;
END$

-- Whenever someone inserts a wl_ExternalEntityUsedExperiment file, we require a
-- hash or we will raise an error.
CREATE TRIGGER wl_t_CheckHashFileNotMissingInsertingExteEntUsedExp
BEFORE INSERT ON wl_ExternalEntityUsedExperiment
FOR EACH ROW BEGIN

	IF NEW.eeue_commands_file_sent != NULL 
	  AND NEW.eeue_commands_file_sent_hash = NULL THEN
		INSERT INTO wl_Error_HashFileMissing(hash_file_missing) 
			VALUES (NULL);
	END IF;

	IF NEW.eeue_result_output != NULL
	  AND NEW.eeue_result_output_hash = NULL THEN
		INSERT INTO wl_Error_HashFileMissing(hash_file_missing) 
			VALUES (NULL);
	END IF;
END$

-- Whenever the web application updates the web_password in the wl_User,
-- the user_password should be updated.
CREATE TRIGGER wl_t_CheckUserPassword
BEFORE UPDATE ON wl_User
FOR EACH ROW BEGIN
	IF OLD.user_password = NEW.user_password
	  AND OLD.web_password != NEW.web_password THEN
		SET NEW.user_password = CONCAT('{md5}',NEW.web_password);
	END IF;
END$

-- Whenever someone tries to update the user_password and doesn't update
-- the web_password, we raise an error.
CREATE TRIGGER wl_t_CheckWebPasswordBeingUpdated
AFTER UPDATE ON wl_User
FOR EACH ROW BEGIN
	IF OLD.user_password != NEW.user_password
	  AND OLD.web_password = NEW.web_password THEN
		INSERT INTO wl_Error_WebPasswordMissing(web_password_missing) 
			VALUES(NULL);
	END IF;
END$

DELIMITER ;

-- ------------------------------------------------------------------------------------
-- ------------------------------------------------------------------------------------
-- ------------------------------------------------------------------------------------
-- ---------------        P E R M I S S I O N S    V A L U E S       ------------------
-- ------------------------------------------------------------------------------------
-- ------------------------------------------------------------------------------------
-- ------------------------------------------------------------------------------------

DELIMITER $

CREATE FUNCTION GetUserPermissionTypeID(name VARCHAR(255))
RETURNS INT
READS SQL DATA
BEGIN
	DECLARE variable INT;
	SELECT upt_id INTO variable
		FROM wl_UserPermissionType WHERE upt_name = name;
	RETURN variable;
END$

DELIMITER ;

INSERT INTO wl_UserPermissionType(
	upt_name,
	upt_description
)VALUES(
	'experiment_allowed',
	'This type has a parameter which is the permanent ID (not a INT) of an Experiment. Users which have this permission will have access to the experiment defined in this parameter'
);

INSERT INTO wl_UserPermissionParameterType(
	uppt_name,
	uppt_type,
	uppt_description,
	uppt_user_permission_type_id
)VALUES(
	'experiment_permanent_id',
	'string',
	'the unique name of the experiment',
	GetUserPermissionTypeID('experiment_allowed')
);

INSERT INTO wl_UserPermissionParameterType(
	uppt_name,
	uppt_type,
	uppt_description,
	uppt_user_permission_type_id
)VALUES(
	'experiment_category_id',
	'string',
	'the unique name of the category of experiment',
	GetUserPermissionTypeID('experiment_allowed')
);


INSERT INTO wl_UserPermissionParameterType(
	uppt_name,
	uppt_type,
	uppt_description,
	uppt_user_permission_type_id
)VALUES(
	'time_allowed',
	'float',
	'Time allowed (in seconds)',
	GetUserPermissionTypeID('experiment_allowed')
);

DELIMITER $

CREATE FUNCTION GetGroupPermissionTypeID(name VARCHAR(255))
RETURNS INT
READS SQL DATA
BEGIN
	DECLARE variable INT;
	SELECT gpt_id INTO variable
		FROM wl_GroupPermissionType WHERE gpt_name = name;
	RETURN variable;
END$

DELIMITER ;

INSERT INTO wl_GroupPermissionType(
	gpt_name,
	gpt_description
)VALUES(
	'experiment_allowed',
	'This type has a parameter which is the permanent ID (not a INT) of an Experiment. Groups which have this permission will have access to the experiment defined in this parameter'
);

INSERT INTO wl_GroupPermissionParameterType(
	gppt_name,
	gppt_type,
	gppt_description,
	gppt_Group_permission_type_id
)VALUES(
	'experiment_permanent_id',
	'string',
	'the unique name of the experiment. The format is not defined',
	GetGroupPermissionTypeID('experiment_allowed')
);

INSERT INTO wl_GroupPermissionParameterType(
	gppt_name,
	gppt_type,
	gppt_description,
	gppt_Group_permission_type_id
)VALUES(
	'experiment_category_id',
	'string',
	'the unique name of the category of the experiment.',
	GetGroupPermissionTypeID('experiment_allowed')
);


INSERT INTO wl_GroupPermissionParameterType(
	gppt_name,
	gppt_type,
	gppt_description,
	gppt_Group_permission_type_id
)VALUES(
	'time_allowed',
	'float',
	'Time allowed to use the experiment, in seconds',
	GetGroupPermissionTypeID('experiment_allowed')
);


-- ------------------------------------------------------------------------------------
-- ------------------------------------------------------------------------------------
-- ------------------------------------------------------------------------------------
-- ---------------        P E R M I S S I O N S   O N   V I E W S       ---------------
-- ------------------------------------------------------------------------------------
-- ------------------------------------------------------------------------------------
-- ------------------------------------------------------------------------------------

-- ------------------------------------------------------------------------------------
-- ---------------------             STUDENT'S VIEWs             ----------------------
-- ------------------------------------------------------------------------------------

-- Users: wl_student_read@localhost, wl_student_write@localhost
-- Passwords: wl_student_read_password, wl_student_write_password

-- ------------------------------------
-- ----  USER AND GROUP DEFINITION ----
-- ------------------------------------

-- Read:

GRANT SELECT ON wl_v_s_Role 
	TO wl_student_read@localhost IDENTIFIED BY 'wl_student_read_password';

GRANT SELECT ON wl_v_s_User
	TO wl_student_read@localhost IDENTIFIED BY 'wl_student_read_password';

GRANT SELECT ON wl_v_s_Group
	TO wl_student_read@localhost IDENTIFIED BY 'wl_student_read_password';

-- Read for _write:

GRANT SELECT ON wl_v_s_Role 
	TO wl_student_write@localhost IDENTIFIED BY 'wl_student_write_password';

GRANT SELECT ON wl_v_s_User
	TO wl_student_write@localhost IDENTIFIED BY 'wl_student_write_password';

GRANT SELECT ON wl_v_s_Group
	TO wl_student_write@localhost IDENTIFIED BY 'wl_student_write_password';

-- Write:

GRANT UPDATE ON wl_v_s_rw_User
	TO wl_student_write@localhost IDENTIFIED BY 'wl_student_write_password';

-- --------------------------------------
-- ----  GROUP MEMBERSHIP DEFINITION ----
-- --------------------------------------

-- Read:

GRANT SELECT ON wl_v_s_UserIsMemberOf
	TO wl_student_read@localhost IDENTIFIED BY 'wl_student_read_password';

GRANT SELECT ON wl_v_s_GroupIsMemberOf
	TO wl_student_read@localhost IDENTIFIED BY 'wl_student_read_password';

-- Read for _write:

GRANT SELECT ON wl_v_s_UserIsMemberOf
	TO wl_student_write@localhost IDENTIFIED BY 'wl_student_write_password';

GRANT SELECT ON wl_v_s_GroupIsMemberOf
	TO wl_student_write@localhost IDENTIFIED BY 'wl_student_write_password';


-- ---------------------------------
-- ----  EXPERIMENTS DEFINITION ----
-- ---------------------------------

-- Read:

GRANT SELECT ON wl_v_s_ExperimentCategory
	TO wl_student_read@localhost IDENTIFIED BY 'wl_student_read_password';

GRANT SELECT ON wl_v_s_Experiment
	TO wl_student_read@localhost IDENTIFIED BY 'wl_student_read_password';

-- Read for _write:

GRANT SELECT ON wl_v_s_ExperimentCategory
	TO wl_student_write@localhost IDENTIFIED BY 'wl_student_write_password';

GRANT SELECT ON wl_v_s_Experiment
	TO wl_student_write@localhost IDENTIFIED BY 'wl_student_write_password';

-- ----------------------------------------------------
-- ----  EXPERIMENT INSTANCE MEMBERSHIP DEFINITION ----
-- ----------------------------------------------------

-- Read:

GRANT SELECT ON wl_v_s_UserUsedExperiment
	TO wl_student_read@localhost IDENTIFIED BY 'wl_student_read_password';

GRANT SELECT ON wl_v_s_UserCommand
	TO wl_student_read@localhost IDENTIFIED BY 'wl_student_read_password';

GRANT SELECT ON wl_v_s_UserFile
	TO wl_student_read@localhost IDENTIFIED BY 'wl_student_read_password';

-- Read for _write:

GRANT SELECT ON wl_v_s_UserUsedExperiment
	TO wl_student_write@localhost IDENTIFIED BY 'wl_student_write_password';

GRANT SELECT ON wl_v_s_UserCommand
	TO wl_student_write@localhost IDENTIFIED BY 'wl_student_write_password';

GRANT SELECT ON wl_v_s_UserFile
	TO wl_student_write@localhost IDENTIFIED BY 'wl_student_write_password';

-- Write:

GRANT INSERT ON wl_v_s_rw_insert_UserUsedExperiment 
	TO wl_student_write@localhost IDENTIFIED BY 'wl_student_write_password';

GRANT INSERT ON wl_v_s_rw_UserCommand
	TO wl_student_write@localhost IDENTIFIED BY 'wl_student_write_password';

GRANT INSERT ON wl_v_s_rw_UserFile
	TO wl_student_write@localhost IDENTIFIED BY 'wl_student_write_password';

-- ---------------------------
-- ----  USER PERMISSIONS ----
-- ---------------------------

-- Read:

GRANT SELECT ON wl_v_s_UserPermissionType
	TO wl_student_read@localhost IDENTIFIED BY 'wl_student_read_password';

GRANT SELECT ON wl_v_s_UserPermissionParameterType
	TO wl_student_read@localhost IDENTIFIED BY 'wl_student_read_password';

GRANT SELECT ON wl_v_s_UserPermissionInstance
	TO wl_student_read@localhost IDENTIFIED BY 'wl_student_read_password';

GRANT SELECT ON wl_v_s_UserPermissionParameter
	TO wl_student_read@localhost IDENTIFIED BY 'wl_student_read_password';

-- Read for _write:

GRANT SELECT ON wl_v_s_UserPermissionType
	TO wl_student_write@localhost IDENTIFIED BY 'wl_student_write_password';

GRANT SELECT ON wl_v_s_UserPermissionParameterType
	TO wl_student_write@localhost IDENTIFIED BY 'wl_student_write_password';

GRANT SELECT ON wl_v_s_UserPermissionInstance
	TO wl_student_write@localhost IDENTIFIED BY 'wl_student_write_password';

GRANT SELECT ON wl_v_s_UserPermissionParameter
	TO wl_student_write@localhost IDENTIFIED BY 'wl_student_write_password';

-- -----------------------------
-- ----  GROUP PERMISSIONS  ----
-- -----------------------------

-- Read:

GRANT SELECT ON wl_v_s_GroupPermissionType
	TO wl_student_read@localhost IDENTIFIED BY 'wl_student_read_password';

GRANT SELECT ON wl_v_s_GroupPermissionParameterType
	TO wl_student_read@localhost IDENTIFIED BY 'wl_student_read_password';

GRANT SELECT ON wl_v_s_GroupPermissionInstance
	TO wl_student_read@localhost IDENTIFIED BY 'wl_student_read_password';

GRANT SELECT ON wl_v_s_GroupPermissionParameter
	TO wl_student_read@localhost IDENTIFIED BY 'wl_student_read_password';

-- Read for _write:

GRANT SELECT ON wl_v_s_GroupPermissionType
	TO wl_student_write@localhost IDENTIFIED BY 'wl_student_write_password';

GRANT SELECT ON wl_v_s_GroupPermissionParameterType
	TO wl_student_write@localhost IDENTIFIED BY 'wl_student_write_password';

GRANT SELECT ON wl_v_s_GroupPermissionInstance
	TO wl_student_write@localhost IDENTIFIED BY 'wl_student_write_password';

GRANT SELECT ON wl_v_s_GroupPermissionParameter
	TO wl_student_write@localhost IDENTIFIED BY 'wl_student_write_password';

-- ------------------------------------------------------------------------------------
-- --------------------             PROFESOR'S VIEWs             ----------------------
-- ------------------------------------------------------------------------------------

-- Users: wl_prof_read@localhost, wl_prof_write@localhost
-- Passwords: wl_prof_read_password, wl_prof_write_password

-- ------------------------------------
-- ----  USER AND GROUP DEFINITION ----
-- ------------------------------------

-- Read:

GRANT SELECT ON wl_v_p_Role
	TO wl_prof_read@localhost IDENTIFIED BY 'wl_prof_read_password';

GRANT SELECT ON wl_v_p_User
	TO wl_prof_read@localhost IDENTIFIED BY 'wl_prof_read_password';

GRANT SELECT ON wl_v_p_Group
	TO wl_prof_read@localhost IDENTIFIED BY 'wl_prof_read_password';

-- Read for _write:

GRANT SELECT ON wl_v_p_Role
	TO wl_prof_write@localhost IDENTIFIED BY 'wl_prof_write_password';

GRANT SELECT ON wl_v_p_User
	TO wl_prof_write@localhost IDENTIFIED BY 'wl_prof_write_password';

GRANT SELECT ON wl_v_p_Group
	TO wl_prof_write@localhost IDENTIFIED BY 'wl_prof_write_password';

-- Write:

GRANT INSERT ON wl_v_p_rw_insert_User
	TO wl_prof_write@localhost IDENTIFIED BY 'wl_prof_write_password';

GRANT UPDATE ON wl_v_p_rw_update_User
	TO wl_prof_write@localhost IDENTIFIED BY 'wl_prof_write_password';

GRANT INSERT, UPDATE ON wl_v_p_rw_Group
	TO wl_prof_write@localhost IDENTIFIED BY 'wl_prof_write_password';

-- --------------------------------------
-- ----  GROUP MEMBERSHIP DEFINITION ----
-- --------------------------------------

-- Read:

GRANT SELECT ON wl_v_p_UserIsMemberOf
	TO wl_prof_read@localhost IDENTIFIED BY 'wl_prof_read_password';

GRANT SELECT ON wl_v_p_GroupIsMemberOf
	TO wl_prof_read@localhost IDENTIFIED BY 'wl_prof_read_password';

-- Read for _write:

GRANT SELECT ON wl_v_p_UserIsMemberOf
	TO wl_prof_write@localhost IDENTIFIED BY 'wl_prof_write_password';

GRANT SELECT ON wl_v_p_GroupIsMemberOf
	TO wl_prof_write@localhost IDENTIFIED BY 'wl_prof_write_password';

-- Write

GRANT INSERT ON wl_v_p_rw_UserIsMemberOf
	TO wl_prof_write@localhost IDENTIFIED BY 'wl_prof_write_password';

GRANT INSERT ON wl_v_p_rw_GroupIsMemberOf
	TO wl_prof_write@localhost IDENTIFIED BY 'wl_prof_write_password';

-- --------------------------------------------------
-- ----  EXPERIMENTS DEFINITION ----
-- --------------------------------------------------

-- Read:
GRANT SELECT ON wl_v_p_ExperimentCategory
	TO wl_prof_read@localhost IDENTIFIED BY 'wl_prof_read_password';

GRANT SELECT ON wl_v_p_Experiment
	TO wl_prof_read@localhost IDENTIFIED BY 'wl_prof_read_password';

-- Read for _write:
GRANT SELECT ON wl_v_p_ExperimentCategory
	TO wl_prof_write@localhost IDENTIFIED BY 'wl_prof_write_password';

GRANT SELECT ON wl_v_p_Experiment
	TO wl_prof_write@localhost IDENTIFIED BY 'wl_prof_write_password';

-- ----------------------------------------------------
-- ----  EXPERIMENT INSTANCE MEMBERSHIP DEFINITION ----
-- ----------------------------------------------------

-- Read:

GRANT SELECT ON wl_v_p_UserUsedExperiment
	TO wl_prof_read@localhost IDENTIFIED BY 'wl_prof_read_password';

GRANT SELECT ON wl_v_p_UserCommand
	TO wl_prof_read@localhost IDENTIFIED BY 'wl_prof_read_password';

GRANT SELECT ON wl_v_p_UserFile
	TO wl_prof_read@localhost IDENTIFIED BY 'wl_prof_read_password';

-- Read for _write:
GRANT SELECT ON wl_v_p_UserUsedExperiment
	TO wl_prof_write@localhost IDENTIFIED BY 'wl_prof_write_password';

GRANT SELECT ON wl_v_p_UserCommand
	TO wl_prof_write@localhost IDENTIFIED BY 'wl_prof_write_password';

GRANT SELECT ON wl_v_p_UserFile
	TO wl_prof_write@localhost IDENTIFIED BY 'wl_prof_write_password';

-- Write:
GRANT INSERT ON wl_v_p_rw_insert_UserUsedExperiment
	TO wl_prof_write@localhost IDENTIFIED BY 'wl_prof_write_password';

GRANT INSERT ON wl_v_p_rw_UserCommand
	TO wl_prof_write@localhost IDENTIFIED BY 'wl_prof_write_password';

GRANT INSERT ON wl_v_p_rw_UserFile
	TO wl_prof_write@localhost IDENTIFIED BY 'wl_prof_write_password';

-- ---------------------------
-- ----  USER PERMISSIONS ----
-- ---------------------------

-- Read:
GRANT SELECT ON wl_v_p_UserPermissionType
	TO wl_prof_read@localhost IDENTIFIED BY 'wl_prof_read_password';

GRANT SELECT ON wl_v_p_UserPermissionParameterType
	TO wl_prof_read@localhost IDENTIFIED BY 'wl_prof_read_password';

GRANT SELECT ON wl_v_p_UserPermissionInstance
	TO wl_prof_read@localhost IDENTIFIED BY 'wl_prof_read_password';

GRANT SELECT ON wl_v_p_UserPermissionParameter
	TO wl_prof_read@localhost IDENTIFIED BY 'wl_prof_read_password';

-- Read for _write:
GRANT SELECT ON wl_v_p_UserPermissionType
	TO wl_prof_write@localhost IDENTIFIED BY 'wl_prof_write_password';

GRANT SELECT ON wl_v_p_UserPermissionParameterType
	TO wl_prof_write@localhost IDENTIFIED BY 'wl_prof_write_password';

GRANT SELECT ON wl_v_p_UserPermissionInstance
	TO wl_prof_write@localhost IDENTIFIED BY 'wl_prof_write_password';

GRANT SELECT ON wl_v_p_UserPermissionParameter
	TO wl_prof_write@localhost IDENTIFIED BY 'wl_prof_write_password';

-- Write:
GRANT INSERT, UPDATE ON wl_v_p_rw_UserPermissionInstance
	TO wl_prof_write@localhost IDENTIFIED BY 'wl_prof_write_password';

GRANT UPDATE ON wl_v_p_rw_UserPermissionParameter
	TO wl_prof_write@localhost IDENTIFIED BY 'wl_prof_write_password';

-- -----------------------------
-- ----  GROUP PERMISSIONS  ----
-- -----------------------------

-- Read:

GRANT SELECT ON wl_v_p_GroupPermissionType
	TO wl_prof_read@localhost IDENTIFIED BY 'wl_prof_read_password';

GRANT SELECT ON wl_v_p_GroupPermissionParameterType
	TO wl_prof_read@localhost IDENTIFIED BY 'wl_prof_read_password';

GRANT SELECT ON wl_v_p_GroupPermissionInstance
	TO wl_prof_read@localhost IDENTIFIED BY 'wl_prof_read_password';

GRANT SELECT ON wl_v_p_GroupPermissionParameter
	TO wl_prof_read@localhost IDENTIFIED BY 'wl_prof_read_password';

-- Read for _write:

GRANT SELECT ON wl_v_p_GroupPermissionType
	TO wl_prof_write@localhost IDENTIFIED BY 'wl_prof_write_password';

GRANT SELECT ON wl_v_p_GroupPermissionParameterType
	TO wl_prof_write@localhost IDENTIFIED BY 'wl_prof_write_password';

GRANT SELECT ON wl_v_p_GroupPermissionInstance
	TO wl_prof_write@localhost IDENTIFIED BY 'wl_prof_write_password';

GRANT SELECT ON wl_v_p_GroupPermissionParameter
	TO wl_prof_write@localhost IDENTIFIED BY 'wl_prof_write_password';


-- Write:

GRANT INSERT, UPDATE ON wl_v_p_rw_GroupPermissionInstance
	TO wl_prof_write@localhost IDENTIFIED BY 'wl_prof_write_password';

GRANT UPDATE ON wl_v_p_rw_GroupPermissionParameter
	TO wl_prof_write@localhost IDENTIFIED BY 'wl_prof_write_password';

-- ------------------------------------------------------------------------------------
-- -----------------             EXTERNAL ENTITY'S VIEWs             ------------------
-- ------------------------------------------------------------------------------------

-- Users: wl_exter_read@localhost, wl_exter_write@localhost
-- Passwords: wl_exter_read_password, wl_exter_write_password

-- -------------------------------------
-- ----  USER AND GROUP DEFINITION  ----
-- -------------------------------------

-- Read

GRANT SELECT ON wl_v_e_User
	TO wl_exter_read@localhost IDENTIFIED BY 'wl_exter_read_password';

GRANT SELECT ON wl_v_e_ExternalEntity
	TO wl_exter_read@localhost IDENTIFIED BY 'wl_exter_read_password';

GRANT SELECT ON wl_v_e_Group
	TO wl_exter_read@localhost IDENTIFIED BY 'wl_exter_read_password';

-- Read for _write:
GRANT SELECT ON wl_v_e_User
	TO wl_exter_write@localhost IDENTIFIED BY 'wl_exter_write_password';

GRANT SELECT ON wl_v_e_ExternalEntity
	TO wl_exter_write@localhost IDENTIFIED BY 'wl_exter_write_password';

GRANT SELECT ON wl_v_e_Group
	TO wl_exter_write@localhost IDENTIFIED BY 'wl_exter_write_password';

-- Write

GRANT UPDATE ON wl_v_e_rw_ExternalEntity
	TO wl_exter_write@localhost IDENTIFIED BY 'wl_exter_write_password';

-- --------------------------------------
-- ----  GROUP MEMBERSHIP DEFINITION ----
-- --------------------------------------

-- Read

GRANT SELECT ON wl_v_e_GroupIsMemberOf
	TO wl_exter_read@localhost IDENTIFIED BY 'wl_exter_read_password';

GRANT SELECT ON wl_v_e_ExternalEntityIsMemberOf
	TO wl_exter_read@localhost IDENTIFIED BY 'wl_exter_read_password';

-- Read for _write:
GRANT SELECT ON wl_v_e_GroupIsMemberOf
	TO wl_exter_write@localhost IDENTIFIED BY 'wl_exter_write_password';

GRANT SELECT ON wl_v_e_ExternalEntityIsMemberOf
	TO wl_exter_write@localhost IDENTIFIED BY 'wl_exter_write_password';

-- ---------------------------------
-- ----  EXPERIMENTS DEFINITION ----
-- ---------------------------------

-- Read

GRANT SELECT ON wl_v_e_ExperimentCategory
	TO wl_exter_read@localhost IDENTIFIED BY 'wl_exter_read_password';

GRANT SELECT ON wl_v_e_Experiment
	TO wl_exter_read@localhost IDENTIFIED BY 'wl_exter_read_password';

-- Read for _write
GRANT SELECT ON wl_v_e_ExperimentCategory
	TO wl_exter_write@localhost IDENTIFIED BY 'wl_exter_write_password';

GRANT SELECT ON wl_v_e_Experiment
	TO wl_exter_write@localhost IDENTIFIED BY 'wl_exter_write_password';

-- ----------------------------------------------------
-- ----  EXPERIMENT INSTANCE MEMBERSHIP DEFINITION ----
-- ----------------------------------------------------


-- Read:

GRANT SELECT ON wl_v_e_ExternalEntityUsedExperiment
	TO wl_exter_read@localhost IDENTIFIED BY 'wl_exter_read_password';

GRANT SELECT ON wl_v_e_ExternalEntityCommand
	TO wl_exter_read@localhost IDENTIFIED BY 'wl_exter_read_password';

-- Read for _write:
GRANT SELECT ON wl_v_e_ExternalEntityUsedExperiment
	TO wl_exter_write@localhost IDENTIFIED BY 'wl_exter_write_password';

GRANT SELECT ON wl_v_e_ExternalEntityCommand
	TO wl_exter_write@localhost IDENTIFIED BY 'wl_exter_write_password';

-- Write:

GRANT INSERT ON wl_v_e_rw_insert_ExternalEntityUsedExperiment
	TO wl_exter_write@localhost IDENTIFIED BY 'wl_exter_write_password';

GRANT UPDATE ON wl_v_e_rw_update_ExternalEntityUsedExperiment
	TO wl_exter_write@localhost IDENTIFIED BY 'wl_exter_write_password';

GRANT INSERT ON wl_v_e_rw_ExternalEntityCommand
	TO wl_exter_write@localhost IDENTIFIED BY 'wl_exter_write_password';

-- ----------------------------
-- ----  GROUP PERMISSIONS ----
-- ----------------------------

-- Read

GRANT SELECT ON wl_v_e_GroupPermissionType
	TO wl_exter_read@localhost IDENTIFIED BY 'wl_exter_read_password';

GRANT SELECT ON wl_v_e_GroupPermissionParameterType
	TO wl_exter_read@localhost IDENTIFIED BY 'wl_exter_read_password';

GRANT SELECT ON wl_v_e_GroupPermissionInstance
	TO wl_exter_read@localhost IDENTIFIED BY 'wl_exter_read_password';

GRANT SELECT ON wl_v_e_GroupPermissionParameter
	TO wl_exter_read@localhost IDENTIFIED BY 'wl_exter_read_password';

-- Read for _write:
GRANT SELECT ON wl_v_e_GroupPermissionType
	TO wl_exter_write@localhost IDENTIFIED BY 'wl_exter_write_password';

GRANT SELECT ON wl_v_e_GroupPermissionParameterType
	TO wl_exter_write@localhost IDENTIFIED BY 'wl_exter_write_password';

GRANT SELECT ON wl_v_e_GroupPermissionInstance
	TO wl_exter_write@localhost IDENTIFIED BY 'wl_exter_write_password';

GRANT SELECT ON wl_v_e_GroupPermissionParameter
	TO wl_exter_write@localhost IDENTIFIED BY 'wl_exter_write_password';

-- ----------------------------------------
-- ----  EXTERNAL ENTITIES PERMISSIONS ----
-- ----------------------------------------

-- Read:

GRANT SELECT ON wl_v_e_ExternalEntityPermissionType
	TO wl_exter_read@localhost IDENTIFIED BY 'wl_exter_read_password';

GRANT SELECT ON wl_v_e_ExternalEntityPermissionParameterType
	TO wl_exter_read@localhost IDENTIFIED BY 'wl_exter_read_password';

GRANT SELECT ON wl_v_e_ExternalEntityPermissionInstance
	TO wl_exter_read@localhost IDENTIFIED BY 'wl_exter_read_password';

GRANT SELECT ON wl_v_e_ExternalEntityPermissionParameter
	TO wl_exter_read@localhost IDENTIFIED BY 'wl_exter_read_password';

-- Read for _write:
GRANT SELECT ON wl_v_e_ExternalEntityPermissionType
	TO wl_exter_write@localhost IDENTIFIED BY 'wl_exter_write_password';

GRANT SELECT ON wl_v_e_ExternalEntityPermissionParameterType
	TO wl_exter_write@localhost IDENTIFIED BY 'wl_exter_write_password';

GRANT SELECT ON wl_v_e_ExternalEntityPermissionInstance
	TO wl_exter_write@localhost IDENTIFIED BY 'wl_exter_write_password';

GRANT SELECT ON wl_v_e_ExternalEntityPermissionParameter
	TO wl_exter_write@localhost IDENTIFIED BY 'wl_exter_write_password';


-- ------------------------------------------------------------------------------------
-- ------------------             ADMINISTRATOR'S VIEWs             -------------------
-- ------------------------------------------------------------------------------------

-- Users: wl_admin_read@localhost, wl_admin_write@localhost
-- Passwords: wl_admin_read_password, wl_admin_write_password

-- ------------------------------------
-- ---- USER AND GROUP DEFINITION  ----
-- ------------------------------------

-- Read

GRANT SELECT ON wl_v_a_Role
	TO wl_admin_read@localhost IDENTIFIED BY 'wl_admin_read_password';

GRANT SELECT ON wl_v_a_User
	TO wl_admin_read@localhost IDENTIFIED BY 'wl_admin_read_password';

GRANT SELECT ON wl_v_a_UserAuth
	TO wl_admin_read@localhost IDENTIFIED BY 'wl_admin_read_password';

GRANT SELECT ON wl_v_a_UserAuthInstance
	TO wl_admin_read@localhost IDENTIFIED BY 'wl_admin_read_password';

GRANT SELECT ON wl_v_a_UserAuthUserRelation
	TO wl_admin_read@localhost IDENTIFIED BY 'wl_admin_read_password';

GRANT SELECT ON wl_v_a_ExternalEntity
	TO wl_admin_read@localhost IDENTIFIED BY 'wl_admin_read_password';

GRANT SELECT ON wl_v_a_Group
	TO wl_admin_read@localhost IDENTIFIED BY 'wl_admin_read_password';

-- Read for _write:

GRANT SELECT ON wl_v_a_Role
	TO wl_admin_write@localhost IDENTIFIED BY 'wl_admin_write_password';

GRANT SELECT ON wl_v_a_User
	TO wl_admin_write@localhost IDENTIFIED BY 'wl_admin_write_password';

GRANT SELECT ON wl_v_a_UserAuth
	TO wl_admin_write@localhost IDENTIFIED BY 'wl_admin_write_password';

GRANT SELECT ON wl_v_a_UserAuthInstance
	TO wl_admin_write@localhost IDENTIFIED BY 'wl_admin_write_password';

GRANT SELECT ON wl_v_a_UserAuthUserRelation
	TO wl_admin_write@localhost IDENTIFIED BY 'wl_admin_write_password';

GRANT SELECT ON wl_v_a_ExternalEntity
	TO wl_admin_write@localhost IDENTIFIED BY 'wl_admin_write_password';

GRANT SELECT ON wl_v_a_Group
	TO wl_admin_write@localhost IDENTIFIED BY 'wl_admin_write_password';

-- Write

GRANT INSERT, UPDATE ON wl_v_a_rw_User
	TO wl_admin_write@localhost IDENTIFIED BY 'wl_admin_write_password';

GRANT INSERT, UPDATE ON wl_v_a_rw_ExternalEntity
	TO wl_admin_write@localhost IDENTIFIED BY 'wl_admin_write_password';

GRANT INSERT, UPDATE ON wl_v_a_rw_Group
	TO wl_admin_write@localhost IDENTIFIED BY 'wl_admin_write_password';

GRANT INSERT, UPDATE ON wl_v_a_rw_UserAuthInstance
	TO wl_admin_write@localhost IDENTIFIED BY 'wl_admin_write_password';

GRANT INSERT, UPDATE ON wl_v_a_rw_UserAuthUserRelation
	TO wl_admin_write@localhost IDENTIFIED BY 'wl_admin_write_password';


-- --------------------------------------
-- ----  GROUP MEMBERSHIP DEFINITION ----
-- --------------------------------------

-- Read

GRANT SELECT ON wl_v_a_UserIsMemberOf
	TO wl_admin_read@localhost IDENTIFIED BY 'wl_admin_read_password';

GRANT SELECT ON wl_v_a_GroupIsMemberOf
	TO wl_admin_read@localhost IDENTIFIED BY 'wl_admin_read_password';

GRANT SELECT ON wl_v_a_ExternalEntityIsMemberOf
	TO wl_admin_read@localhost IDENTIFIED BY 'wl_admin_read_password';

-- Read for _write:

GRANT SELECT ON wl_v_a_UserIsMemberOf
	TO wl_admin_write@localhost IDENTIFIED BY 'wl_admin_write_password';

GRANT SELECT ON wl_v_a_GroupIsMemberOf
	TO wl_admin_write@localhost IDENTIFIED BY 'wl_admin_write_password';

GRANT SELECT ON wl_v_a_ExternalEntityIsMemberOf
	TO wl_admin_write@localhost IDENTIFIED BY 'wl_admin_write_password';


-- Write

GRANT INSERT ON wl_v_a_rw_UserIsMemberOf
	TO wl_admin_write@localhost IDENTIFIED BY 'wl_admin_write_password';

GRANT INSERT ON wl_v_a_rw_GroupIsMemberOf
	TO wl_admin_write@localhost IDENTIFIED BY 'wl_admin_write_password';

GRANT INSERT ON wl_v_a_rw_ExternalEntityIsMemberOf
	TO wl_admin_write@localhost IDENTIFIED BY 'wl_admin_write_password';

-- --------------------------------------
-- ----  GROUP MEMBERSHIP DEFINITION ----
-- --------------------------------------

-- Read
GRANT SELECT ON wl_v_a_ExperimentCategory
	TO wl_admin_read@localhost IDENTIFIED BY 'wl_admin_read_password';

GRANT SELECT ON wl_v_a_Experiment
	TO wl_admin_read@localhost IDENTIFIED BY 'wl_admin_read_password';

-- Read for _write:

GRANT SELECT ON wl_v_a_ExperimentCategory
	TO wl_admin_write@localhost IDENTIFIED BY 'wl_admin_write_password';

GRANT SELECT ON wl_v_a_Experiment
	TO wl_admin_write@localhost IDENTIFIED BY 'wl_admin_write_password';

-- Write
GRANT INSERT, UPDATE ON wl_v_a_rw_ExperimentCategory
	TO wl_admin_write@localhost IDENTIFIED BY 'wl_admin_write_password';

GRANT INSERT, UPDATE ON wl_v_a_rw_Experiment
	TO wl_admin_write@localhost IDENTIFIED BY 'wl_admin_write_password';

-- ----------------------------------------------------
-- ----  EXPERIMENT INSTANCE MEMBERSHIP DEFINITION ----
-- ----------------------------------------------------

-- Read

GRANT SELECT ON wl_v_a_UserUsedExperiment
	TO wl_admin_read@localhost IDENTIFIED BY 'wl_admin_read_password';

GRANT SELECT ON wl_v_a_UserCommand
	TO wl_admin_read@localhost IDENTIFIED BY 'wl_admin_read_password';

GRANT SELECT ON wl_v_a_UserFile
	TO wl_admin_read@localhost IDENTIFIED BY 'wl_admin_read_password';

GRANT SELECT ON wl_v_a_ExternalEntityUsedExperiment
	TO wl_admin_read@localhost IDENTIFIED BY 'wl_admin_read_password';

GRANT SELECT ON wl_v_a_ExternalEntityCommand
	TO wl_admin_read@localhost IDENTIFIED BY 'wl_admin_read_password';

-- Read for _write:
GRANT SELECT ON wl_v_a_UserUsedExperiment
	TO wl_admin_write@localhost IDENTIFIED BY 'wl_admin_write_password';

GRANT SELECT ON wl_v_a_UserCommand
	TO wl_admin_write@localhost IDENTIFIED BY 'wl_admin_write_password';

GRANT SELECT ON wl_v_a_UserFile
	TO wl_admin_write@localhost IDENTIFIED BY 'wl_admin_write_password';

GRANT SELECT ON wl_v_a_ExternalEntityUsedExperiment
	TO wl_admin_write@localhost IDENTIFIED BY 'wl_admin_write_password';

GRANT SELECT ON wl_v_a_ExternalEntityCommand
	TO wl_admin_write@localhost IDENTIFIED BY 'wl_admin_write_password';

-- Write

GRANT INSERT ON wl_v_a_rw_insert_UserUsedExperiment
	TO wl_admin_write@localhost IDENTIFIED BY 'wl_admin_write_password';

GRANT INSERT ON wl_v_a_rw_UserCommand
	TO wl_admin_write@localhost IDENTIFIED BY 'wl_admin_write_password';

GRANT INSERT ON wl_v_a_rw_UserFile
	TO wl_admin_write@localhost IDENTIFIED BY 'wl_admin_write_password';

-- ----------------------------
-- ----  USER PERMISSIONS  ----
-- ----------------------------

-- Read

GRANT SELECT ON wl_v_a_UserPermissionType
	TO wl_admin_read@localhost IDENTIFIED BY 'wl_admin_read_password';

GRANT SELECT ON wl_v_a_UserPermissionParameterType
	TO wl_admin_read@localhost IDENTIFIED BY 'wl_admin_read_password';

GRANT SELECT ON wl_v_a_UserPermissionInstance
	TO wl_admin_read@localhost IDENTIFIED BY 'wl_admin_read_password';

GRANT SELECT ON wl_v_a_UserPermissionParameter
	TO wl_admin_read@localhost IDENTIFIED BY 'wl_admin_read_password';

-- Read for _write:

GRANT SELECT ON wl_v_a_UserPermissionType
	TO wl_admin_write@localhost IDENTIFIED BY 'wl_admin_write_password';

GRANT SELECT ON wl_v_a_UserPermissionParameterType
	TO wl_admin_write@localhost IDENTIFIED BY 'wl_admin_write_password';

GRANT SELECT ON wl_v_a_UserPermissionInstance
	TO wl_admin_write@localhost IDENTIFIED BY 'wl_admin_write_password';

GRANT SELECT ON wl_v_a_UserPermissionParameter
	TO wl_admin_write@localhost IDENTIFIED BY 'wl_admin_write_password';

-- Write

GRANT INSERT, UPDATE ON wl_v_a_rw_UserPermissionInstance
	TO wl_admin_write@localhost IDENTIFIED BY 'wl_admin_write_password';

GRANT UPDATE ON wl_v_a_rw_UserPermissionParameter
	TO wl_admin_write@localhost IDENTIFIED BY 'wl_admin_write_password';

-- ----------------------------
-- ----  GROUP PERMISSIONS  ---
-- ----------------------------

-- Read

GRANT SELECT ON wl_v_a_GroupPermissionType
	TO wl_admin_read@localhost IDENTIFIED BY 'wl_admin_read_password';

GRANT SELECT ON wl_v_a_GroupPermissionParameterType
	TO wl_admin_read@localhost IDENTIFIED BY 'wl_admin_read_password';

GRANT SELECT ON wl_v_a_GroupPermissionInstance
	TO wl_admin_read@localhost IDENTIFIED BY 'wl_admin_read_password';

GRANT SELECT ON wl_v_a_GroupPermissionParameter
	TO wl_admin_read@localhost IDENTIFIED BY 'wl_admin_read_password';

-- Read for _write

GRANT SELECT ON wl_v_a_GroupPermissionType
	TO wl_admin_write@localhost IDENTIFIED BY 'wl_admin_write_password';

GRANT SELECT ON wl_v_a_GroupPermissionParameterType
	TO wl_admin_write@localhost IDENTIFIED BY 'wl_admin_write_password';

GRANT SELECT ON wl_v_a_GroupPermissionInstance
	TO wl_admin_write@localhost IDENTIFIED BY 'wl_admin_write_password';

GRANT SELECT ON wl_v_a_GroupPermissionParameter
	TO wl_admin_write@localhost IDENTIFIED BY 'wl_admin_write_password';

-- Write

GRANT INSERT, UPDATE ON wl_v_a_rw_GroupPermissionInstance
	TO wl_admin_write@localhost IDENTIFIED BY 'wl_admin_write_password';

GRANT UPDATE ON wl_v_a_rw_GroupPermissionParameter
	TO wl_admin_write@localhost IDENTIFIED BY 'wl_admin_write_password';

-- ---------------------------------------
-- ----  EXTERNAL ENTITY PERMISSIONS  ----
-- ---------------------------------------

-- Read

GRANT SELECT ON wl_v_a_ExternalEntityPermissionType
	TO wl_admin_read@localhost IDENTIFIED BY 'wl_admin_read_password';

GRANT SELECT ON wl_v_a_ExternalEntityPermissionParameterType
	TO wl_admin_read@localhost IDENTIFIED BY 'wl_admin_read_password';

GRANT SELECT ON wl_v_a_ExternalEntityPermissionInstance
	TO wl_admin_read@localhost IDENTIFIED BY 'wl_admin_read_password';

GRANT SELECT ON wl_v_a_ExternalEntityPermissionParameter
	TO wl_admin_read@localhost IDENTIFIED BY 'wl_admin_read_password';

-- Read for _write:

GRANT SELECT ON wl_v_a_ExternalEntityPermissionType
	TO wl_admin_write@localhost IDENTIFIED BY 'wl_admin_write_password';

GRANT SELECT ON wl_v_a_ExternalEntityPermissionParameterType
	TO wl_admin_write@localhost IDENTIFIED BY 'wl_admin_write_password';

GRANT SELECT ON wl_v_a_ExternalEntityPermissionInstance
	TO wl_admin_write@localhost IDENTIFIED BY 'wl_admin_write_password';

GRANT SELECT ON wl_v_a_ExternalEntityPermissionParameter
	TO wl_admin_write@localhost IDENTIFIED BY 'wl_admin_write_password';


-- Write

GRANT INSERT, UPDATE ON wl_v_a_rw_ExternalEntityPermissionInstance
	TO wl_admin_write@localhost IDENTIFIED BY 'wl_admin_write_password';

GRANT UPDATE ON wl_v_a_rw_ExternalEntityPermissionParameter
	TO wl_admin_write@localhost IDENTIFIED BY 'wl_admin_write_password';

-- ------------------------------------------------------------------------------------
-- ---------------------             AUTH'S VIEWs             -------------------------
-- ------------------------------------------------------------------------------------

-- Users: wl_auth_read@localhost
-- Passwords: wl_auth_read_password

-- ------------------------------------
-- ---- USER AND GROUP DEFINITION  ----
-- ------------------------------------

GRANT SELECT ON wl_v_auth_Role
	TO wl_auth_read@localhost IDENTIFIED BY 'wl_auth_read_password';

GRANT SELECT ON wl_v_auth_User
	TO wl_auth_read@localhost IDENTIFIED BY 'wl_auth_read_password';

GRANT SELECT ON wl_v_auth_UserAuth
	TO wl_auth_read@localhost IDENTIFIED BY 'wl_auth_read_password';

GRANT SELECT ON wl_v_auth_UserAuthInstance
	TO wl_auth_read@localhost IDENTIFIED BY 'wl_auth_read_password';

GRANT SELECT ON wl_v_auth_UserAuthUserRelation
	TO wl_auth_read@localhost IDENTIFIED BY 'wl_auth_read_password';


