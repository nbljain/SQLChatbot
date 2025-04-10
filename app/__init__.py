# Initialize the app package
from app.database import (
    connect_to_database, 
    get_active_connection,
    get_table_names,
    get_table_schema,
    get_all_table_schemas,
    execute_sql_query,
    get_active_connection_info,
    get_all_connections_info,
    add_database_connection,
    remove_database_connection
)

from app.models import generate_sql_query

__all__ = [
    'connect_to_database',
    'get_active_connection',
    'get_table_names',
    'get_table_schema',
    'get_all_table_schemas',
    'execute_sql_query',
    'get_active_connection_info',
    'get_all_connections_info',
    'add_database_connection',
    'remove_database_connection',
    'generate_sql_query'
]