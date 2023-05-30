--
-- PostgreSQL database cluster dump
--

SET default_transaction_read_only = off;

SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;

--
-- Roles
--

CREATE ROLE azure_pg_admin;
ALTER ROLE azure_pg_admin WITH NOSUPERUSER INHERIT NOCREATEROLE NOCREATEDB NOLOGIN REPLICATION NOBYPASSRLS;
CREATE ROLE azure_superuser;
ALTER ROLE azure_superuser WITH SUPERUSER INHERIT CREATEROLE CREATEDB LOGIN REPLICATION BYPASSRLS;
CREATE ROLE hanil;
ALTER ROLE hanil WITH NOSUPERUSER INHERIT CREATEROLE CREATEDB LOGIN REPLICATION NOBYPASSRLS PASSWORD 'md56c7a4a840f579ca3bb720f837bbf82fa';

--
-- User Configurations
--

--
-- User Config "azure_superuser"
--

ALTER ROLE azure_superuser SET search_path TO 'pg_catalog';


--
-- Role memberships
--

GRANT azure_pg_admin TO hanil GRANTED BY azure_superuser;


--
-- PostgreSQL database cluster dump complete
--

