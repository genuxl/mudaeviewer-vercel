"""
Vercel handler for Django application
"""
import os
import sys
from django.core.wsgi import get_wsgi_application
from django.core.management import execute_from_command_line

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_dir)

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mudae_project.vercel_settings')

# Create the WSGI application
application = get_wsgi_application()

# Vercel expects a 'handler' function
def handler(request, context):
    """
    Vercel handler function for Django application
    """
    # Delegate to the WSGI application
    return application(request, context)

# Also provide app for some frameworks
app = application

# For backwards compatibility
def main():
    """Main function for local development"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mudae_project.settings')
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()