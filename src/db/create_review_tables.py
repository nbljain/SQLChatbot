import sqlite3
import os

# Define the path to the SQLite database
DB_PATH = 'sql_chatbot.db'

def create_review_tables():
    """Create the employee review tables if they don't exist"""
    # Connect to the database
    conn = sqlite3.connect(DB_PATH)
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
    
    # Insert some sample categories
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
    
    # Insert some sample themes
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
    
    # Insert some sample subtopics
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
    
    # Insert some sample topics
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
    
    # Insert some sample survey questions
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
    
    # Insert some sample employee reviews
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
    
    print("Employee review tables created and populated successfully!")

if __name__ == "__main__":
    create_review_tables()