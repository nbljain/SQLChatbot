import os
import logging
import sys
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import SQLAlchemyError

# Add the project root directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.utils.db_init import initialize_database

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize the database before connecting
initialize_database()

# Create a SQLite database connection
db_url = "sqlite:///sql_chatbot.db"

try:
    engine = create_engine(db_url)
    logger.info(f"Successfully connected to SQLite database at sql_chatbot.db")
except Exception as e:
    logger.error(f"Error creating database engine: {e}")
    raise

def get_table_names():
    """Get all table names from the database"""
    try:
        inspector = inspect(engine)
        return inspector.get_table_names()
    except SQLAlchemyError as e:
        logger.error(f"Error getting table names: {e}")
        return []

def get_table_schema(table_name):
    """Get schema for a specific table"""
    try:
        inspector = inspect(engine)
        columns = inspector.get_columns(table_name)
        return {column['name']: column['type'].__str__() for column in columns}
    except SQLAlchemyError as e:
        logger.error(f"Error getting schema for table {table_name}: {e}")
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
        logger.error(f"Error getting all table schemas: {e}")
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
        logger.error(f"Error executing SQL query: {e}")
        return {"success": False, "error": str(e)}