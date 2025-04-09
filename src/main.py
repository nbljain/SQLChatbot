"""
SQL Chatbot - Main Implementation Module

This module provides the core functionality to run the SQL Chatbot application.
It includes functions to:
1. Run the FastAPI backend server
2. Run the Streamlit frontend interface
3. Set up the database with sample data

These functions can be imported and used by other modules, or this module can be run directly.
"""
import sys
import os
import multiprocessing
import time

def run_backend():
    """Run the FastAPI backend"""
    try:
        from src.api.fastapi_backend import start_backend
        start_backend()
    except Exception as e:
        print(f"Error starting backend: {e}")
        sys.exit(1)

def run_frontend():
    """Run the Streamlit frontend"""
    try:
        # Use streamlit run command to start the frontend
        import streamlit.web.cli as stcli
        
        # Add a delay to ensure backend starts first
        time.sleep(3)
        
        # Set directory to src/frontend for the app
        frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")
        os.chdir(frontend_dir)
        
        # Run Streamlit app
        sys.argv = ["streamlit", "run", "app.py", "--server.port", "5000"]
        sys.exit(stcli.main())
    except Exception as e:
        print(f"Error starting frontend: {e}")
        sys.exit(1)

def setup_database():
    """Setup the SQLite database with sample data"""
    try:
        from src.db.setup_database import setup_database as setup_db_impl
        setup_db_impl()
        return True
    except Exception as e:
        print(f"Error setting up database: {e}")
        return False

def run_application():
    """Run the complete application (both backend and frontend)"""
    # Start backend in a separate process
    backend_process = multiprocessing.Process(target=run_backend)
    backend_process.start()
    
    # Run frontend in main process
    run_frontend()
    
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
    
    # Run the full application
    run_application()