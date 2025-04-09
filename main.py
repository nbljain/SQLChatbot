"""
SQL Chatbot - Main Entry Point
"""
import sys
from src.main import run_backend, run_frontend, setup_database
import multiprocessing

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