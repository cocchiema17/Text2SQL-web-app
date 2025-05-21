-- File per la creazione automatica del database e delle tabelle

create database if not exists movie_catalog;

use movie_catalog;

create table if not exists directors (
    id int auto_increment primary key,
    nome varchar(255) not null unique,
    eta int not null
);

create table if not exists platforms (
    id int auto_increment primary key,
    nome varchar(255) not null unique
);

create table if not exists movies (
    id int auto_increment primary key,
    titolo varchar(255) not null unique,
    anno int not null,
    genere varchar(255) not null,
    id_director int not null,
    id_platform1 int,
    id_platform2 int,
    foreign key (id_director) references directors(id),
    foreign key (id_platform1) references platforms(id),
    foreign key (id_platform2) references platforms(id)
);