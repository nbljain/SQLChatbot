import os
import json
import sqlalchemy
from sqlalchemy import create_engine

# Base path for the app
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "app", "data")
CONFIG_PATH = os.path.join(DATA_DIR, "config.json")
DATABASE_PATH = os.path.join(DATA_DIR, "sql_chatbot.db")

# Global engine object
_engine = None

def ensure_directories():
    """Ensure all necessary directories exist"""
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(os.path.join(DATA_DIR, "csv"), exist_ok=True)
    
    # Output paths created for debugging
    print(f"BASE_DIR: {BASE_DIR}")
    print(f"DATA_DIR: {DATA_DIR}")
    print(f"CONFIG_PATH: {CONFIG_PATH}")
    print(f"DATABASE_PATH: {DATABASE_PATH}")

def load_config():
    """Load configuration from config file"""
    # Make sure directories exist
    ensure_directories()
    
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
    
    # Return default config if file doesn't exist
    default_config = {
        "app": {
            "port": 5000
        },
        "api": {
            "port": 8000
        },
        "database": {
            "type": "sqlite",
            "path": DATABASE_PATH
        }
    }
    
    # Create config file if it doesn't exist
    try:
        with open(CONFIG_PATH, "w") as f:
            json.dump(default_config, f, indent=2)
    except Exception as e:
        print(f"Error creating default config: {e}")
    
    return default_config

def get_db_engine():
    """Get a SQLAlchemy engine for database operations"""
    global _engine
    
    if _engine is not None:
        return _engine
    
    config = load_config()
    db_type = config["database"]["type"]
    
    if db_type == "sqlite":
        # Set a default path if not provided
        db_path = config["database"].get("path", DATABASE_PATH)
        connection_string = f"sqlite:///{db_path}"
    else:
        # Default to SQLite if unknown type
        connection_string = f"sqlite:///{DATABASE_PATH}"
    
    _engine = create_engine(connection_string)
    return _engine

def check_table_exists(table_name):
    """Check if a table exists in the database"""
    from sqlalchemy import inspect
    engine = get_db_engine()
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()

def execute_query(query_text, params=None):
    """Execute a SQL query and return results"""
    from sqlalchemy import text
    
    engine = get_db_engine()
    
    try:
        with engine.connect() as conn:
            if params:
                result = conn.execute(text(query_text), params)
            else:
                result = conn.execute(text(query_text))
                
            # For SELECT queries
            if query_text.strip().lower().startswith("select"):
                columns = result.keys()
                data = [dict(zip(columns, row)) for row in result]
                return {"success": True, "data": data}
            
            # For other queries
            return {"success": True, "rowcount": result.rowcount}
            
    except Exception as e:
        print(f"Database error: {e}")
        return {"success": False, "error": str(e)}