"""
CSV File Loader Utility for SQL Chatbot

This module provides functions to load CSV files from the data/csv directory 
into the database. It handles relationships between tables and ensures proper 
foreign key constraints.
"""

import os
import pandas as pd
import sqlite3
from typing import Dict, List, Any, Optional, Union
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
CSV_DIR = Path("data/csv")
DB_FILE = "sql_chatbot.db"

# SQLite connection
def get_sqlite_connection(db_file: str = DB_FILE) -> sqlite3.Connection:
    """Get a SQLite database connection"""
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    return conn

# Table schema definitions with foreign keys
TABLE_SCHEMAS = {
    "customers": """
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY,
        name TEXT,
        email TEXT,
        phone TEXT,
        address TEXT,
        city TEXT,
        created_at DATE
    )
    """,
    
    "products": """
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY,
        name TEXT,
        category TEXT,
        price REAL,
        stock INTEGER,
        created_at DATE
    )
    """,
    
    "orders": """
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY,
        customer_id INTEGER,
        order_date DATE,
        total_amount REAL,
        status TEXT,
        FOREIGN KEY (customer_id) REFERENCES customers (id)
    )
    """,
    
    "order_items": """
    CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY,
        order_id INTEGER,
        product_id INTEGER,
        quantity REAL,
        price REAL,
        FOREIGN KEY (order_id) REFERENCES orders (id),
        FOREIGN KEY (product_id) REFERENCES products (id)
    )
    """,
    
    "employees": """
    CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY,
        first_name TEXT,
        last_name TEXT,
        email TEXT,
        department TEXT,
        hire_date DATE,
        salary REAL
    )
    """
}

# Table relationships for determining import order
TABLE_RELATIONSHIPS = {
    "customers": [],  # No dependencies
    "products": [],   # No dependencies
    "orders": ["customers"],  # Depends on customers
    "order_items": ["orders", "products"],  # Depends on orders and products
    "employees": []   # No dependencies
}

def get_available_csv_files() -> List[str]:
    """Get list of available CSV files in the data directory"""
    if not os.path.exists(CSV_DIR):
        logger.warning(f"CSV directory '{CSV_DIR}' does not exist")
        return []
    
    csv_files = [f.stem for f in CSV_DIR.glob("*.csv")]
    return csv_files

def check_csv_file_exists(table_name: str) -> bool:
    """Check if a CSV file exists for a table"""
    csv_path = CSV_DIR / f"{table_name}.csv"
    return csv_path.exists()

def get_csv_preview(table_name: str, rows: int = 5) -> Dict[str, Any]:
    """Get a preview of a CSV file"""
    csv_path = CSV_DIR / f"{table_name}.csv"
    
    if not csv_path.exists():
        return {
            "success": False,
            "error": f"CSV file for '{table_name}' not found"
        }
    
    try:
        df = pd.read_csv(csv_path)
        preview_data = df.head(rows).to_dict(orient='records')
        
        return {
            "success": True,
            "preview_data": preview_data,
            "columns": df.columns.tolist(),
            "total_rows": len(df),
            "preview_rows": min(rows, len(df))
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error reading CSV file: {str(e)}"
        }

def create_tables(conn: sqlite3.Connection, tables: Optional[List[str]] = None) -> bool:
    """Create database tables with the proper schema"""
    cursor = conn.cursor()
    
    if tables is None:
        tables = list(TABLE_SCHEMAS.keys())
    
    try:
        for table in tables:
            if table in TABLE_SCHEMAS:
                cursor.execute(TABLE_SCHEMAS[table])
        
        conn.commit()
        return True
    except Exception as e:
        logger.error(f"Error creating tables: {e}")
        conn.rollback()
        return False

def import_csv_to_db(table_name: str, if_exists: str = 'replace', db_file: str = DB_FILE) -> Dict[str, Any]:
    """Import a CSV file into the database"""
    csv_path = CSV_DIR / f"{table_name}.csv"
    
    if not csv_path.exists():
        return {
            "success": False,
            "error": f"CSV file for '{table_name}' not found"
        }
    
    try:
        # Read CSV file
        df = pd.read_csv(csv_path)
        
        # Connect to database
        conn = get_sqlite_connection(db_file)
        
        # Create table if needed
        if table_name in TABLE_SCHEMAS:
            create_tables(conn, [table_name])
        
        # Import data
        if if_exists == 'replace':
            # If replacing, first delete existing data
            conn.execute(f"DELETE FROM {table_name}")
        elif if_exists == 'fail':
            # Check if table has data
            count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
            if count > 0:
                return {
                    "success": False,
                    "error": f"Table '{table_name}' already has data and if_exists='fail'"
                }
        
        # Insert data
        df.to_sql(table_name, conn, if_exists='append', index=False)
        
        # Close connection
        conn.close()
        
        return {
            "success": True,
            "message": f"Successfully imported {len(df)} rows into '{table_name}'",
            "row_count": len(df),
            "column_count": len(df.columns)
        }
    except Exception as e:
        logger.error(f"Error importing CSV file: {e}")
        return {
            "success": False,
            "error": f"Error importing CSV file: {str(e)}"
        }

