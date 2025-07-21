-- Drop tables if they exist to prevent errors on re-creation
DROP TABLE IF EXISTS transactions CASCADE;
DROP TABLE IF EXISTS customers CASCADE;

-- Create customers table
-- This table stores basic information about each bank customer.
CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    phone_number VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create transactions table
-- This table will hold records of all financial transactions for customers.
CREATE TABLE transactions (
    transaction_id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    amount NUMERIC(10, 2) NOT NULL, -- Using NUMERIC for precise currency values
    type VARCHAR(50) NOT NULL, -- e.g., 'credit' for income, 'debit' for expenses
    description VARCHAR(255) NOT NULL,
    transaction_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE
);

-- Populate customers table with sample data
INSERT INTO customers (full_name, email, phone_number) VALUES
('Ariel Henryson', 'ariel.h@example.com', '555-0101'),
('Jane Doe', 'jane.d@example.com', '555-0102'),
('John Smith', 'john.s@example.com', '555-0103'),
('Emily White', 'emily.w@example.com', '555-0104');

-- Populate transactions table with sample data
-- This data corresponds to the customers created above.

-- Transactions for Ariel Henryson (customer_id = 1)
INSERT INTO transactions (customer_id, amount, type, description, transaction_date) VALUES
(1, 2500.00, 'credit', 'Monthly Salary', '2025-07-15 12:00:00+00'),
(1, 150.75, 'debit', 'Grocery Shopping', '2025-07-18 09:30:00+00'),
(1, 45.50, 'debit', 'Restaurant Dinner', '2025-07-20 19:45:00+00');

-- Transactions for Jane Doe (customer_id = 2)
INSERT INTO transactions (customer_id, amount, type, description, transaction_date) VALUES
(2, 1200.00, 'credit', 'Freelance Project Payment', '2025-07-19 14:00:00+00'),
(2, 89.99, 'debit', 'Online Shopping', '2025-07-19 15:10:00+00'),
(2, 500.00, 'debit', 'Rent Payment', '2025-07-01 10:00:00+00');

-- Transactions for John Smith (customer_id = 3)
INSERT INTO transactions (customer_id, amount, type, description, transaction_date) VALUES
(3, 3000.00, 'credit', 'Paycheck', '2025-07-15 11:00:00+00'),
(3, 25.00, 'debit', 'Coffee Shop', '2025-07-21 08:00:00+00'),
(3, 50.00, 'debit', 'Gasoline', '2025-07-20 17:00:00+00');

-- Transactions for Emily White (customer_id = 4)
INSERT INTO transactions (customer_id, amount, type, description, transaction_date) VALUES
(4, 75.20, 'debit', 'Bookstore', '2025-07-17 16:20:00+00');