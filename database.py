import os
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import SQLAlchemyError

# Create a SQLite database
db_url = "sqlite:///sql_chatbot.db"

try:
    engine = create_engine(db_url)
    print(f"Successfully connected to SQLite database at sql_chatbot.db")
except Exception as e:
    print(f"Error creating database engine: {e}")
    raise

def get_table_names():
    """Get all table names from the database"""
    try:
        inspector = inspect(engine)
        return inspector.get_table_names()
    except SQLAlchemyError as e:
        print(f"Error getting table names: {e}")
        return []

def get_table_schema(table_name):
    """Get schema for a specific table"""
    try:
        inspector = inspect(engine)
        columns = inspector.get_columns(table_name)
        return {column['name']: column['type'].__str__() for column in columns}
    except SQLAlchemyError as e:
        print(f"Error getting schema for table {table_name}: {e}")
        return {}

def get_all_table_schemas():
    """Get schemas for all tables in the database"""
    try:
        table_schemas = {}
        tables = get_table_names()
        
        for table in tables:
            table_schemas[table] = get_table_schema(table)
        
        return table_schemas
    except Exception as e:
        print(f"Error getting all table schemas: {e}")
        return {}

def execute_sql_query(query):
    """Execute SQL query and return results"""
    try:
        with engine.connect() as connection:
            result = connection.execute(text(query))
            # Convert row objects to dictionaries
            rows = [dict(row._mapping) for row in result]
            return {"success": True, "data": rows}
    except Exception as e:
        return {"success": False, "error": str(e)}
