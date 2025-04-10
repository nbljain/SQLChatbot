import os
import time
import subprocess
import sys

# Make sure we're in the right directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Load the employee reviews data
print("Loading employee reviews data...")
from load_employee_reviews import load_employee_reviews
load_employee_reviews()
print("Data loaded successfully!")

# Start the FastAPI backend
print("Starting FastAPI backend...")
backend_process = subprocess.Popen(
    [sys.executable, "fastapi_backend.py"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT
)

# Wait for backend to start
print("Waiting for backend to initialize...")
time.sleep(3)

# Start Streamlit frontend
print("Starting Streamlit frontend...")
streamlit_cmd = [sys.executable, "-m", "streamlit", "run", "app.py", "--server.port=5000", "--server.headless=true", "--server.address=0.0.0.0"]
streamlit_process = subprocess.Popen(streamlit_cmd)

# Keep the script running
print("Application started! Press Ctrl+C to stop.")
try:
    streamlit_process.wait()
except KeyboardInterrupt:
    print("Shutting down...")
    backend_process.terminate()
    streamlit_process.terminate()