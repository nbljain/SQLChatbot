import os
import csv
import sqlite3
import pandas as pd
from sqlalchemy import create_engine, inspect, text, MetaData, Table, Column, Integer, Float, String, Boolean, insert
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

# Get the absolute path of the current file
current_dir = os.path.dirname(os.path.abspath(__file__))
csv_file_path = os.path.join(current_dir, 'csv', 'employee_reviews.csv')
db_file_path = os.path.join(current_dir, 'sql_chatbot.db')

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

def load_reviews_from_csv():
    """Load employee reviews from CSV to database"""
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

def get_connection():
    """Get a connection to the database with employee reviews"""
    engine = create_engine(f"sqlite:///{db_file_path}")
    
    # Check if table exists, if not, load data
    if not check_table_exists(engine, 'employee_reviews'):
        engine = load_reviews_from_csv()
    
    return engine

def add_employee_reviews_to_config():
    """Add employee reviews database to the connection config"""
    try:
        import json
        config_file = os.path.join(current_dir, 'db_config.json')
        
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                configs = json.load(f)
            
            # Check if employee_reviews config already exists
            if not any(c.get('name') == 'employee_reviews' for c in configs):
                # Add new connection config
                configs.append({
                    "name": "employee_reviews",
                    "description": "Employee Reviews Database",
                    "type": "sqlite",
                    "connection_string": f"sqlite:///{db_file_path}",
                    "display_name": "Employee Reviews Database"
                })
                
                # Save updated config
                with open(config_file, 'w') as f:
                    json.dump(configs, f, indent=2)
                    
                print("Added employee reviews database to connection configurations.")
            else:
                print("Employee reviews database already in configurations.")
        else:
            print("Config file not found. Database will still be created.")
    except Exception as e:
        print(f"Error updating config file: {e}")
        print("Database will still be created and can be accessed directly.")

if __name__ == "__main__":
    # Load the data
    engine = load_reviews_from_csv()
    
    # Add to connection config
    add_employee_reviews_to_config()
    
    # Verify the data was loaded
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM employee_reviews"))
        count = result.scalar()
        print(f"Employee reviews table contains {count} records.")
        
        # Sample query to show some data
        result = conn.execute(text("SELECT employee_id, department, performance_score FROM employee_reviews LIMIT 5"))
        print("\nSample employee review data:")
        for row in result:
            print(f"Employee ID: {row[0]}, Department: {row[1]}, Score: {row[2]}")