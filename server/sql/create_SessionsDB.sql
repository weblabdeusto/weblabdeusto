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
-- $ mysql -uroot -p < createSessDB_MySQL.sql
--

-- In order to be able to process petitions using different servers,
-- the shared session should be stored in a common database. Since this
-- database is completely independent of the other databases, we separate
-- it in other file. It's important to mark this independence, since the
-- database could be deployed in other MySQL servers. 

-- The structure is very simple, it should be replicated so that different
-- server profiles have different permissions. For example, if there are 
-- "Database servers" and "User Processing Servers", this structure should
-- be replicated twice (so user processing servers can not access sessions
-- of database servers)

-- Here speed is important and there is no need of foreign key use. So
-- we will use MyISAM instead of InnoDB. Unfortunately, we can't use Memory 
-- because neither BLOB or TEXT would be supported (we must provide a fixed
-- size session value instead), and at this point we don't really know what
-- is the session size (or even if we will ever know about it).

-- TODO: If the application fails to remove the sessions that are here,
-- the sessions will be stored here "forever". Maybe some kind of trigger
-- or so Garbage Collecting the SESSIONS which have not been accessed in 
-- a lot of time could be interesting.

DROP DATABASE IF EXISTS `WebLabSessions`;
CREATE DATABASE `WebLabSessions` ;

use `WebLabSessions`;

-- -------------------------------------------------------------------------
-- --------------             DATABASE SESSION            ------------------
-- -------------------------------------------------------------------------

CREATE TABLE wl_DbSessions (
	session_id		CHAR( 100 ) NOT NULL PRIMARY KEY,
    session_pool_id CHAR( 100 ) NOT NULL,
	start_date		DATETIME	NOT NULL,
	latest_change	DATETIME,
	latest_access	DATETIME,
    session_obj    	BLOB        NOT NULL,
	session_locked  DATETIME
) ENGINE = InnoDB;

DELIMITER $

CREATE FUNCTION wl_CreateSession(sess_id CHAR( 100 ), session_pool_id CHAR( 100 ), sess_obj BLOB) RETURNS INT READS SQL DATA
BEGIN
	DECLARE lock_status INT;
	DECLARE already_there CHAR( 100 ) DEFAULT '';
	DECLARE ret_value INT DEFAULT 2;
	DECLARE now_v DATETIME;
	DECLARE CONTINUE HANDLER FOR SQLSTATE '02000' SET already_there = '';


	SELECT GET_LOCK('wl_lock',10) INTO lock_status;
	IF lock_status = 0 THEN
		RETURN -1; -- lock timeout!
	END IF;


    SELECT '' INTO already_there;

	SELECT session_id INTO already_there 
                FROM wl_DbSessions WHERE session_id = sess_id;
	
	IF already_there = sess_id THEN
		SELECT 1 INTO ret_value;
	ELSE
		SELECT NOW() INTO now_v;
		INSERT INTO wl_DbSessions(session_id, session_pool_id, start_date,latest_change,latest_access, session_obj, session_locked) VALUES(sess_id,session_pool_id,now_v,now_v,now_v,sess_obj, NULL);
		SELECT 0 INTO ret_value;
	END IF;

	SELECT RELEASE_LOCK('wl_lock') INTO lock_status;
	IF lock_status IS NULL  THEN
		RETURN -2; -- lock timeout!
	END IF;

	RETURN ret_value;
END$

CREATE FUNCTION wl_LockSession(sess_id CHAR( 100 ) ) RETURNS INT READS SQL DATA
BEGIN
	-- Locks the lock_session
	-- If it can lock the session, it returns 0
	-- If it can't because it's already locked, it returns 1
	-- Low-level errors return codes < 0
	DECLARE lock_status INT;
	DECLARE session_locked_size INT DEFAULT -1;
	DECLARE v_session_locked DATETIME;
	DECLARE return_value INT DEFAULT -4;

	SELECT GET_LOCK('wl_lock',10) INTO lock_status;
	IF lock_status = 0 THEN
		RETURN -1; -- lock timeout!
	END IF;

	-- <Critical region>

	SELECT COUNT(session_id) INTO session_locked_size FROM wl_DbSessions WHERE session_id = sess_id;

	IF session_locked_size = 0 THEN
		SELECT -3 INTO return_value;
	ELSE
		SELECT session_locked INTO v_session_locked FROM wl_DbSessions WHERE session_id = sess_id;

		IF v_session_locked IS NULL THEN
			UPDATE wl_DbSessions SET session_locked = NOW() WHERE session_id = sess_id;
			SELECT 0 INTO return_value;
		ELSE 
			IF (UNIX_TIMESTAMP(NOW()) - UNIX_TIMESTAMP(v_session_locked)) > 100 THEN
		       		-- Max time: 100 seconds
				UPDATE wl_DbSessions SET session_locked = NOW() WHERE session_id = sess_id;
				SELECT 0 INTO return_value;
			ELSE
				SELECT 1 INTO return_value;
			END IF;
		END IF;
	END IF;

	-- </Critical region>

	SELECT RELEASE_LOCK('wl_lock') INTO lock_status;
	IF lock_status IS NULL THEN
		RETURN -2; -- Couldn't release lock
	END IF;

	RETURN return_value;
END$

CREATE FUNCTION wl_UnlockSession(sess_id CHAR( 100 )) RETURNS INT READS SQL DATA
BEGIN
	DECLARE lock_status INT;
	DECLARE return_value INT DEFAULT -4;
	DECLARE session_locked_size INT DEFAULT -1;

	SELECT GET_LOCK('wl_lock',10) INTO lock_status;
	IF lock_status = 0 THEN
		RETURN -1; -- lock timeout!
	END IF;

	-- <Critical Region>
	
	SELECT COUNT(session_id) INTO session_locked_size FROM wl_DbSessions WHERE session_id = sess_id;
	IF session_locked_size = 0 THEN
		SELECT -3 INTO return_value;
	ELSE	
		UPDATE wl_DbSessions SET session_locked = NULL WHERE session_id = sess_id;
		SELECT 0 INTO return_value;
	END IF;
	-- </Critical Region>

	SELECT RELEASE_LOCK('wl_lock') INTO lock_status;
	IF lock_status IS NULL THEN
		RETURN -2; -- Couldn't release lock
	END IF;

	RETURN return_value;
END$

CREATE TRIGGER wl_t_SessionAccessed
BEFORE UPDATE ON wl_DbSessions
FOR EACH ROW BEGIN
	SET NEW.latest_change = NOW();
	SET NEW.latest_access = NOW();
END$

CREATE VIEW wl_rw_DbSessions
AS SELECT
--      *
	session_id,
	latest_access,
	session_obj
FROM wl_DbSessions;

GRANT SELECT, UPDATE, DELETE ON wl_DbSessions
 	TO wl_session_user@localhost IDENTIFIED BY 'wl_session_user_password';

GRANT SELECT, UPDATE, DELETE ON wl_rw_DbSessions
 	TO wl_session_user@localhost IDENTIFIED BY 'wl_session_user_password';

GRANT EXECUTE ON FUNCTION wl_CreateSession
 	TO wl_session_user@localhost IDENTIFIED BY 'wl_session_user_password';

GRANT EXECUTE ON FUNCTION wl_LockSession
 	TO wl_session_user@localhost IDENTIFIED BY 'wl_session_user_password';

GRANT EXECUTE ON FUNCTION wl_UnlockSession
 	TO wl_session_user@localhost IDENTIFIED BY 'wl_session_user_password';

