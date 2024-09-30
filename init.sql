-- init.sql
CREATE DATABASE musicbox;
CREATE USER musicbox_user WITH PASSWORD 'musicbox_password';
ALTER ROLE musicbox_user SET client_encoding TO 'utf8';
ALTER ROLE musicbox_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE musicbox_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE musicbox TO musicbox_user;

-- Grant usage on the public schema
GRANT USAGE ON SCHEMA public TO musicbox_user;

-- Grant the ability to create tables in the public schema
GRANT CREATE ON SCHEMA public TO musicbox_user;

-- Optionally, you can make the user the owner of the public schema
ALTER SCHEMA public OWNER TO musicbox_user;