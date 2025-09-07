-- scripts-library/database/mysql/common_queries.sql
-- Common queries for testing and debugging

-- Check table structure
DESCRIBE data;

-- Count records
SELECT COUNT(*) as total_records FROM data;

-- Show all data with formatting
SELECT
    ID,
    CONCAT(first_name, ' ', last_name) as full_name,
    created_at
FROM data
ORDER BY ID;

-- Find specific records
SELECT * FROM data WHERE first_name LIKE '%John%';

-- Show table status
SHOW TABLE STATUS LIKE 'data';

-- Show all tables in database
SHOW TABLES;

-- Show database info
SELECT DATABASE() as current_database;