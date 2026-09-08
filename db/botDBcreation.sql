drop database listBot;

create database listBot;

use listBot;

create table lists(id int auto_increment primary key, property bigint, creationDate datetime, name varchar(30));

create table listElements(id int auto_increment primary key, listid int, name varchar(100), done bool, assignee bigint);