DROP TABLE IF EXISTS `#__weblab`;

CREATE TABLE IF NOT EXISTS `#__weblab` (
  `gid` int(10) NOT NULL,
  `exp_name` varchar(200) NOT NULL,
  `cat_name` varchar(50) NOT NULL,
  PRIMARY KEY (`gid`,`exp_name`,`cat_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `#__weblab_config`;

CREATE TABLE IF NOT EXISTS `#__weblab_config` (
  `host` varchar(100) NOT NULL,
  `user` varchar(100) NOT NULL,
  `password` varchar(100) NOT NULL,
  PRIMARY KEY (`host`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT INTO `#__weblab_config` (`host`, `user`, `password`) VALUES
('http://www.weblab.deusto.es/weblab/', 'joomla', 'joomlajoomla');