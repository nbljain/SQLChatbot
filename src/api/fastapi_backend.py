from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import uvicorn

from src.db.database import (
    get_table_names, 
    get_table_schema, 
    get_all_table_schemas, 
    execute_sql_query,
    get_active_connection_info,
    get_all_connections_info,
    connect_to_database,
    add_database_connection,
    remove_database_connection
)
from src.utils.langchain_sql import generate_sql_query

app = FastAPI()

# === Pydantic Models for Request/Response ===

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    success: bool
    sql: Optional[str] = None
    data: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None

class SchemaRequest(BaseModel):
    table_name: Optional[str] = None

class TableListResponse(BaseModel):
    tables: List[str]

class SchemaResponse(BaseModel):
    schema: Dict[str, Any]

class DatabaseConnectionInfo(BaseModel):
    name: str
    display_name: str
    description: str = ""
    type: str
    is_active: Optional[bool] = False

class DatabaseConnectionList(BaseModel):
    connections: List[DatabaseConnectionInfo]

class ActiveConnectionResponse(BaseModel):
    connection: DatabaseConnectionInfo

class DatabaseConnectionRequest(BaseModel):
    name: str
    display_name: str
    description: str = ""
    type: str
    connection_string: str

class ConnectionSwitchRequest(BaseModel):
    name: str

class MessageResponse(BaseModel):
    success: bool
    message: str

# === API Endpoints ===

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
        schema = {request.table_name: get_table_schema(request.table_name)}
    else:
        schema = get_all_table_schemas()
    
    return {"schema": schema}

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Process natural language query and return SQL results"""
    if not request.question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    # Generate SQL from natural language
    sql_result = generate_sql_query(request.question)
    
    if not sql_result.get("success", False):
        return {
            "success": False,
            "error": sql_result.get("error", "Failed to generate SQL")
        }
    
    sql_query = sql_result.get("sql", "")
    
    # Execute the SQL
    query_result = execute_sql_query(sql_query)
    
    if not query_result.get("success", False):
        return {
            "success": False,
            "sql": sql_query,
            "error": query_result.get("error", "Failed to execute SQL query")
        }
    
    # Return the results
    return {
        "success": True,
        "sql": sql_query,
        "data": query_result.get("data", [])
    }

@app.get("/connections", response_model=DatabaseConnectionList)
async def list_connections():
    """List all available database connections"""
    connections = get_all_connections_info()
    return {"connections": connections}

@app.get("/connections/active", response_model=ActiveConnectionResponse)
async def get_active_connection():
    """Get information about the active database connection"""
    connection = get_active_connection_info()
    return {"connection": connection}

@app.post("/connections/switch", response_model=MessageResponse)
async def switch_connection(request: ConnectionSwitchRequest):
    """Switch to a different database connection"""
    result = connect_to_database(request.name)
    if result:
        return {"success": True, "message": f"Successfully switched to database '{request.name}'"}
    else:
        return {"success": False, "message": f"Failed to switch to database '{request.name}'"}

@app.post("/connections/add", response_model=MessageResponse)
async def create_connection(request: DatabaseConnectionRequest):
    """Add a new database connection"""
    config = {
        "name": request.name,
        "display_name": request.display_name,
        "description": request.description,
        "type": request.type,
        "connection_string": request.connection_string
    }
    
    result = add_database_connection(config)
    if result:
        return {"success": True, "message": f"Successfully added database connection '{request.name}'"}
    else:
        return {"success": False, "message": f"Failed to add database connection '{request.name}'"}

@app.delete("/connections/{name}", response_model=MessageResponse)
async def delete_connection(name: str):
    """Remove a database connection"""
    result = remove_database_connection(name)
    if result:
        return {"success": True, "message": f"Successfully removed database connection '{name}'"}
    else:
        return {"success": False, "message": f"Failed to remove database connection '{name}'"}

def start_backend():
    """Start the FastAPI backend server"""
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    start_backend()