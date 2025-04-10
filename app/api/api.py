from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union

from app.database import (
    get_table_names, get_table_schema, execute_sql_query,
    get_all_connections_info, get_active_connection_info,
    connect_to_database, add_database_connection, remove_database_connection
)
from app.models import generate_sql_query
from app.api.models import (
    QueryRequest, QueryResponse, SchemaRequest, TableListResponse,
    SchemaResponse, DatabaseConnectionInfo, DatabaseConnectionList,
    ActiveConnectionResponse, DatabaseConnectionRequest,
    ConnectionSwitchRequest, MessageResponse
)

# Initialize FastAPI app
app = FastAPI(title="SQL Chatbot API")

# Group routers for organization
routers = {
    "database": ["/tables", "/schema"],
    "query": ["/query"],
    "connection": ["/connections", "/connections/active", "/connections/switch", "/connections/add"]
}

# API endpoints
@app.get("/")
async def root():
    return {"message": "SQL Chatbot API is running"}

@app.get("/tables", response_model=TableListResponse)
async def get_tables():
    """Get all table names from the database"""
    tables = get_table_names()
    return {"tables": tables}

@app.post("/schema", response_model=SchemaResponse)
async def get_schema(request: SchemaRequest):
    """Get schema for a specific table or all tables"""
    if request.table_name:
        schema = get_table_schema(request.table_name)
        if not schema:
            raise HTTPException(status_code=404, detail=f"Table {request.table_name} not found")
        return {"schema": {request.table_name: schema}}
    else:
        # Get all table schemas
        tables = get_table_names()
        full_schema = {}
        for table in tables:
            full_schema[table] = get_table_schema(table)
        return {"schema": full_schema}

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Process natural language query and return SQL results"""
    if not request.question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    # Generate SQL from natural language
    sql_result = generate_sql_query(request.question)
    
    if not sql_result["success"]:
        return {
            "success": False,
            "error": sql_result["error"]
        }
    
    # Execute the generated SQL
    query_result = execute_sql_query(sql_result["sql"])
    
    if not query_result["success"]:
        return {
            "success": False,
            "sql": sql_result["sql"],
            "error": query_result["error"]
        }
    
    # Return successful response
    return {
        "success": True,
        "sql": sql_result["sql"],
        "data": query_result["data"]
    }

# Database connection management endpoints
@app.get("/connections", response_model=DatabaseConnectionList)
async def list_connections():
    """List all available database connections"""
    connections = get_all_connections_info()
    return {"connections": connections}

@app.get("/connections/active", response_model=ActiveConnectionResponse)
async def get_active_connection():
    """Get information about the active database connection"""
    connection = get_active_connection_info()
    # Create a new dict with is_active flag for consistency with list endpoint
    connection_with_flag = {**connection, "is_active": True}
    return {"connection": connection_with_flag}

@app.post("/connections/switch", response_model=MessageResponse)
async def switch_connection(request: ConnectionSwitchRequest):
    """Switch to a different database connection"""
    success = connect_to_database(request.name)
    if not success:
        raise HTTPException(status_code=404, detail=f"Database connection '{request.name}' not found or connection failed")
    
    return {
        "success": True,
        "message": f"Successfully switched to database connection: {request.name}"
    }

@app.post("/connections/add", response_model=MessageResponse)
async def create_connection(request: DatabaseConnectionRequest):
    """Add a new database connection"""
    connection_config = {
        "name": request.name,
        "display_name": request.display_name,
        "description": request.description,
        "type": request.type,
        "connection_string": request.connection_string
    }
    
    success = add_database_connection(connection_config)
    
    if not success:
        raise HTTPException(status_code=400, detail=f"Failed to add database connection '{request.name}'")
    
    return {
        "success": True,
        "message": f"Successfully added database connection: {request.name}"
    }

@app.delete("/connections/{name}", response_model=MessageResponse)
async def delete_connection(name: str):
    """Remove a database connection"""
    if name == "default":
        raise HTTPException(status_code=400, detail="Cannot remove the default database connection")
    
    success = remove_database_connection(name)
    
    if not success:
        raise HTTPException(status_code=404, detail=f"Database connection '{name}' not found or could not be removed")
    
    return {
        "success": True,
        "message": f"Successfully removed database connection: {name}"
    }