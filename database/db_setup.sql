create database if not exists routegen;
use routegen;

create table if not exists airport(
	a_name varchar(128),
    a_city varchar(64),
    a_country varchar(64),
    a_iata char(3),
    a_icao char(4) primary key,
    a_lat double,
    a_long double,
    a_alt smallint,
    a_timezone float,
    a_dst char(1), 
    a_rwy int
);

create table if not exists airline(
    l_name varchar(128),
    l_alias varchar(32),
    l_iata char(2),
    l_icao char(3) primary key,
    l_call varchar(32),
    l_country varchar(64),
    l_active boolean
);

create table if not exists plane(
	p_icao char(4),
    p_iata char(3),
    p_name varchar(75),
    primary key(p_icao, p_iata)
);

create table if not exists route(
	routeID int primary key,
	r_airline char(3),
    r_dep char(4),
    r_arr char(4),
    r_plane char(3),
    r_dist int
);

