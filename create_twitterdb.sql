CREATE SCHEMA `twitterdb` ;
USE `twitterdb` ;
CREATE TABLE `tb_seed_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `fbid` varchar(45) DEFAULT NULL,
  `name` varchar(120) DEFAULT NULL,
  `mobileoremail` varchar(80) DEFAULT NULL,
  `Origin` varchar(50) DEFAULT NULL,
  `publishedtime` datetime DEFAULT NULL,
  `hasTasked` int(11) DEFAULT NULL,
  `taskedTime` datetime DEFAULT NULL,
  `Description` varchar(1024) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

CREATE TABLE `tb_task_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `fbid` varchar(45) NOT NULL,
  `Tasktype` varchar(50) NOT NULL DEFAULT 'Twitter.userInfo',
  `originalfbid` varchar(45) DEFAULT NULL,
  `priority` int(11) NOT NULL DEFAULT '0',
  `FbDescription` varchar(500) DEFAULT NULL,
  `dispatchTime` varchar(45) DEFAULT NULL,
  `Spider` varchar(50) DEFAULT NULL,
  `runningState` int(11) NOT NULL DEFAULT '0',
  `completedTime` datetime DEFAULT NULL,
  `Description` varchar(500) DEFAULT NULL,
  `deep` int(11) NOT NULL DEFAULT '0',
  `name` varchar(120) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

CREATE TABLE `tb_user_friends` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `fbid` varchar(45) NOT NULL,
  `name` varchar(120) DEFAULT NULL,
  `Homepage` varchar(128) DEFAULT NULL,
  `priority` int(11) DEFAULT NULL,
  `crawledTime` datetime DEFAULT NULL,
  `hasTasked` int(11) DEFAULT NULL,
  `taskedTime` datetime DEFAULT NULL,
  `Description` varchar(1024) DEFAULT NULL,
  `deep` int(11) DEFAULT NULL,
  `originalfbid` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `fbid_UNIQUE` (`fbid`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;