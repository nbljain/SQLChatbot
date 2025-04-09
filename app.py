"""
SQL Chatbot - Streamlit Frontend (Compatibility Module)

This file is a compatibility wrapper that imports from the new package structure 
but maintains the original file path for backwards compatibility with existing workflows.

The actual implementation has been moved to src/frontend/app.py
"""
import sys
import os

# Make sure the current directory is in the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import the main app code
from src.frontend.app import *

# This file is the entry point for Streamlit
# No additional code needed as Streamlit will execute the imported code