-- Create the database
CREATE DATABASE musicbox;

-- Create the user with the specified password
CREATE USER musicbox_user WITH PASSWORD 'musicbox_password';

-- Grant all privileges on the database to the user
GRANT ALL PRIVILEGES ON DATABASE musicbox TO musicbox_user;

-- Optional: Set the default privileges for the user to own tables they create
ALTER DATABASE musicbox OWNER TO musicbox_user;
