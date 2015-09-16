-- 
-- $ mysql -uroot -p
-- mysql> CREATE DATABASE phplab DEFAULT CHARSET 'utf8';
-- Query OK, 1 row affected (0.00 sec)
-- mysql> GRANT ALL ON phplab.* TO 'phplab'@'localhost' IDENTIFIED BY 'phplab';
-- Query OK, 0 rows affected (0.00 sec)
-- mysql> FLUSH PRIVILEGES;
-- Query OK, 0 rows affected (0.00 sec)
-- 
-- $ mysql -uphplab -p phplab < initial.sql 
-- 
CREATE TABLE WebLabSessions (
    session_id VARCHAR(50) PRIMARY KEY,
    back VARCHAR(300),
    last_poll DATETIME,
    max_date DATETIME,
    username VARCHAR(50)
) ENGINE = InnoDB;

CREATE TABLE WebLabExpiredSessions (
    session_id VARCHAR(50) PRIMARY KEY,
    back VARCHAR(300),
    expired DATETIME
) ENGINE = InnoDB;
