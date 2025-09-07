-- scripts-library/database/mysql/create_basic_table.sql
-- Template for creating a basic data table
-- Customize table name and fields as needed

CREATE TABLE IF NOT EXISTS data (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Alternative: Create table with different structure
-- Uncomment and modify as needed:

-- CREATE TABLE IF NOT EXISTS users (
--     ID INT AUTO_INCREMENT PRIMARY KEY,
--     username VARCHAR(100) UNIQUE NOT NULL,
--     email VARCHAR(255) UNIQUE NOT NULL,
--     password_hash VARCHAR(255) NOT NULL,
--     is_active BOOLEAN DEFAULT TRUE,
--     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
-- );

-- CREATE TABLE IF NOT EXISTS products (
--     ID INT AUTO_INCREMENT PRIMARY KEY,
--     name VARCHAR(255) NOT NULL,
--     description TEXT,
--     price DECIMAL(10,2) NOT NULL,
--     stock_quantity INT DEFAULT 0,
--     category_id INT,
--     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
-- );