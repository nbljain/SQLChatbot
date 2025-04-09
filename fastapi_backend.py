from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uvicorn
from database import get_table_names, get_table_schema, execute_sql_query
from langchain_sql import generate_sql_query

# Initialize FastAPI app
app = FastAPI(title="SQL Chatbot API")

# Define request and response models
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

# Run the API with Uvicorn when the script is executed directly
if __name__ == "__main__":
    uvicorn.run("fastapi_backend:app", host="0.0.0.0", port=8000, reload=True)
