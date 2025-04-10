import sqlite3
import os

def setup_employee_projects_db():
    # Create data directory if it doesn't exist
    os.makedirs("app/data", exist_ok=True)
    
    # Connect to SQLite database (creates it if it doesn't exist)
    conn = sqlite3.connect('app/data/sql_chatbot.db')
    cursor = conn.cursor()

    # Create employees table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS employees (
        employee_id INTEGER PRIMARY KEY,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        department TEXT NOT NULL,
        position TEXT NOT NULL,
        salary REAL NOT NULL,
        hire_date TEXT NOT NULL
    )
    ''')

    # Create projects table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS projects (
        project_id INTEGER PRIMARY KEY,
        project_name TEXT NOT NULL,
        description TEXT,
        start_date TEXT NOT NULL,
        end_date TEXT,
        budget REAL,
        department TEXT NOT NULL
    )
    ''')

    # Create employee_projects table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS employee_projects (
        assignment_id INTEGER PRIMARY KEY,
        employee_id INTEGER,
        project_id INTEGER,
        role TEXT NOT NULL,
        assigned_date TEXT NOT NULL,
        hours_allocated INTEGER NOT NULL,
        FOREIGN KEY (employee_id) REFERENCES employees (employee_id),
        FOREIGN KEY (project_id) REFERENCES projects (project_id)
    )
    ''')

    # Clear existing data
    cursor.execute("DELETE FROM employee_projects")
    cursor.execute("DELETE FROM employees")
    cursor.execute("DELETE FROM projects")

    # Reset auto-increment counters if sqlite_sequence exists
    try:
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='employees'")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='projects'")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='employee_projects'")
    except sqlite3.OperationalError:
        print("Note: sqlite_sequence table not found (this is normal for a fresh database)")

    # Sample data for employees
    employees_data = [
        ('John', 'Smith', 'john.smith@example.com', 'Engineering', 'Senior Developer', 95000.00, '2020-06-15'),
        ('Emily', 'Johnson', 'emily.johnson@example.com', 'Marketing', 'Marketing Manager', 85000.00, '2019-03-22'),
        ('Michael', 'Williams', 'michael.williams@example.com', 'Engineering', 'Developer', 78000.00, '2021-02-10'),
        ('Sarah', 'Brown', 'sarah.brown@example.com', 'Human Resources', 'HR Director', 92000.00, '2018-11-05'),
        ('David', 'Jones', 'david.jones@example.com', 'Finance', 'Financial Analyst', 76000.00, '2022-01-20'),
        ('Jessica', 'Davis', 'jessica.davis@example.com', 'Marketing', 'Content Specialist', 65000.00, '2021-08-15'),
        ('Robert', 'Miller', 'robert.miller@example.com', 'Engineering', 'Lead Developer', 105000.00, '2017-05-18'),
        ('Lisa', 'Wilson', 'lisa.wilson@example.com', 'Human Resources', 'Recruiter', 68000.00, '2020-04-12'),
        ('James', 'Taylor', 'james.taylor@example.com', 'Finance', 'Finance Manager', 98000.00, '2019-07-30'),
        ('Jennifer', 'Anderson', 'jennifer.anderson@example.com', 'Marketing', 'SEO Specialist', 72000.00, '2022-03-08')
    ]

    cursor.executemany('''
    INSERT INTO employees (first_name, last_name, email, department, position, salary, hire_date)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', employees_data)

    # Sample data for projects
    projects_data = [
        ('Website Redesign', 'Redesign company website with modern UI/UX', '2023-01-15', '2023-06-30', 120000.00, 'Engineering'),
        ('Q2 Marketing Campaign', 'Digital marketing campaign for Q2 product launch', '2023-03-01', '2023-05-31', 85000.00, 'Marketing'),
        ('HR System Implementation', 'Implement new HR management system', '2023-02-10', '2023-08-15', 95000.00, 'Human Resources'),
        ('Financial Reporting Tool', 'Develop automated financial reporting dashboard', '2023-04-01', '2023-07-31', 70000.00, 'Finance'),
        ('Mobile App Development', 'Develop mobile application for customers', '2023-01-10', '2023-09-30', 200000.00, 'Engineering')
    ]

    cursor.executemany('''
    INSERT INTO projects (project_name, description, start_date, end_date, budget, department)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', projects_data)

    # Sample data for employee_projects
    employee_projects_data = [
        (1, 1, 'Lead Developer', '2023-01-20', 120),
        (3, 1, 'Frontend Developer', '2023-01-25', 160),
        (7, 1, 'Backend Developer', '2023-01-22', 140),
        (2, 2, 'Campaign Manager', '2023-03-05', 100),
        (6, 2, 'Content Creator', '2023-03-10', 80),
        (10, 2, 'SEO Specialist', '2023-03-12', 60),
        (4, 3, 'HR Lead', '2023-02-15', 90),
        (8, 3, 'HR Assistant', '2023-02-20', 110),
        (5, 4, 'Finance Lead', '2023-04-05', 75),
        (9, 4, 'Data Analyst', '2023-04-10', 85),
        (1, 5, 'Technical Advisor', '2023-01-15', 50),
        (3, 5, 'Mobile Developer', '2023-01-18', 130),
        (7, 5, 'Lead Architect', '2023-01-12', 160)
    ]

    cursor.executemany('''
    INSERT INTO employee_projects (employee_id, project_id, role, assigned_date, hours_allocated)
    VALUES (?, ?, ?, ?, ?)
    ''', employee_projects_data)

    # Commit changes and close connection
    conn.commit()
    print("SQLite database setup complete with sample data.")

    # Verify data
    print("\nVerifying data:")
    cursor.execute("SELECT COUNT(*) FROM employees")
    print(f"Employees: {cursor.fetchone()[0]}")

    cursor.execute("SELECT COUNT(*) FROM projects")
    print(f"Projects: {cursor.fetchone()[0]}")

    cursor.execute("SELECT COUNT(*) FROM employee_projects")
    print(f"Employee project assignments: {cursor.fetchone()[0]}")

    # Close connection
    conn.close()
    
    return True

def setup_store_db():
    # Create data directory if it doesn't exist
    os.makedirs("app/data", exist_ok=True)
    
    # Connect to SQLite database (creates it if it doesn't exist)
    conn = sqlite3.connect('app/data/test_database.db')
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
    
    return True

if __name__ == "__main__":
    setup_employee_projects_db()
    setup_store_db()
    
    # Add the test database configuration to the system
    import json
    import os
    
    test_db_config = {
        "name": "store_db",
        "description": "Store Database with customer and product data",
        "type": "sqlite",
        "connection_string": "sqlite:///app/data/test_database.db",
        "display_name": "Store Database"
    }
    
    config_file = "app/data/db_config.json"
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(config_file), exist_ok=True)
    
    # Load existing configs or create default
    if os.path.exists(config_file):
        with open(config_file, "r") as f:
            configs = json.load(f)
    else:
        configs = [{
            "name": "default",
            "description": "SQLite Database",
            "type": "sqlite",
            "connection_string": "sqlite:///app/data/sql_chatbot.db",
            "display_name": "SQLite Sample Database"
        }]
    
    # Add test db config if it doesn't exist
    if not any(c["name"] == "store_db" for c in configs):
        configs.append(test_db_config)
        with open(config_file, "w") as f:
            json.dump(configs, f, indent=2)
        print("Added store database configuration to db_config.json")
    else:
        print("Store database configuration already exists")