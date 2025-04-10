import os
import logging
import uvicorn
import threading
import subprocess
import time
from init_db import initialize_database

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def start_fastapi_backend():
    """Start the FastAPI backend server"""
    logger.info("Starting FastAPI backend...")
    import fastapi_backend
    uvicorn.run("fastapi_backend:app", host="0.0.0.0", port=8000)

def start_streamlit_frontend():
    """Start the Streamlit frontend"""
    logger.info("Starting Streamlit frontend...")
    subprocess.run(["streamlit", "run", "app.py", "--server.port", "5000", "--server.address", "0.0.0.0", "--server.headless", "true"])

def main():
    """Main entry point for the application"""
    # Initialize the database
    logger.info("Initializing database...")
    initialize_database()
    
    # Start the FastAPI backend in a separate thread
    backend_thread = threading.Thread(target=start_fastapi_backend, daemon=True)
    backend_thread.start()
    
    # Wait a bit for the backend to start up
    logger.info("Waiting for backend to start...")
    time.sleep(3)
    
    # Start the Streamlit frontend (this will block until the frontend exits)
    start_streamlit_frontend()

if __name__ == "__main__":
    main()