import sqlite3

def setup_main_tables():
    """Create and populate the main database tables (employees, projects, assignments)"""
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
    conn.close()
    print("Main database tables setup complete with sample data.")

def setup_review_tables():
    """Create and populate employee review tables"""
    # Connect to SQLite database
    conn = sqlite3.connect('sql_chatbot.db')
    cursor = conn.cursor()
    
    # Create the review_categories table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS review_categories (
        category_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT
    )
    ''')
    
    # Create the review_themes table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS review_themes (
        theme_id INTEGER PRIMARY KEY,
        category_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        FOREIGN KEY (category_id) REFERENCES review_categories (category_id)
    )
    ''')
    
    # Create the review_subtopics table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS review_subtopics (
        subtopic_id INTEGER PRIMARY KEY,
        theme_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        FOREIGN KEY (theme_id) REFERENCES review_themes (theme_id)
    )
    ''')
    
    # Create the review_topics table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS review_topics (
        topic_id INTEGER PRIMARY KEY,
        subtopic_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        FOREIGN KEY (subtopic_id) REFERENCES review_subtopics (subtopic_id)
    )
    ''')
    
    # Create the survey_questions table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS survey_questions (
        question_id INTEGER PRIMARY KEY,
        question_text TEXT NOT NULL,
        created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create the employee_reviews table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS employee_reviews (
        review_id INTEGER PRIMARY KEY,
        employee_id INTEGER NOT NULL,
        question_id INTEGER NOT NULL,
        response_text TEXT NOT NULL,
        topic_id INTEGER,
        review_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (employee_id) REFERENCES employees (employee_id),
        FOREIGN KEY (question_id) REFERENCES survey_questions (question_id),
        FOREIGN KEY (topic_id) REFERENCES review_topics (topic_id)
    )
    ''')
    
    # Clear existing review data
    tables_to_clear = [
        'employee_reviews', 'survey_questions', 'review_topics', 
        'review_subtopics', 'review_themes', 'review_categories'
    ]
    
    for table in tables_to_clear:
        cursor.execute(f"DELETE FROM {table}")
        try:
            cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{table}'")
        except sqlite3.OperationalError:
            pass
    
    # Insert sample categories
    categories = [
        (1, 'Work Environment', 'Feedback related to the physical and cultural workplace'),
        (2, 'Management', 'Feedback related to leadership and management practices'),
        (3, 'Compensation', 'Feedback related to salary, benefits, and rewards'),
        (4, 'Career Growth', 'Feedback related to professional development and advancement')
    ]
    
    cursor.executemany('''
    INSERT OR IGNORE INTO review_categories (category_id, name, description)
    VALUES (?, ?, ?)
    ''', categories)
    
    # Insert sample themes
    themes = [
        (1, 1, 'Office Space', 'Physical workspace conditions'),
        (2, 1, 'Culture', 'Company culture and values'),
        (3, 2, 'Leadership Style', 'Approach to leadership and decision making'),
        (4, 3, 'Salary', 'Base compensation'),
        (5, 4, 'Training', 'Learning and development opportunities')
    ]
    
    cursor.executemany('''
    INSERT OR IGNORE INTO review_themes (theme_id, category_id, name, description)
    VALUES (?, ?, ?, ?)
    ''', themes)
    
    # Insert sample subtopics
    subtopics = [
        (1, 1, 'Desk Setup', 'Workstation ergonomics and setup'),
        (2, 2, 'Team Collaboration', 'Teamwork and collaboration practices'),
        (3, 3, 'Communication', 'Management communication effectiveness'),
        (4, 4, 'Pay Fairness', 'Perception of fair compensation'),
        (5, 5, 'Skill Development', 'Opportunities to develop new skills')
    ]
    
    cursor.executemany('''
    INSERT OR IGNORE INTO review_subtopics (subtopic_id, theme_id, name, description)
    VALUES (?, ?, ?, ?)
    ''', subtopics)
    
    # Insert sample topics
    topics = [
        (1, 1, 'Ergonomic Equipment', 'Quality and availability of ergonomic tools'),
        (2, 2, 'Team Building', 'Activities that promote team bonding'),
        (3, 3, 'Feedback Quality', 'Quality and frequency of manager feedback'),
        (4, 4, 'Industry Comparison', 'Salary compared to industry standards'),
        (5, 5, 'Learning Budget', 'Allocation for training and development')
    ]
    
    cursor.executemany('''
    INSERT OR IGNORE INTO review_topics (topic_id, subtopic_id, name, description)
    VALUES (?, ?, ?, ?)
    ''', topics)
    
    # Insert sample survey questions
    questions = [
        (1, 'How would you rate your overall satisfaction with your work environment?'),
        (2, 'What aspects of management could be improved?'),
        (3, 'Do you feel your compensation is fair compared to your contributions?'),
        (4, 'What training or development opportunities would help you grow professionally?'),
        (5, 'How would you describe the company culture in your own words?')
    ]
    
    cursor.executemany('''
    INSERT OR IGNORE INTO survey_questions (question_id, question_text)
    VALUES (?, ?)
    ''', questions)
    
    # Insert sample employee reviews
    reviews = [
        (1, 1, 1, 'The work environment is good, but my desk chair needs replacement.', 1),
        (2, 2, 2, 'My manager provides clear direction but could improve on timely feedback.', 3),
        (3, 3, 3, 'I believe I am paid fairly for my skills and experience.', 4),
        (4, 4, 4, 'I would like more budget for attending industry conferences.', 5),
        (5, 5, 5, 'The culture is collaborative and supportive.', 2)
    ]
    
    cursor.executemany('''
    INSERT OR IGNORE INTO employee_reviews (review_id, employee_id, question_id, response_text, topic_id)
    VALUES (?, ?, ?, ?, ?)
    ''', reviews)
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    print("Employee review tables setup complete with sample data.")

def setup_database():
    """Set up the complete database with all tables and sample data"""
    setup_main_tables()
    setup_review_tables()
    
    # Verify data
    conn = sqlite3.connect('sql_chatbot.db')
    cursor = conn.cursor()
    
    print("\nVerifying data:")
    cursor.execute("SELECT COUNT(*) FROM employees")
    print(f"Employees: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT COUNT(*) FROM projects")
    print(f"Projects: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT COUNT(*) FROM employee_projects")
    print(f"Employee project assignments: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT COUNT(*) FROM employee_reviews")
    print(f"Employee reviews: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT COUNT(*) FROM review_categories")
    print(f"Review categories: {cursor.fetchone()[0]}")
    
    # Close connection
    conn.close()
    
    print("\nDatabase setup complete!")

if __name__ == "__main__":
    setup_database()