"""
WSGI config for mudae_project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
import sys
from django.core.wsgi import get_wsgi_application

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_dir)

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mudae_project.vercel_settings')

# Create the WSGI application
application = get_wsgi_application()

# For Vercel, we need to make sure this module can be imported as a callable
# Vercel expects the handler to be named 'application' or 'handler'
handler = application

# Also provide app for some frameworks
app = application
