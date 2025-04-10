def validate_connection_config(config):
    """Validate database connection configuration"""
    required_fields = ["name", "display_name", "type", "connection_string"]
    for field in required_fields:
        if field not in config or not config[field]:
            return False, f"Missing required field: {field}"
    
    # Check for unique name
    from app.database.connection_manager import load_database_configs
    configs = load_database_configs()
    
    # If this is a new config (not updating existing)
    if any(c["name"] == config["name"] for c in configs):
        return False, f"Connection with name '{config['name']}' already exists"
    
    return True, ""