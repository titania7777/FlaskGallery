DROP DATABASE IF EXISTS `gallery`;
CREATE DATABASE `gallery`;

USE `gallery`;

DROP TABLE IF EXISTS `users`;
CREATE TABLE `users`(
    `root` BOOL NOT NULL,
    `email` VARCHAR(128) NOT NULL PRIMARY KEY,
    `password` VARCHAR(128) NOT NULL,
    `created` DATETIME DEFAULT NOW())CHARSET=utf8;

DROP TABLE IF EXISTS `post_gallery`;
CREATE TABLE `post_gallery`(
    `pgid` INT(40) NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `title` VARCHAR(255) NOT NULL,
    `image` VARCHAR(255) NOT NULL,
    `created` DATETIME DEFAULT NOW(),
    `updated` DATETIME NOT NULL)CHARSET=utf8;

DROP TABLE IF EXISTS `post_board`;
CREATE TABLE `post_board`(
    `pbid` INT(40) NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `email` VARCHAR(128) NOT NULL,
    `title` VARCHAR(50) NOT NULL,
    `content` VARCHAR(255) NOT NULL,
    `created` DATETIME DEFAULT NOW(),
    `updated` DATETIME NOT NULL,
    `hidden` BOOL NOT NULL,
    FOREIGN KEY (email) REFERENCES users (email) ON DELETE CASCADE
)CHARSET=utf8;

DROP TABLE IF EXISTS `post_board_sub`;
CREATE TABLE `post_board_sub`(
    `pbsid` INT(10) NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `pbid` INT(40) NOT NULL,
    `content` VARCHAR(100) NOT NULL,
    `created` DATETIME DEFAULT NOW(),
    `updated` DATETIME NOT NULL,
    FOREIGN KEY (pbid) REFERENCES post_board (pbid) ON DELETE CASCADE
)CHARSET=utf8;