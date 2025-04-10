from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union

from app.database.db_connection import load_config, get_db_engine
from app.database.db_operations import (
    get_table_names, get_table_schema, get_all_table_schemas, execute_sql_query
)
from app.models import generate_sql_query
from app.api.models import (
    QueryRequest, QueryResponse, SchemaRequest, TableListResponse,
    SchemaResponse, MessageResponse
)

# Initialize FastAPI app
app = FastAPI(title="SQL Chatbot API")

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
        return {"schema": get_all_table_schemas()}

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

@app.get("/db-info")
async def get_db_info():
    """Get database connection information"""
    config = load_config()
    # Return sanitized config (without sensitive connection details)
    return {
        "database_type": config["database"]["type"],
        "app_port": config["app"]["port"],
        "api_port": config["api"]["port"]
    }