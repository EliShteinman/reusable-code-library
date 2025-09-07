-- scripts-library/database/mysql/insert_sample_data.sql
-- Template for inserting sample data
-- Customize data as needed for your specific use case

INSERT INTO data (first_name, last_name) VALUES
('John', 'Doe'),
('Jane', 'Smith'),
('Peter', 'Jones'),
('Emily', 'Williams'),
('Michael', 'Brown'),
('Sarah', 'Davis'),
('David', 'Miller'),
('Lisa', 'Wilson'),
('Robert', 'Moore'),
('Amanda', 'Taylor');

-- Alternative sample data sets:
-- Uncomment and modify as needed:

-- For users table:
-- INSERT INTO users (username, email, password_hash) VALUES
-- ('admin', 'admin@example.com', 'hashed_password_1'),
-- ('user1', 'user1@example.com', 'hashed_password_2'),
-- ('user2', 'user2@example.com', 'hashed_password_3'),
-- ('test_user', 'test@example.com', 'hashed_password_4');

-- For products table:
-- INSERT INTO products (name, description, price, stock_quantity) VALUES
-- ('Product A', 'Description for Product A', 29.99, 100),
-- ('Product B', 'Description for Product B', 49.99, 50),
-- ('Product C', 'Description for Product C', 19.99, 200),
-- ('Product D', 'Description for Product D', 99.99, 25);