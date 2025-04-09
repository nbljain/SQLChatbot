"""
CSV Data Management for SQL Chatbot

This module provides a structured approach to handle CSV data with relationships 
without requiring file uploads. It creates sample data that can be imported 
directly into the database.

The module provides:
1. Sample CSV data for different entities
2. Relationship definitions between tables
3. Functions to create tables with proper foreign key relationships
"""

import pandas as pd
import os
import json
from typing import Dict, List, Any, Optional
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime, date
from src.db.database import get_active_connection

# Define sample CSV data for different entities
SAMPLE_DATA = {
    # Customer data
    "customers": [
        {"id": 1, "name": "John Smith", "email": "john@example.com", "phone": "555-1234", "address": "123 Main St", "city": "New York", "created_at": "2023-01-05"},
        {"id": 2, "name": "Emily Johnson", "email": "emily@example.com", "phone": "555-5678", "address": "456 Oak Ave", "city": "Los Angeles", "created_at": "2023-02-10"},
        {"id": 3, "name": "Michael Brown", "email": "michael@example.com", "phone": "555-9012", "address": "789 Pine Rd", "city": "Chicago", "created_at": "2023-03-15"},
        {"id": 4, "name": "Sarah Davis", "email": "sarah@example.com", "phone": "555-3456", "address": "101 Elm St", "city": "Houston", "created_at": "2023-04-20"},
        {"id": 5, "name": "David Wilson", "email": "david@example.com", "phone": "555-7890", "address": "202 Maple Ave", "city": "Phoenix", "created_at": "2023-05-25"}
    ],
    
    # Product data
    "products": [
        {"id": 1, "name": "Laptop", "category": "Electronics", "price": 1200.00, "stock": 15, "created_at": "2023-01-10"},
        {"id": 2, "name": "Smartphone", "category": "Electronics", "price": 800.00, "stock": 25, "created_at": "2023-01-15"},
        {"id": 3, "name": "Coffee Table", "category": "Furniture", "price": 300.00, "stock": 10, "created_at": "2023-02-05"},
        {"id": 4, "name": "Desk Chair", "category": "Furniture", "price": 150.00, "stock": 20, "created_at": "2023-02-20"},
        {"id": 5, "name": "Headphones", "category": "Electronics", "price": 100.00, "stock": 30, "created_at": "2023-03-10"},
        {"id": 6, "name": "Bookshelf", "category": "Furniture", "price": 250.00, "stock": 8, "created_at": "2023-03-25"},
        {"id": 7, "name": "Tablet", "category": "Electronics", "price": 500.00, "stock": 12, "created_at": "2023-04-05"},
        {"id": 8, "name": "Sofa", "category": "Furniture", "price": 900.00, "stock": 5, "created_at": "2023-04-15"}
    ],
    
    # Order data
    "orders": [
        {"id": 1, "customer_id": 1, "order_date": "2023-02-01", "total_amount": 1200.00, "status": "Delivered"},
        {"id": 2, "customer_id": 2, "order_date": "2023-03-05", "total_amount": 950.00, "status": "Delivered"},
        {"id": 3, "customer_id": 3, "order_date": "2023-04-10", "total_amount": 300.00, "status": "Shipped"},
        {"id": 4, "customer_id": 1, "order_date": "2023-05-15", "total_amount": 650.00, "status": "Processing"},
        {"id": 5, "customer_id": 4, "order_date": "2023-06-01", "total_amount": 1100.00, "status": "Delivered"},
        {"id": 6, "customer_id": 5, "order_date": "2023-06-15", "total_amount": 800.00, "status": "Shipped"},
        {"id": 7, "customer_id": 2, "order_date": "2023-07-01", "total_amount": 400.00, "status": "Processing"}
    ],
    
    # Order items data
    "order_items": [
        {"id": 1, "order_id": 1, "product_id": 1, "quantity": 1, "price": 1200.00},
        {"id": 2, "order_id": 2, "product_id": 2, "quantity": 1, "price": 800.00},
        {"id": 3, "order_id": 2, "product_id": 5, "quantity": 1, "price": 100.00},
        {"id": 4, "order_id": 2, "product_id": 6, "quantity": 0.2, "price": 50.00},
        {"id": 5, "order_id": 3, "product_id": 3, "quantity": 1, "price": 300.00},
        {"id": 6, "order_id": 4, "product_id": 7, "quantity": 1, "price": 500.00},
        {"id": 7, "order_id": 4, "product_id": 5, "quantity": 1, "price": 100.00},
        {"id": 8, "order_id": 4, "product_id": 6, "quantity": 0.2, "price": 50.00},
        {"id": 9, "order_id": 5, "product_id": 2, "quantity": 1, "price": 800.00},
        {"id": 10, "order_id": 5, "product_id": 5, "quantity": 3, "price": 300.00},
        {"id": 11, "order_id": 6, "product_id": 2, "quantity": 1, "price": 800.00},
        {"id": 12, "order_id": 7, "product_id": 3, "quantity": 1, "price": 300.00},
        {"id": 13, "order_id": 7, "product_id": 5, "quantity": 1, "price": 100.00}
    ],
    
    # Employee data
    "employees": [
        {"id": 1, "first_name": "Robert", "last_name": "Johnson", "email": "robert@example.com", "department": "Sales", "hire_date": "2021-03-15", "salary": 60000.00},
        {"id": 2, "first_name": "Jennifer", "last_name": "Smith", "email": "jennifer@example.com", "department": "Marketing", "hire_date": "2020-08-10", "salary": 65000.00},
        {"id": 3, "first_name": "William", "last_name": "Brown", "email": "william@example.com", "department": "IT", "hire_date": "2019-11-20", "salary": 75000.00},
        {"id": 4, "first_name": "Maria", "last_name": "Garcia", "email": "maria@example.com", "department": "HR", "hire_date": "2022-01-05", "salary": 62000.00},
        {"id": 5, "first_name": "James", "last_name": "Miller", "email": "james@example.com", "department": "Finance", "hire_date": "2020-05-15", "salary": 70000.00},
        {"id": 6, "first_name": "Elizabeth", "last_name": "Davis", "email": "elizabeth@example.com", "department": "Sales", "hire_date": "2021-07-22", "salary": 61000.00},
        {"id": 7, "first_name": "Michael", "last_name": "Wilson", "email": "michael@example.com", "department": "IT", "hire_date": "2019-06-30", "salary": 78000.00},
        {"id": 8, "first_name": "Susan", "last_name": "Anderson", "email": "susan@example.com", "department": "Marketing", "hire_date": "2022-02-18", "salary": 63000.00}
    ],
    
    # Project data
    "projects": [
        {"id": 1, "name": "Website Redesign", "start_date": "2023-01-10", "end_date": "2023-04-15", "budget": 50000.00, "status": "Completed"},
        {"id": 2, "name": "Mobile App Development", "start_date": "2023-02-20", "end_date": "2023-07-30", "budget": 75000.00, "status": "In Progress"},
        {"id": 3, "name": "Database Migration", "start_date": "2023-03-05", "end_date": "2023-05-20", "budget": 30000.00, "status": "Completed"},
        {"id": 4, "name": "Digital Marketing Campaign", "start_date": "2023-04-10", "end_date": "2023-09-30", "budget": 45000.00, "status": "In Progress"},
        {"id": 5, "name": "Office Renovation", "start_date": "2023-05-15", "end_date": "2023-08-15", "budget": 100000.00, "status": "In Progress"}
    ],
    
    # Project assignments data
    "assignments": [
        {"id": 1, "project_id": 1, "employee_id": 2, "role": "Project Manager", "assigned_date": "2023-01-10"},
        {"id": 2, "project_id": 1, "employee_id": 3, "role": "Developer", "assigned_date": "2023-01-15"},
        {"id": 3, "project_id": 1, "employee_id": 8, "role": "Designer", "assigned_date": "2023-01-20"},
        {"id": 4, "project_id": 2, "employee_id": 7, "role": "Project Manager", "assigned_date": "2023-02-20"},
        {"id": 5, "project_id": 2, "employee_id": 3, "role": "Developer", "assigned_date": "2023-02-25"},
        {"id": 6, "project_id": 3, "employee_id": 5, "role": "Project Manager", "assigned_date": "2023-03-05"},
        {"id": 7, "project_id": 3, "employee_id": 7, "role": "Database Admin", "assigned_date": "2023-03-10"},
        {"id": 8, "project_id": 4, "employee_id": 2, "role": "Project Manager", "assigned_date": "2023-04-10"},
        {"id": 9, "project_id": 4, "employee_id": 8, "role": "Marketing Specialist", "assigned_date": "2023-04-15"},
        {"id": 10, "project_id": 5, "employee_id": 4, "role": "Project Manager", "assigned_date": "2023-05-15"},
        {"id": 11, "project_id": 5, "employee_id": 5, "role": "Finance Analyst", "assigned_date": "2023-05-20"}
    ],
    
    # Customer feedback data
    "feedback": [
        {"id": 1, "customer_id": 1, "order_id": 1, "rating": 5, "comment": "Excellent product and fast delivery", "created_at": "2023-02-10"},
        {"id": 2, "customer_id": 2, "order_id": 2, "rating": 4, "comment": "Good product but packaging could be better", "created_at": "2023-03-15"},
        {"id": 3, "customer_id": 3, "order_id": 3, "rating": 5, "comment": "Very satisfied with my purchase", "created_at": "2023-04-20"},
        {"id": 4, "customer_id": 1, "order_id": 4, "rating": 3, "comment": "Product is good but delivery was delayed", "created_at": "2023-05-25"},
        {"id": 5, "customer_id": 4, "order_id": 5, "rating": 5, "comment": "Perfect in every way!", "created_at": "2023-06-10"}
    ]
}

