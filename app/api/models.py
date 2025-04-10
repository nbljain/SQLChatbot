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

# Database connection models
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