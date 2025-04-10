from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union

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

class DatabaseInfo(BaseModel):
    type: str
    uri: str

class MessageResponse(BaseModel):
    success: bool
    message: str