# Define table relationships
TABLE_RELATIONSHIPS = {
    "customers": {
        "orders": {"foreign_key": "customer_id", "relationship": "one-to-many"},
        "feedback": {"foreign_key": "customer_id", "relationship": "one-to-many"}
    },
    "orders": {
        "order_items": {"foreign_key": "order_id", "relationship": "one-to-many"},
        "feedback": {"foreign_key": "order_id", "relationship": "one-to-one"}
    },
    "products": {
        "order_items": {"foreign_key": "product_id", "relationship": "one-to-many"}
    },
    "employees": {
        "assignments": {"foreign_key": "employee_id", "relationship": "one-to-many"}
    },
    "projects": {
        "assignments": {"foreign_key": "project_id", "relationship": "one-to-many"}
    }
}

# Define column types for each table
TABLE_COLUMN_TYPES = {
    "customers": {
        "id": "INTEGER PRIMARY KEY",
        "name": "TEXT",
        "email": "TEXT",
        "phone": "TEXT",
        "address": "TEXT",
        "city": "TEXT",
        "created_at": "DATE"
    },
    "products": {
        "id": "INTEGER PRIMARY KEY",
        "name": "TEXT",
        "category": "TEXT",
        "price": "REAL",
        "stock": "INTEGER",
        "created_at": "DATE"
    },
    "orders": {
        "id": "INTEGER PRIMARY KEY",
        "customer_id": "INTEGER",
        "order_date": "DATE",
        "total_amount": "REAL",
        "status": "TEXT",
        "FOREIGN KEY(customer_id)": "REFERENCES customers(id)"
    },
    "order_items": {
        "id": "INTEGER PRIMARY KEY",
        "order_id": "INTEGER",
        "product_id": "INTEGER",
        "quantity": "REAL",
        "price": "REAL",
        "FOREIGN KEY(order_id)": "REFERENCES orders(id)",
        "FOREIGN KEY(product_id)": "REFERENCES products(id)"
    },
    "employees": {
        "id": "INTEGER PRIMARY KEY",
        "first_name": "TEXT",
        "last_name": "TEXT",
        "email": "TEXT",
        "department": "TEXT",
        "hire_date": "DATE",
        "salary": "REAL"
    },
    "projects": {
        "id": "INTEGER PRIMARY KEY",
        "name": "TEXT",
        "start_date": "DATE",
        "end_date": "DATE",
        "budget": "REAL",
        "status": "TEXT"
    },
    "assignments": {
        "id": "INTEGER PRIMARY KEY",
        "project_id": "INTEGER",
        "employee_id": "INTEGER",
        "role": "TEXT",
        "assigned_date": "DATE",
        "FOREIGN KEY(project_id)": "REFERENCES projects(id)",
        "FOREIGN KEY(employee_id)": "REFERENCES employees(id)"
    },
    "feedback": {
        "id": "INTEGER PRIMARY KEY",
        "customer_id": "INTEGER",
        "order_id": "INTEGER",
        "rating": "INTEGER",
        "comment": "TEXT",
        "created_at": "DATE",
        "FOREIGN KEY(customer_id)": "REFERENCES customers(id)",
        "FOREIGN KEY(order_id)": "REFERENCES orders(id)"
    }
}

