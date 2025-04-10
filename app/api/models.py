from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union

# Query models
class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    success: bool
    sql: Optional[str] = None
    data: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None

# Schema models
class SchemaRequest(BaseModel):
    table_name: Optional[str] = None

class TableListResponse(BaseModel):
    tables: List[str]

class SchemaResponse(BaseModel):
    schema: Dict[str, Any]

# Simple database info model
class DatabaseInfo(BaseModel):
    type: str
    uri: str

# General response model
class MessageResponse(BaseModel):
    success: bool
    message: str