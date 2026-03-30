"""
Pxxl entry point for Django application.
This file serves as the entry point that Pxxl expects,
then delegates to the actual Django WSGI application.
"""
import os
import sys

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventory_management.settings')

# Import Django WSGI application
from inventory_management.wsgi import application

# For Pxxl compatibility
app = application
