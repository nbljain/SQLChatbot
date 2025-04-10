#!/usr/bin/env python

import os
import sys
import time
import subprocess
import threading
import signal
import atexit

# Make sure the current directory is in the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# First, load the employee reviews data
from load_employee_reviews import load_employee_reviews

# For graceful shutdown of child processes
processes = []

def clean_exit():
    """Kill all child processes when the main process exits"""
    for process in processes:
        if process.poll() is None:  # Process is still running
            try:
                process.terminate()
                process.wait(timeout=1)
            except:
                process.kill()

def start_backend():
    """Start the FastAPI backend server"""
    print("Starting FastAPI backend server...")
    backend_process = subprocess.Popen(
        [sys.executable, "-m", "fastapi_backend"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    processes.append(backend_process)
    
    # Start a thread to read and print the FastAPI server's output
    def read_output():
        while True:
            line = backend_process.stdout.readline()
            if not line:
                break
            print(f"[Backend] {line.strip()}")
    
    threading.Thread(target=read_output, daemon=True).start()
    return backend_process

def start_frontend():
    """Start the Streamlit frontend app"""
    print("Starting Streamlit frontend...")
    frontend_process = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "app.py", "--server.port", "5000", "--server.address", "0.0.0.0"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    processes.append(frontend_process)
    
    # Start a thread to read and print the Streamlit server's output
    def read_output():
        while True:
            line = frontend_process.stdout.readline()
            if not line:
                break
            print(f"[Frontend] {line.strip()}")
    
    threading.Thread(target=read_output, daemon=True).start()
    return frontend_process

if __name__ == "__main__":
    # Register cleanup function
    atexit.register(clean_exit)
    
    # Initialize by loading the employee reviews data
    print("Loading employee reviews data...")
    engine = load_employee_reviews()
    print("Employee data loaded successfully.")
    
    # Start the backend server
    backend_process = start_backend()
    
    # Wait for backend to start up
    print("Waiting for backend server to start...")
    time.sleep(3)
    
    # Start the frontend Streamlit app
    frontend_process = start_frontend()
    
    try:
        # Wait for either process to exit
        while True:
            if backend_process.poll() is not None:
                print("Backend server stopped. Exiting...")
                break
            
            if frontend_process.poll() is not None:
                print("Frontend app stopped. Exiting...")
                break
            
            time.sleep(1)
    except KeyboardInterrupt:
        print("Received interrupt. Shutting down...")
    finally:
        clean_exit()