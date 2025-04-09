"""
Compatibility module for existing workflow.
This module imports and re-exports functionality from the src package.
"""
import sys
import os

# Make sure the current directory is in the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import the main app code
from src.frontend.app import *

# This file is the entry point for Streamlit
# No additional code needed as Streamlit will execute the imported code