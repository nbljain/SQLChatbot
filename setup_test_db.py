import sqlite3

# Connect to SQLite database (creates it if it doesn't exist)
conn = sqlite3.connect('test_database.db')
cursor = conn.cursor()

# Create products table
cursor.execute('''
CREATE TABLE IF NOT EXISTS products (
    product_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    price REAL NOT NULL,
    stock_quantity INTEGER NOT NULL,
    description TEXT
)
''')

# Create customers table
cursor.execute('''
CREATE TABLE IF NOT EXISTS customers (
    customer_id INTEGER PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone TEXT,
    address TEXT
)
''')

# Create orders table
cursor.execute('''
CREATE TABLE IF NOT EXISTS orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER,
    order_date TEXT NOT NULL,
    total_amount REAL NOT NULL,
    status TEXT NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
)
''')

# Create order_items table
cursor.execute('''
CREATE TABLE IF NOT EXISTS order_items (
    item_id INTEGER PRIMARY KEY,
    order_id INTEGER,
    product_id INTEGER,
    quantity INTEGER NOT NULL,
    price REAL NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders (order_id),
    FOREIGN KEY (product_id) REFERENCES products (product_id)
)
''')

# Clear existing data
tables = ['order_items', 'orders', 'customers', 'products']
for table in tables:
    cursor.execute(f"DELETE FROM {table}")

# Sample data for products
products_data = [
    ('Laptop', 'Electronics', 999.99, 15, 'High-performance laptop with 16GB RAM'),
    ('Smartphone', 'Electronics', 699.99, 25, '5G-capable smartphone with triple camera'),
    ('Desk Chair', 'Furniture', 129.99, 8, 'Ergonomic office chair'),
    ('Coffee Maker', 'Appliances', 79.99, 12, 'Programmable 12-cup coffee maker'),
    ('Wireless Headphones', 'Electronics', 149.99, 18, 'Noise-cancelling wireless headphones'),
    ('Desk Lamp', 'Furniture', 39.99, 20, 'LED desk lamp with adjustable brightness'),
    ('Blender', 'Appliances', 89.99, 10, 'High-speed blender for smoothies'),
    ('Bookshelf', 'Furniture', 149.99, 5, 'Wooden bookshelf with 5 shelves'),
    ('Tablet', 'Electronics', 499.99, 22, '10-inch tablet with 128GB storage'),
    ('Toaster', 'Appliances', 49.99, 15, '4-slice toaster with bagel setting')
]

cursor.executemany('''
INSERT INTO products (name, category, price, stock_quantity, description)
VALUES (?, ?, ?, ?, ?)
''', products_data)

# Sample data for customers
customers_data = [
    ('John', 'Doe', 'john.doe@example.com', '555-123-4567', '123 Main St, City'),
    ('Jane', 'Smith', 'jane.smith@example.com', '555-234-5678', '456 Oak Ave, Town'),
    ('Robert', 'Johnson', 'robert.j@example.com', '555-345-6789', '789 Pine Rd, Village'),
    ('Sarah', 'Williams', 'sarah.w@example.com', '555-456-7890', '101 Maple Dr, County'),
    ('Michael', 'Brown', 'michael.b@example.com', '555-567-8901', '202 Cedar Ln, Borough')
]

cursor.executemany('''
INSERT INTO customers (first_name, last_name, email, phone, address)
VALUES (?, ?, ?, ?, ?)
''', customers_data)

# Sample data for orders
orders_data = [
    (1, '2023-01-15', 999.99, 'Delivered'),
    (2, '2023-02-20', 279.98, 'Shipped'),
    (3, '2023-03-10', 549.97, 'Processing'),
    (4, '2023-03-15', 129.99, 'Delivered'),
    (1, '2023-04-05', 239.98, 'Delivered'),
    (5, '2023-04-20', 699.99, 'Shipped')
]

cursor.executemany('''
INSERT INTO orders (customer_id, order_date, total_amount, status)
VALUES (?, ?, ?, ?)
''', orders_data)

# Sample data for order_items
order_items_data = [
    (1, 1, 1, 999.99),
    (2, 4, 1, 79.99),
    (2, 6, 1, 199.99),
    (3, 2, 0.5, 349.995),
    (3, 5, 1, 149.99),
    (3, 10, 1, 49.99),
    (4, 3, 1, 129.99),
    (5, 5, 1, 149.99),
    (5, 4, 1, 79.99),
    (6, 2, 1, 699.99)
]

cursor.executemany('''
INSERT INTO order_items (order_id, product_id, quantity, price)
VALUES (?, ?, ?, ?)
''', order_items_data)

# Commit changes and close connection
conn.commit()
print("Test database setup complete with sample data.")

# Verify data
print("\nVerifying data:")
cursor.execute("SELECT COUNT(*) FROM products")
print(f"Products: {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(*) FROM customers")
print(f"Customers: {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(*) FROM orders")
print(f"Orders: {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(*) FROM order_items")
print(f"Order items: {cursor.fetchone()[0]}")

# Close connection
conn.close()