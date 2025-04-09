"""
SQL Chatbot - FastAPI Backend (Compatibility Module)

This file is a compatibility wrapper that imports from the new package structure 
but maintains the original file path for backwards compatibility with existing workflows.

The actual implementation has been moved to src/api/fastapi_backend.py
"""
from src.api.fastapi_backend import app, start_backend

# Run the backend server if this file is executed directly
if __name__ == "__main__":
    start_backend()