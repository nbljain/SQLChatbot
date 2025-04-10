import os
import csv
import sqlite3
import pandas as pd
from sqlalchemy import create_engine, inspect, text, MetaData, Table, Column, Integer, Float, String, Boolean
from sqlalchemy.orm import declarative_base

# Get paths
current_dir = os.path.dirname(os.path.abspath(__file__))
csv_file_path = os.path.join(current_dir, 'app', 'data', 'csv', 'employee_reviews.csv')
db_file_path = os.path.join(current_dir, 'app', 'data', 'sql_chatbot.db')

# SQLAlchemy setup
Base = declarative_base()

class EmployeeReview(Base):
    __tablename__ = 'employee_reviews'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer)
    review_date = Column(String)
    performance_score = Column(Float)
    review_text = Column(String)
    reviewer_id = Column(Integer)
    department = Column(String)
    improvement_needed = Column(String)
    strengths = Column(String)
    goals_met = Column(String)

def check_table_exists(engine, table_name):
    """Check if a table exists in the database"""
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()

def load_employee_reviews():
    """Load employee review data from CSV to SQLite database"""
    print(f"Loading employee reviews from: {csv_file_path}")
    
    # Create database connection
    engine = create_engine(f"sqlite:///{db_file_path}")
    
    # Check if table already exists
    if check_table_exists(engine, 'employee_reviews'):
        print("Employee reviews table already exists.")
        
        # Count rows to verify data is loaded
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM employee_reviews"))
            count = result.scalar()
            
        if count > 0:
            print(f"Table already contains {count} records. No need to reload data.")
            return engine
        else:
            print("Table exists but is empty. Will load data.")
    else:
        print("Creating employee_reviews table.")
        # Create the table
        Base.metadata.create_all(engine)
    
    # Read CSV data using pandas
    try:
        df = pd.read_csv(csv_file_path)
        print(f"Found {len(df)} records in CSV file.")
        
        # Insert data into the database
        df.to_sql('employee_reviews', engine, if_exists='replace', index=False)
        print("Successfully loaded employee reviews data into database.")
        
    except Exception as e:
        print(f"Error loading data: {e}")
    
    return engine

if __name__ == "__main__":
    # Load the data
    engine = load_employee_reviews()
    
    # Verify the data was loaded
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM employee_reviews"))
        count = result.scalar()
        print(f"Employee reviews table contains {count} records.")
        
        # Sample query to show some data
        result = conn.execute(text("""
            SELECT employee_id, department, performance_score, review_date 
            FROM employee_reviews LIMIT 5
        """))
        print("\nSample employee review data:")
        for row in result:
            print(f"Employee ID: {row[0]}, Department: {row[1]}, Score: {row[2]}, Date: {row[3]}")