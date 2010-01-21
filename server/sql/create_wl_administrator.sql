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

-- DROP USER 'wl_administrator'@'localhost';

CREATE USER 'wl_administrator'@'localhost' IDENTIFIED BY 'wl_administrator_password';
GRANT SUPER ON *.* TO 'wl_administrator'@'localhost' IDENTIFIED BY 'wl_administrator_password' WITH GRANT OPTION;
GRANT INSERT,UPDATE ON mysql.* TO 'wl_administrator'@'localhost' IDENTIFIED BY 'wl_administrator_password';
GRANT ALL PRIVILEGES ON WebLab.* TO 'wl_administrator'@'localhost' IDENTIFIED BY 'wl_administrator_password';
GRANT ALL PRIVILEGES ON WebLabSessions.* TO 'wl_administrator'@'localhost' IDENTIFIED BY 'wl_administrator_password';
GRANT ALL PRIVILEGES ON WebLabCoordination.* TO 'wl_administrator'@'localhost' IDENTIFIED BY 'wl_administrator_password';
