#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    create database notme_dev;
    create database notme_tst;
    \c notme_dev;
    create extension if not exists fuzzystrmatch;
    create extension if not exists postgis;
    create extension if not exists postgis_tiger_geocoder;
    create extension if not exists postgis_topology;
    create schema pgsodium;
    create extension if not exists pgsodium with schema pgsodium;
    \c notme_tst;
    create extension if not exists fuzzystrmatch;
    create extension if not exists postgis;
    create extension if not exists postgis_tiger_geocoder;
    create extension if not exists postgis_topology;
    create schema pgsodium;
    create extension if not exists pgsodium with schema pgsodium;
EOSQL