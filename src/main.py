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
        from src.db.setup_database import setup_database
        setup_database()
    except Exception as e:
        print(f"Error setting up database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Check if we should setup the database first
    if len(sys.argv) > 1 and sys.argv[1] == "setup":
        print("Setting up database...")
        setup_database()
        print("Database setup complete!")
        sys.exit(0)
    
    # Start backend in a separate process
    backend_process = multiprocessing.Process(target=run_backend)
    backend_process.start()
    
    # Run frontend in main process
    run_frontend()