drop database if exists streamoutput;
create database streamoutput;

\c streamoutput;
drop table if exists taxi_etl;
create table taxi_etl (
    day VARCHAR(128) NOT NULL,
    borough VARCHAR(128) NOT NULL,
    num_departures INTEGER NOT NULL,
    num_arrivals INTEGER NOT NULL,
    total_departing_passengers INTEGER NOT NULL,
    total_arriving_passengers INTEGER NOT NULL
)
