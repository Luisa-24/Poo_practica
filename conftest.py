"""
Configuration for pytest to include the src directory in the path.
"""
import sys
import os

# Path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))
