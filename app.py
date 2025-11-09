"""
WSGI entry point for Render deployment.
This file allows gunicorn to use 'app:app' command.
"""
import os

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_management_system.settings')

# Import the WSGI application
from library_management_system.wsgi import application

# Expose as 'app' for gunicorn
app = application

