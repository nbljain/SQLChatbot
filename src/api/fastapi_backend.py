from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends
from pydantic import BaseModel
from typing import Dict, List, Optional, Any, Union, Literal
import uvicorn
import os
import tempfile
import shutil

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
from src.utils.csv_import import preview_csv, import_csv_to_table
from src.utils.csv_file_loader import (
    get_available_csv_files,
    get_csv_preview,
    import_csv_to_db,
    import_related_tables,
    import_all_available_tables,
    get_table_schema as get_csv_table_schema,
    get_table_relationships as get_csv_table_relationships
)

app = FastAPI()

# === Pydantic Models for Request/Response ===

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    success: bool
    sql: Optional[str] = None
    data: Optional[List[Dict[str, Any]]] = None
    explanation: Optional[str] = None
    insights: Optional[Union[str, List[str]]] = None
    follow_up_questions: Optional[List[str]] = None
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

class CSVPreviewResponse(BaseModel):
    success: bool
    preview_data: Optional[List[Dict[str, Any]]] = None
    columns: Optional[List[str]] = None
    total_rows: Optional[int] = None
    preview_rows: Optional[int] = None
    detected_types: Optional[Dict[str, str]] = None
    error: Optional[str] = None

class CSVImportResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    row_count: Optional[int] = None
    column_count: Optional[int] = None
    column_types: Optional[Dict[str, str]] = None
    error: Optional[str] = None

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
    
    # Get insights and ensure proper formatting
    insights = sql_result.get("insights", "Here are the results of your query.")
    
    # If insights is already a string, use it as is
    # If it's a list, join it into a string
    if isinstance(insights, list):
        insights = "\n".join([f"- {insight}" for insight in insights])
    
    # Return the results with explanation, insights, and follow-up questions
    return {
        "success": True,
        "sql": sql_query,
        "data": query_result.get("data", []),
        "explanation": sql_result.get("explanation", "Query executed successfully."),
        "insights": insights,
        "follow_up_questions": sql_result.get("follow_up_questions", [])
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

@app.post("/csv/preview", response_model=CSVPreviewResponse)
async def preview_csv_file(
    file: UploadFile = File(...),
    preview_rows: int = Form(5),
    has_header: bool = Form(True),
    delimiter: str = Form(",")
):
    """
    Preview CSV file contents before importing
    
    Args:
        file: The CSV file to preview
        preview_rows: Number of rows to preview
        has_header: Whether the CSV has a header row
        delimiter: CSV delimiter character
    """
    try:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temp_file:
            # Copy uploaded file to temp file
            shutil.copyfileobj(file.file, temp_file)
            temp_path = temp_file.name
        
        # Get file preview
        preview_result = preview_csv(temp_path, rows=preview_rows, has_header=has_header, delimiter=delimiter)
        
        # Clean up temp file
        os.unlink(temp_path)
        
        # Return preview results
        if preview_result.get("success", False):
            return {
                "success": True,
                "preview_data": preview_result.get("preview_data", []),
                "columns": preview_result.get("columns", []),
                "total_rows": preview_result.get("total_rows", 0),
                "preview_rows": preview_result.get("preview_rows", 0),
                "detected_types": preview_result.get("detected_types", {}),
            }
        else:
            return {
                "success": False,
                "error": preview_result.get("error", "Unknown error previewing CSV file")
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error processing CSV file: {str(e)}"
        }
    finally:
        file.file.close()

@app.post("/csv/import", response_model=CSVImportResponse)
async def import_csv_file(
    file: UploadFile = File(...),
    table_name: str = Form(...),
    if_exists: str = Form("replace"),
    has_header: bool = Form(True),
    delimiter: str = Form(",")
):
    """
    Import CSV file into database table
    
    Args:
        file: The CSV file to import
        table_name: Name of the table to create or update
        if_exists: Action if table exists ('fail', 'replace', or 'append')
        has_header: Whether the CSV has a header row
        delimiter: CSV delimiter character
    """
    try:
        # Validate if_exists parameter
        if if_exists not in ["fail", "replace", "append"]:
            return {
                "success": False,
                "error": "Invalid if_exists value. Must be 'fail', 'replace', or 'append'."
            }
            
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temp_file:
            # Copy uploaded file to temp file
            shutil.copyfileobj(file.file, temp_file)
            temp_path = temp_file.name
        
        # Import CSV to database
        import_result = import_csv_to_table(
            temp_path, 
            table_name=table_name,
            if_exists=if_exists,
            has_header=has_header,
            delimiter=delimiter
        )
        
        # Clean up temp file
        os.unlink(temp_path)
        
        # Return import results
        if import_result.get("success", False):
            return {
                "success": True,
                "message": import_result.get("message", "CSV imported successfully"),
                "row_count": import_result.get("row_count", 0),
                "column_count": import_result.get("column_count", 0),
                "column_types": import_result.get("column_types", {})
            }
        else:
            return {
                "success": False,
                "error": import_result.get("error", "Unknown error importing CSV file")
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error importing CSV file: {str(e)}"
        }
    finally:
        file.file.close()

# === Sample CSV Data Endpoints ===

class SampleTableListResponse(BaseModel):
    tables: List[str]

class SampleTablePreviewResponse(BaseModel):
    success: bool
    preview_data: Optional[List[Dict[str, Any]]] = None
    schema: Optional[str] = None
    relationships: Optional[Dict[str, Dict[str, str]]] = None
    error: Optional[str] = None

class SampleTableImportRequest(BaseModel):
    table_name: str
    if_exists: Literal["replace", "append", "fail"] = "replace"
    import_related: bool = False

class SampleTableImportResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    row_count: Optional[int] = None
    column_count: Optional[int] = None
    tables: Optional[List[str]] = None
    details: Optional[Dict[str, Dict[str, Any]]] = None
    error: Optional[str] = None

@app.get("/csv/sample-tables", response_model=SampleTableListResponse)
async def get_sample_tables():
    """Get a list of available sample tables"""
    tables = get_available_csv_files()
    return {"tables": tables}

@app.get("/csv/sample-preview/{table_name}", response_model=SampleTablePreviewResponse)
async def preview_sample_table(table_name: str):
    """Preview a sample table's data and schema"""
    try:
        # Check if CSV file exists
        available_tables = get_available_csv_files()
        if table_name not in available_tables:
            return {
                "success": False,
                "error": f"CSV file for '{table_name}' not found in data/csv directory"
            }
        
        # Get CSV preview
        preview = get_csv_preview(table_name, rows=10)
        
        if not preview.get("success", False):
            return {
                "success": False,
                "error": preview.get("error", f"Failed to preview data for '{table_name}'")
            }
        
        # Get table schema
        schema = get_csv_table_schema(table_name)
        
        # Get table relationships
        relationships = get_csv_table_relationships(table_name)
        
        return {
            "success": True,
            "preview_data": preview.get("preview_data", []),
            "schema": schema,
            "relationships": relationships
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error previewing data: {str(e)}"
        }

@app.post("/csv/sample-import", response_model=SampleTableImportResponse)
async def import_sample_table(request: SampleTableImportRequest):
    """Import a CSV file into the database"""
    try:
        # Check if CSV file exists
        available_tables = get_available_csv_files()
        if request.table_name not in available_tables:
            return {
                "success": False,
                "error": f"CSV file for '{request.table_name}' not found in data/csv directory"
            }
        
        # Import the table
        result = import_csv_to_db(request.table_name, if_exists=request.if_exists)
        
        if not result.get("success", False):
            return {
                "success": False,
                "error": result.get("error", f"Failed to import '{request.table_name}'")
            }
        
        return {
            "success": True,
            "message": result.get("message", "CSV data imported successfully"),
            "row_count": result.get("row_count", 0),
            "column_count": result.get("column_count", 0)
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error importing CSV data: {str(e)}"
        }

@app.post("/csv/sample-import-related", response_model=SampleTableImportResponse)
async def import_sample_related_tables(request: SampleTableImportRequest):
    """Import a CSV file and all its related tables"""
    try:
        # Check if CSV file exists
        available_tables = get_available_csv_files()
        if request.table_name not in available_tables:
            return {
                "success": False,
                "error": f"CSV file for '{request.table_name}' not found in data/csv directory"
            }
        
        # Import the table and related tables
        result = import_related_tables(request.table_name, if_exists=request.if_exists)
        
        if not result.get("success", False):
            return {
                "success": False,
                "error": result.get("error", f"Failed to import related tables for '{request.table_name}'")
            }
        
        return {
            "success": True,
            "message": result.get("message", "Related tables imported successfully"),
            "tables": result.get("tables", []),
            "details": result.get("details", {})
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error importing related tables: {str(e)}"
        }

@app.post("/csv/create-all-sample-tables", response_model=SampleTableImportResponse)
async def create_all_samples():
    """Import all available CSV files with proper relationships"""
    try:
        result = import_all_available_tables()
        
        if not result.get("success", False):
            return {
                "success": False,
                "error": result.get("error", "Failed to import all CSV files")
            }
        
        return {
            "success": True,
            "message": result.get("message", "All CSV files imported successfully"),
            "tables": result.get("tables", []),
            "details": result.get("details", {})
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error importing all CSV files: {str(e)}"
        }

def start_backend():
    """Start the FastAPI backend server"""
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    start_backend()