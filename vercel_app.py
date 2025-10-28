"""
Vercel Django application entry point
"""
import os
import sys

# Add project directory to Python path
project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_dir)

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mudae_project.vercel_settings')

def handler(event, context):
    """
    Vercel handler function for Django application
    """
    try:
        # Import Django here to ensure settings are loaded first
        import django
        from django.core.wsgi import get_wsgi_application
        from django.core.management import execute_from_command_line
        
        # Setup Django
        django.setup()
        
        # Get the WSGI application
        application = get_wsgi_application()
        
        # Process the request through Django
        return application
        
    except Exception as e:
        print(f"Error in Vercel handler: {str(e)}")
        # Return a simple error response
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'text/plain'},
            'body': 'Internal Server Error'
        }

# Also provide app for compatibility
app = handler

if __name__ == '__main__':
    # For local development
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mudae_project.settings')
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)