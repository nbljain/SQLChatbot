"""
SQL Chatbot - Main Entry Point

This file serves as the main entry point for running the complete SQL Chatbot application.
It coordinates starting both the FastAPI backend and Streamlit frontend components,
and can optionally set up the database with sample data.

Usage:
    python main.py            # Start the application
    python main.py setup      # Set up the database only

Components:
    - FastAPI backend (runs on port 8000)
    - Streamlit frontend (runs on port 5000)
    - Database with employee and review data
"""
import sys
from src.main import run_application, setup_database

if __name__ == "__main__":
    # Check if we should setup the database first
    if len(sys.argv) > 1 and sys.argv[1] == "setup":
        print("Setting up database...")
        if setup_database():
            print("Database setup complete!")
            sys.exit(0)
        else:
            print("Database setup failed!")
            sys.exit(1)
    
    # Run the complete application
    run_application()