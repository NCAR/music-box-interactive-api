CREATE USER musicbox_user WITH PASSWORD 'musicbox_password';

CREATE DATABASE musicbox;
GRANT ALL PRIVILEGES ON DATABASE musicbox TO musicbox_user;