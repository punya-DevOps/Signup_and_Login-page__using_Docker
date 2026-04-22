-- ============================================================
--  AUTH_DB  –  Manual setup script
--  Run this in MySQL Workbench or the MySQL CLI:
--     mysql -u root -p < setup.sql
-- ============================================================

-- 1. Create the database
CREATE DATABASE IF NOT EXISTS auth_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE auth_db;

-- 2. Users table
CREATE TABLE IF NOT EXISTS users (
    id          INT UNSIGNED     AUTO_INCREMENT PRIMARY KEY,
    full_name   VARCHAR(100)     NOT NULL,
    email       VARCHAR(100)     UNIQUE,          -- NULL if user signed up with mobile
    mobile      VARCHAR(15)      UNIQUE,          -- NULL if user signed up with email
    password    VARCHAR(255)     NOT NULL,        -- bcrypt hash
    created_at  TIMESTAMP        DEFAULT CURRENT_TIMESTAMP,

    -- At least one identifier must be present
    CONSTRAINT chk_identifier CHECK (email IS NOT NULL OR mobile IS NOT NULL)
);

-- 3. Optional: view all registered users
-- SELECT id, full_name, email, mobile, created_at FROM users;
