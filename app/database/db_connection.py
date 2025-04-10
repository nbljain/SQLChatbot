import os
import json
from sqlalchemy import create_engine, inspect, text

# Load configuration
def load_config():
    """Load configuration from config file"""
    config_file = "app/data/config.json"
    try:
        if os.path.exists(config_file):
            with open(config_file, "r") as f:
                return json.load(f)
        else:
            # Return default config if file doesn't exist
            return {
                "database": {
                    "uri": "sqlite:///app/data/sql_chatbot.db",
                    "type": "sqlite"
                },
                "app": {
                    "port": 5000,
                    "host": "0.0.0.0",
                    "debug": False
                },
                "api": {
                    "port": 8000,
                    "host": "0.0.0.0"
                }
            }
    except Exception as e:
        print(f"Error loading configuration: {e}")
        # Return default config in case of error
        return {
            "database": {
                "uri": "sqlite:///app/data/sql_chatbot.db",
                "type": "sqlite"
            },
            "app": {
                "port": 5000,
                "host": "0.0.0.0",
                "debug": False
            },
            "api": {
                "port": 8000,
                "host": "0.0.0.0"
            }
        }

# Create singleton database engine
_engine = None

def get_db_engine():
    """Get a SQLAlchemy engine for database operations"""
    global _engine
    
    if _engine is None:
        config = load_config()
        db_uri = config["database"]["uri"]
        
        try:
            _engine = create_engine(db_uri)
            print(f"Successfully connected to database at {db_uri}")
        except Exception as e:
            print(f"Error connecting to database: {e}")
            raise
    
    return _engine

# Additional helper functions
def check_table_exists(table_name):
    """Check if a table exists in the database"""
    engine = get_db_engine()
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()

def execute_query(query_text, params=None):
    """Execute a SQL query and return results"""
    engine = get_db_engine()
    with engine.connect() as conn:
        if params:
            result = conn.execute(text(query_text), params)
        else:
            result = conn.execute(text(query_text))
        return result