def get_table_data(table_name: str) -> List[Dict[str, Any]]:
    """Get sample data for a specific table"""
    return SAMPLE_DATA.get(table_name, [])

def get_table_relationships(table_name: str) -> Dict[str, Dict[str, str]]:
    """Get relationships for a specific table"""
    return TABLE_RELATIONSHIPS.get(table_name, {})

def get_all_tables() -> List[str]:
    """Get a list of all available tables"""
    return list(SAMPLE_DATA.keys())

def get_column_types(table_name: str) -> Dict[str, str]:
    """Get column types for a specific table"""
    return TABLE_COLUMN_TYPES.get(table_name, {})

def import_table_to_db(table_name: str, if_exists: str = 'replace') -> Dict[str, Any]:
    """Import a sample table into the database"""
    if table_name not in SAMPLE_DATA:
        return {"success": False, "error": f"Table '{table_name}' not found in sample data"}
    
    try:
        # Get the active database connection
        engine = get_active_connection()
        if not engine:
            return {"success": False, "error": "No active database connection"}
        
        # Convert sample data to DataFrame
        df = pd.DataFrame(SAMPLE_DATA[table_name])
        
        # Import to database
        df.to_sql(table_name, engine, if_exists=if_exists, index=False)
        
        return {
            "success": True, 
            "message": f"Imported {len(df)} rows into table '{table_name}'",
            "row_count": len(df),
            "column_count": len(df.columns)
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def import_related_tables(main_table: str, if_exists: str = 'replace') -> Dict[str, Any]:
    """
    Import a table and all its related tables into the database
    
    This function will create tables in the correct order to maintain referential integrity
    """
    if main_table not in SAMPLE_DATA:
        return {"success": False, "error": f"Table '{main_table}' not found in sample data"}
    
    try:
        # Get the active database connection
        engine = get_active_connection()
        if not engine:
            return {"success": False, "error": "No active database connection"}
        
        # Determine the order of table creation
        tables_to_create = get_table_creation_order(main_table)
        
        # Import each table in the correct order
        results = {}
        for table in tables_to_create:
            df = pd.DataFrame(SAMPLE_DATA[table])
            df.to_sql(table, engine, if_exists=if_exists, index=False)
            results[table] = {
                "success": True,
                "row_count": len(df),
                "column_count": len(df.columns)
            }
        
        return {
            "success": True,
            "message": f"Imported {len(tables_to_create)} related tables",
            "tables": tables_to_create,
            "details": results
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_table_creation_order(main_table: str) -> List[str]:
    """
    Determine the correct order to create tables to maintain referential integrity
    
    Uses a basic topological sort algorithm to handle dependencies
    """
    # Build a dependency graph
    graph = {}
    for table, relations in TABLE_RELATIONSHIPS.items():
        if table not in graph:
            graph[table] = []
        
        for related_table, info in relations.items():
            if related_table not in graph:
                graph[related_table] = []
            
            # Add dependency: related_table depends on table
            graph[related_table].append(table)
    
    # Helper function for topological sort
    def topo_sort_util(v, visited, temp, result):
        # Mark current node as temporarily visited
        temp[v] = True
        
        # Process all adjacent vertices
        for neighbor in graph.get(v, []):
            if neighbor in temp and temp[neighbor]:
                # Found a cycle
                return False
            if neighbor not in visited:
                if not topo_sort_util(neighbor, visited, temp, result):
                    return False
        
        # Add current vertex to result and mark as visited
        temp[v] = False
        visited[v] = True
        result.append(v)
        return True
    
    # Perform topological sort
    visited = {}
    temp = {}
    result = []
    
    # Ensure main table and all its related tables are included
    tables_to_process = [main_table]
    
    # Add all directly related tables
    for table in TABLE_RELATIONSHIPS.get(main_table, {}):
        tables_to_process.append(table)
    
    # Add tables that have relationships with the related tables
    for related_table in list(tables_to_process):
        for table in TABLE_RELATIONSHIPS.get(related_table, {}):
            if table not in tables_to_process:
                tables_to_process.append(table)
    
    # Process all tables
    for v in tables_to_process:
        if v not in visited:
            if not topo_sort_util(v, visited, temp, result):
                # If there's a cycle, just return the list of tables
                return tables_to_process
    
    # Reverse to get the correct order
    result.reverse()
    
    # Only return tables that are in tables_to_process
    return [table for table in result if table in tables_to_process]

def create_table_schema(table_name: str) -> str:
    """Generate SQL CREATE TABLE statement for a table"""
    if table_name not in TABLE_COLUMN_TYPES:
        return ""
    
    columns = []
    for column, data_type in TABLE_COLUMN_TYPES[table_name].items():
        columns.append(f"{column} {data_type}")
    
    sql = f"CREATE TABLE IF NOT EXISTS {table_name} (\n"
    sql += ",\n".join(f"    {column}" for column in columns)
    sql += "\n);"
    
    return sql

def create_all_sample_tables() -> Dict[str, Any]:
    """Create all sample tables in the database with proper relationships"""
    try:
        # Get the active database connection
        engine = get_active_connection()
        if not engine:
            return {"success": False, "error": "No active database connection"}
        
        # Get table creation order
        tables = get_table_creation_order("customers")
        
        # Make sure all tables are included
        for table in SAMPLE_DATA:
            if table not in tables:
                tables.append(table)
        
        # Create tables in the correct order
        results = {}
        for table in tables:
            # Generate and execute CREATE TABLE statement
            create_sql = create_table_schema(table)
            if create_sql:
                engine.execute(create_sql)
                
                # Import data
                df = pd.DataFrame(SAMPLE_DATA[table])
                df.to_sql(table, engine, if_exists='replace', index=False)
                
                results[table] = {
                    "success": True,
                    "row_count": len(df),
                    "column_count": len(df.columns)
                }
        
        return {
            "success": True,
            "message": "Created all sample tables with relationships",
            "tables": tables,
            "details": results
        }
    except Exception as e:
        return {"success": False, "error": str(e)}