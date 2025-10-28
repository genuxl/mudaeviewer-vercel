"""
Vercel handler for Django applications
"""
import os
import sys

# Add project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

def handler(event, context):
    """
    Vercel handler function for Django application
    """
    try:
        # Set Django settings
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mudae_project.vercel_settings')
        
        # Import Django
        import django
        from django.core.wsgi import get_wsgi_application
        from django.core.management import execute_from_command_line
        
        # Setup Django
        django.setup()
        
        # Get the WSGI application
        application = get_wsgi_application()
        
        # For now, return a simple response to test
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'text/plain'},
            'body': 'Django application initialized successfully'
        }
        
    except Exception as e:
        print(f"Error in Vercel handler: {str(e)}")
        import traceback
        traceback.print_exc()
        # Return a simple error response
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'text/plain'},
            'body': f'Internal Server Error: {str(e)}'
        }

# Also provide app for compatibility
app = handler

if __name__ == '__main__':
    # For local development
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mudae_project.settings')
    from django.core.management import execute_from_command_line
    import sys
    execute_from_command_line(sys.argv)