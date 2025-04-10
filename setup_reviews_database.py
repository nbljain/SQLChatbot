import os
import sys
import csv
import sqlite3
import pandas as pd
import json
from sqlalchemy import create_engine, inspect, text

def setup_employee_reviews_database():
    """Setup and load employee reviews database"""
    # Get file paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    csv_file_path = os.path.join(current_dir, 'app', 'data', 'csv', 'employee_reviews.csv')
    db_file_path = os.path.join(current_dir, 'app', 'data', 'sql_chatbot.db')
    config_file_path = os.path.join(current_dir, 'app', 'data', 'db_config.json')
    
    print(f"Setting up employee reviews database...")
    print(f"CSV path: {csv_file_path}")
    print(f"DB path: {db_file_path}")
    
    # Create database connection
    engine = create_engine(f"sqlite:///{db_file_path}")
    
    # Check if the employee_reviews table already exists
    inspector = inspect(engine)
    table_exists = 'employee_reviews' in inspector.get_table_names()
    
    if table_exists:
        print("Employee reviews table already exists.")
        
        # Count rows to verify data is loaded
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM employee_reviews"))
            count = result.scalar()
            
        if count > 0:
            print(f"Table already contains {count} records. No need to reload data.")
        else:
            print("Table exists but is empty. Will load data.")
            # Load data from CSV
            df = pd.read_csv(csv_file_path)
            print(f"Found {len(df)} records in CSV file.")
            df.to_sql('employee_reviews', engine, if_exists='replace', index=False)
            print("Successfully loaded employee reviews data into database.")
    else:
        print("Creating employee_reviews table and loading data.")
        # Read CSV data
        df = pd.read_csv(csv_file_path)
        print(f"Found {len(df)} records in CSV file.")
        
        # Create table and insert data
        df.to_sql('employee_reviews', engine, if_exists='replace', index=False)
        print("Successfully created employee reviews table and loaded data.")
    
    # Update the database configuration file
    if os.path.exists(config_file_path):
        try:
            with open(config_file_path, 'r') as f:
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
                with open(config_file_path, 'w') as f:
                    json.dump(configs, f, indent=2)
                    
                print("Added employee reviews database to connection configurations.")
            else:
                print("Employee reviews database already in configurations.")
        except Exception as e:
            print(f"Error updating config file: {e}")
    else:
        print(f"Config file not found at {config_file_path}. Database will still be created but not added to connections.")
    
    # Verify the data
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM employee_reviews"))
        count = result.scalar()
        print(f"Employee reviews table contains {count} records.")
        
        # Sample query to show some data
        result = conn.execute(text("SELECT employee_id, department, performance_score FROM employee_reviews LIMIT 5"))
        print("\nSample employee review data:")
        for row in result:
            print(f"Employee ID: {row[0]}, Department: {row[1]}, Score: {row[2]}")

if __name__ == "__main__":
    try:
        setup_employee_reviews_database()
        print("\nEmployee reviews database setup completed successfully.")
    except Exception as e:
        print(f"Error setting up employee reviews database: {e}")
        sys.exit(1)