def get_import_order(table_names: List[str]) -> List[str]:
    """Get the correct order to import tables to maintain referential integrity"""
    # Start with tables that have no dependencies
    ordered_tables = []
    remaining_tables = table_names.copy()
    
    # Keep going until we've processed all tables
    while remaining_tables:
        added_table = False
        
        for table in remaining_tables[:]:  # Use a copy for iteration
            # Check if all dependencies are already in the ordered list
            deps = TABLE_RELATIONSHIPS.get(table, [])
            deps_satisfied = all(dep in ordered_tables for dep in deps if dep in table_names)
            
            if deps_satisfied:
                ordered_tables.append(table)
                remaining_tables.remove(table)
                added_table = True
        
        if not added_table and remaining_tables:
            # If we couldn't add any table but still have tables,
            # there's a circular dependency or missing tables
            logger.warning(f"Circular dependency or missing tables detected: {remaining_tables}")
            ordered_tables.extend(remaining_tables)
            break
    
    return ordered_tables

def import_related_tables(main_table: str, if_exists: str = 'replace', db_file: str = DB_FILE) -> Dict[str, Any]:
    """Import a table and all its related tables"""
    # Determine which tables to import
    available_tables = get_available_csv_files()
    
    if main_table not in available_tables:
        return {
            "success": False,
            "error": f"CSV file for '{main_table}' not found"
        }
    
    # Get all tables related to the main table
    tables_to_import = [main_table]
    
    # Add direct dependencies
    for table, deps in TABLE_RELATIONSHIPS.items():
        if main_table in deps and table in available_tables:
            tables_to_import.append(table)
    
    # Add tables that depend on main table
    for table, deps in TABLE_RELATIONSHIPS.items():
        if table not in tables_to_import and deps and any(dep == main_table for dep in deps) and table in available_tables:
            tables_to_import.append(table)
    
    # Get correct import order
    ordered_tables = get_import_order(tables_to_import)
    
    # Create database connection
    conn = get_sqlite_connection(db_file)
    
    # Create all tables first
    create_tables(conn, ordered_tables)
    conn.close()
    
    # Import each table
    results = {}
    for table in ordered_tables:
        result = import_csv_to_db(table, if_exists, db_file)
        results[table] = result
    
    # Check if any imports failed
    failed_imports = [table for table, result in results.items() if not result.get("success", False)]
    
    if failed_imports:
        return {
            "success": False,
            "error": f"Failed to import some tables: {', '.join(failed_imports)}",
            "details": results
        }
    
    return {
        "success": True,
        "message": f"Successfully imported {len(ordered_tables)} related tables",
        "tables": ordered_tables,
        "details": results
    }

def import_all_available_tables(if_exists: str = 'replace', db_file: str = DB_FILE) -> Dict[str, Any]:
    """Import all available CSV files into the database"""
    available_tables = get_available_csv_files()
    
    if not available_tables:
        return {
            "success": False,
            "error": "No CSV files found in data directory"
        }
    
    # Get correct import order
    ordered_tables = get_import_order(available_tables)
    
    # Create database connection
    conn = get_sqlite_connection(db_file)
    
    # Create all tables first
    create_tables(conn, ordered_tables)
    conn.close()
    
    # Import each table
    results = {}
    for table in ordered_tables:
        result = import_csv_to_db(table, if_exists, db_file)
        results[table] = result
    
    # Check if any imports failed
    failed_imports = [table for table, result in results.items() if not result.get("success", False)]
    
    if failed_imports:
        return {
            "success": False,
            "error": f"Failed to import some tables: {', '.join(failed_imports)}",
            "details": results
        }
    
    return {
        "success": True,
        "message": f"Successfully imported {len(ordered_tables)} tables",
        "tables": ordered_tables,
        "details": results
    }

def get_table_schema(table_name: str) -> str:
    """Get the SQL schema for a table"""
    if table_name in TABLE_SCHEMAS:
        return TABLE_SCHEMAS[table_name]
    return ""

def get_table_relationships(table_name: str) -> Dict[str, str]:
    """Get the relationships for a table"""
    relationships = {}
    
    # Tables that this table depends on
    if table_name in TABLE_RELATIONSHIPS:
        for dep in TABLE_RELATIONSHIPS[table_name]:
            relationships[dep] = {
                "relationship": "depends on",
                "direction": "incoming"
            }
    
    # Tables that depend on this table
    for table, deps in TABLE_RELATIONSHIPS.items():
        if table_name in deps:
            relationships[table] = {
                "relationship": "depended on by",
                "direction": "outgoing"
            }
    
    return relationships