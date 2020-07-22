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
    a_dst char(1)
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

create table if not exists airplane(
	p_icao char(4) primary key,
    p_iata char(3),
    p_name varchar(75)
);

/*create table if not exists airplane(
    p_name varchar(74),
    p_iata char(3),
    p_icao char(4) primary key
);

/*create table if not exists route(
	r_id int primary key,
    r_airline int,
    r_src int,
    r_dest int,
    r_codeshare boolean,
    r_plane char(3),
    constraint route_r_airline_fk foreign key (r_airline) references airline(l_id),
    constraint route_r_src_fk foreign key (r_src) references airport(a_id),
    constraint route_r_dest_fk foreign key (r_dest) references airport(a_id)
);*/