import sqlite3

# Connect to SQLite database (creates it if it doesn't exist)
conn = sqlite3.connect('sql_chatbot.db')
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