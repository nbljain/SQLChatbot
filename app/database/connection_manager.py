import os
import json
from typing import Dict, List, Optional, Any
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.engine.base import Engine

# Dictionary to store database connections
db_connections: Dict[str, Engine] = {}

# Current active connection name
active_connection_name = "default"

# Default database configuration
default_db_config = {
    "name": "default",
    "description": "SQLite Database",
    "type": "sqlite",
    "connection_string": "sqlite:///app/data/sql_chatbot.db",
    "display_name": "SQLite Sample Database"
}

def load_database_configs() -> List[Dict[str, str]]:
    """Load database configurations from config file"""
    config_file = "app/data/db_config.json"
    
    # Create default config if file doesn't exist
    if not os.path.exists(config_file):
        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(config_file), exist_ok=True)
        with open(config_file, "w") as f:
            json.dump([default_db_config], f, indent=2)
        return [default_db_config]
    
    try:
        with open(config_file, "r") as f:
            configs = json.load(f)
            # Make sure the default config is always available
            if not any(config["name"] == "default" for config in configs):
                configs.append(default_db_config)
            return configs
    except Exception as e:
        print(f"Error loading database configurations: {e}")
        return [default_db_config]

def save_database_configs(configs: List[Dict[str, str]]) -> bool:
    """Save database configurations to config file"""
    config_file = "app/data/db_config.json"
    try:
        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(config_file), exist_ok=True)
        with open(config_file, "w") as f:
            json.dump(configs, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving database configurations: {e}")
        return False

def add_database_connection(config: Dict[str, str]) -> bool:
    """Add a new database connection"""
    global active_connection_name
    
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

# Initialize the default connection
try:
    connect_to_database("default")
except Exception as e:
    print(f"Error initializing default database connection: {e}")
    raise