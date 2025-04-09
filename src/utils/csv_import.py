"""
CSV Import Utility for SQL Chatbot

This module provides functions to import CSV files into the database.
It can create new tables or append to existing ones based on CSV data.
"""
import csv
import os
import pandas as pd
from sqlalchemy import create_engine, MetaData, Table, Column, String, Integer, Float, DateTime
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Dict, Any, Optional, Tuple, Union

from src.db.database import get_active_connection


def detect_column_types(df: pd.DataFrame) -> Dict[str, str]:
    """
    Detect appropriate SQL column types based on DataFrame data types.
    
    Args:
        df: Pandas DataFrame containing the data
        
    Returns:
        Dictionary mapping column names to SQL type names
    """
    type_map = {}
    
    for col in df.columns:
        # Try to infer basic types
        if pd.api.types.is_integer_dtype(df[col]):
            type_map[col] = "INTEGER"
        elif pd.api.types.is_float_dtype(df[col]):
            type_map[col] = "FLOAT"
        elif pd.api.types.is_datetime64_any_dtype(df[col]):
            type_map[col] = "TIMESTAMP"
        else:
            # Default to TEXT for strings and other types
            type_map[col] = "TEXT"
            
    return type_map


def clean_column_names(columns: List[str]) -> List[str]:
    """
    Clean column names to be SQL-compatible.
    
    Args:
        columns: List of column names from CSV
        
    Returns:
        List of cleaned column names
    """
    clean_names = []
    
    for col in columns:
        # Replace spaces and special characters with underscores
        cleaned = col.strip().lower().replace(' ', '_')
        # Remove any non-alphanumeric characters except underscores
        cleaned = ''.join(c if c.isalnum() or c == '_' else '_' for c in cleaned)
        # Ensure it doesn't start with a number
        if cleaned and cleaned[0].isdigit():
            cleaned = 'col_' + cleaned
        clean_names.append(cleaned)
        
    return clean_names


def read_csv_to_df(file_path: str, has_header: bool = True, delimiter: str = ',') -> pd.DataFrame:
    """
    Read a CSV file into a pandas DataFrame.
    
    Args:
        file_path: Path to the CSV file
        has_header: Whether the CSV has a header row
        delimiter: CSV delimiter character
        
    Returns:
        Pandas DataFrame with the CSV data
    """
    try:
        if has_header:
            df = pd.read_csv(file_path, delimiter=delimiter)
        else:
            df = pd.read_csv(file_path, delimiter=delimiter, header=None, 
                            prefix='column_')
            
        # Clean column names
        df.columns = clean_column_names(df.columns.tolist())
        
        return df
    except Exception as e:
        raise Exception(f"Error reading CSV file: {str(e)}")


def import_csv_to_table(
    file_path: str, 
    table_name: str, 
    if_exists: str = 'replace', 
    has_header: bool = True,
    delimiter: str = ',',
    custom_dtypes: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    Import a CSV file into a database table.
    
    Args:
        file_path: Path to the CSV file
        table_name: Name of the table to create or update
        if_exists: Action if table exists ('fail', 'replace', or 'append')
        has_header: Whether the CSV has a header row
        delimiter: CSV delimiter character
        custom_dtypes: Optional dictionary mapping column names to SQLite types
        
    Returns:
        Dictionary with import results
    """
    try:
        # Get the active database connection
        engine = get_active_connection()
        
        # Read the CSV file
        df = read_csv_to_df(file_path, has_header, delimiter)
        
        # Detect column types if not provided
        if custom_dtypes is None:
            detected_types = detect_column_types(df)
        else:
            detected_types = custom_dtypes
            
        # Import the data
        df.to_sql(table_name, engine, if_exists=if_exists, index=False, 
                 dtype=detected_types if custom_dtypes else None)
        
        return {
            "success": True,
            "message": f"Successfully imported {len(df)} rows into table '{table_name}'",
            "row_count": len(df),
            "column_count": len(df.columns),
            "column_types": detected_types
        }
    except SQLAlchemyError as e:
        return {
            "success": False,
            "error": f"Database error: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error importing CSV: {str(e)}"
        }


def preview_csv(file_path: str, rows: int = 5, has_header: bool = True, delimiter: str = ',') -> Dict[str, Any]:
    """
    Generate a preview of a CSV file.
    
    Args:
        file_path: Path to the CSV file
        rows: Number of rows to preview
        has_header: Whether the CSV has a header row
        delimiter: CSV delimiter character
        
    Returns:
        Dictionary with preview data
    """
    try:
        df = read_csv_to_df(file_path, has_header, delimiter)
        preview_df = df.head(rows)
        
        column_types = detect_column_types(df)
        
        return {
            "success": True,
            "preview_data": preview_df.to_dict(orient='records'),
            "columns": df.columns.tolist(),
            "total_rows": len(df),
            "preview_rows": len(preview_df),
            "detected_types": column_types
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error generating preview: {str(e)}"
        }