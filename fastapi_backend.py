"""
Compatibility module for existing workflow.
This module imports and re-exports functionality from the src package.
"""
from src.api.fastapi_backend import app, start_backend

# Run the backend server if this file is executed directly
if __name__ == "__main__":
    start_backend()