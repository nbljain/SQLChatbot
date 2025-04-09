import os
import json
from typing import Dict, List, Optional, Any
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.engine.base import Engine
from src.utils.encryption_utils import encrypt_value, decrypt_value

# Dictionary to store database connections
db_connections: Dict[str, Engine] = {}

# Current active connection name
active_connection_name = "default"

# Default database configuration
default_db_config = {
    "name": "default",
    "description": "SQLite Database",
    "type": "sqlite",
    "connection_string": "sqlite:///sql_chatbot.db",
    "display_name": "SQLite Sample Database",
    "encrypted": False
}

def load_database_configs() -> List[Dict[str, Any]]:
    """Load database configurations from config file"""
    config_file = "db_config.json"
    
    # Create default config if file doesn't exist
    if not os.path.exists(config_file):
        with open(config_file, "w") as f:
            json.dump([default_db_config], f, indent=2)
        return [default_db_config]
    
    try:
        with open(config_file, "r") as f:
            configs = json.load(f)
            
            # Make sure the default config is always available
            if not any(config["name"] == "default" for config in configs):
                configs.append(default_db_config)
            
            # Decrypt any encrypted connection strings
            for config in configs:
                if config.get("encrypted", False):
                    try:
                        config["connection_string"] = decrypt_value(config["connection_string"])
                    except Exception as e:
                        print(f"Error decrypting connection string for {config['name']}: {e}")
                        # If decryption fails, keep the encrypted string
            
            return configs
    except Exception as e:
        print(f"Error loading database configurations: {e}")
        return [default_db_config]

def save_database_configs(configs: List[Dict[str, Any]]) -> bool:
    """Save database configurations to config file"""
    config_file = "db_config.json"
    try:
        # Make a deep copy of the configs to avoid modifying the original
        configs_to_save = []
        for config in configs:
            config_copy = config.copy()
            
            # Encrypt the connection string if not already encrypted
            if not config.get("encrypted", False) and "connection_string" in config:
                try:
                    config_copy["connection_string"] = encrypt_value(config["connection_string"])
                    config_copy["encrypted"] = True
                except Exception as e:
                    print(f"Error encrypting connection string for {config['name']}: {e}")
                    # If encryption fails, save as plaintext but mark as not encrypted
                    config_copy["encrypted"] = False
            
            configs_to_save.append(config_copy)
        
        with open(config_file, "w") as f:
            json.dump(configs_to_save, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving database configurations: {e}")
        return False

def add_database_connection(config: Dict[str, str]) -> bool:
    """Add a new database connection"""
    # Add validation for required fields
    required_fields = ["name", "type", "connection_string"]
    for field in required_fields:
        if field not in config:
            print(f"Missing required field: {field}")
            return False
    
    # Ensure name is unique
    configs = load_database_configs()
    if any(c["name"] == config["name"] for c in configs):
        print(f"Database with name '{config['name']}' already exists")
        return False
    
    # Add the new config
    configs.append(config)
    
    # Save to file
    if save_database_configs(configs):
        # Immediately connect to the new database
        return connect_to_database(config["name"])
    
    return False

def remove_database_connection(name: str) -> bool:
    """Remove a database connection"""
    global active_connection_name
    
    # Cannot remove default
    if name == "default":
        print("Cannot remove the default database connection")
        return False
    
    # If it's the active connection, switch to default first
    if name == active_connection_name:
        connect_to_database("default")
    
    # Remove from connections dictionary
    if name in db_connections:
        del db_connections[name]
    
    # Remove from config
    configs = load_database_configs()
    configs = [c for c in configs if c["name"] != name]
    
    return save_database_configs(configs)

def connect_to_database(name: str) -> bool:
    """Connect to a specific database by name"""
    global active_connection_name
    
    # Check if connection already exists
    if name in db_connections:
        active_connection_name = name
        print(f"Switched to existing database connection: {name}")
        return True
    
    # Find the config for this connection
    configs = load_database_configs()
    config = next((c for c in configs if c["name"] == name), None)
    
    if not config:
        print(f"No database configuration found with name: {name}")
        return False
    
    try:
        # Create the engine
        engine = create_engine(config["connection_string"])
        
        # Test the connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        # Store the connection
        db_connections[name] = engine
        
        # Set as active
        active_connection_name = name
        
        display_name = config.get("display_name", name)
        print(f"Successfully connected to database: {display_name}")
        return True
    except Exception as e:
        print(f"Error connecting to database {name}: {e}")
        return False

def get_active_connection() -> Engine:
    """Get the currently active database connection"""
    global active_connection_name
    
    # If no connections exist, connect to default
    if not db_connections:
        connect_to_database("default")
    
    # If active connection doesn't exist, use first available
    if active_connection_name not in db_connections:
        if "default" in db_connections:
            active_connection_name = "default"
        else:
            active_connection_name = next(iter(db_connections))
    
    return db_connections[active_connection_name]

def get_active_connection_info() -> Dict[str, Any]:
    """Get information about the active database connection"""
    global active_connection_name
    configs = load_database_configs()
    config = next((c for c in configs if c["name"] == active_connection_name), None)
    
    if not config:
        # Return info for default if active not found
        config = next((c for c in configs if c["name"] == "default"), default_db_config)
    
    # Return a safe subset of the connection info (excluding connection string)
    return {
        "name": config["name"],
        "display_name": config.get("display_name", config["name"]),
        "description": config.get("description", ""),
        "type": config["type"]
    }

def get_all_connections_info() -> List[Dict[str, Any]]:
    """Get information about all available database connections"""
    configs = load_database_configs()
    # Return only the safe information for each connection
    return [{
        "name": c["name"],
        "display_name": c.get("display_name", c["name"]),
        "description": c.get("description", ""),
        "type": c["type"],
        "is_active": c["name"] == active_connection_name
    } for c in configs]

def get_table_names():
    """Get all table names from the database"""
    try:
        engine = get_active_connection()
        inspector = inspect(engine)
        return inspector.get_table_names()
    except SQLAlchemyError as e:
        print(f"Error getting table names: {e}")
        return []

def get_table_schema(table_name):
    """Get schema for a specific table"""
    try:
        engine = get_active_connection()
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
        engine = get_active_connection()
        with engine.connect() as connection:
            result = connection.execute(text(query))
            # Convert row objects to dictionaries
            rows = [dict(row._mapping) for row in result]
            return {"success": True, "data": rows}
    except Exception as e:
        return {"success": False, "error": str(e)}

# Initialize the default connection
try:
    connect_to_database("default")
except Exception as e:
    print(f"Error initializing default database connection: {e}")
    raise