import sqlalchemy
import sqlalchemy.exc
from sqlalchemy import inspect, text

from app.database.db_connection import get_db_engine

def get_table_names():
    """Get all table names from the database"""
    try:
        engine = get_db_engine()
        inspector = inspect(engine)
        return inspector.get_table_names()
    except Exception as e:
        print(f"Error getting table names: {e}")
        return []

def get_table_schema(table_name):
    """Get schema for a specific table"""
    try:
        engine = get_db_engine()
        inspector = inspect(engine)
        
        if table_name not in inspector.get_table_names():
            return None
        
        columns = inspector.get_columns(table_name)
        schema = {}
        
        for column in columns:
            schema[column['name']] = str(column['type'])
            
        return schema
    except Exception as e:
        print(f"Error getting schema for table {table_name}: {e}")
        return None

def get_all_table_schemas():
    """Get schemas for all tables in the database"""
    tables = get_table_names()
    full_schema = {}
    
    for table in tables:
        full_schema[table] = get_table_schema(table)
        
    return full_schema

def execute_sql_query(query):
    """Execute SQL query and return results"""
    try:
        engine = get_db_engine()
        
        with engine.connect() as connection:
            # Execute the query
            result = connection.execute(text(query))
            
            # Get column names
            column_names = result.keys()
            
            # Convert result to list of dicts
            rows = []
            for row in result:
                row_dict = {}
                for i, column in enumerate(column_names):
                    row_dict[column] = row[i]
                rows.append(row_dict)
            
            return {
                "success": True,
                "data": rows
            }
            
    except Exception as e:
        print(f"Error executing query: {e}")
        return {
            "success": False,
            "error": str(e)
        }