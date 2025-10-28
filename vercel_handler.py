"""
Vercel handler for Django applications
"""
import os
import sys
from io import BytesIO

# Add project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Global application instance
_application = None

def get_application():
    """Get or create the Django WSGI application."""
    global _application
    if _application is None:
        # Set Django settings
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mudae_project.vercel_settings')
        
        # Import Django
        import django
        from django.core.wsgi import get_wsgi_application
        
        # Setup Django
        django.setup()
        
        # Get the WSGI application
        _application = get_wsgi_application()
    
    return _application

def create_wsgi_environ(event):
    """Create WSGI environ dict from Vercel event."""
    # Extract request details
    method = event.get('httpMethod', 'GET')
    path = event.get('path', '/')
    headers = event.get('headers', {}) or {}
    query_params = event.get('queryStringParameters', {}) or {}
    body = event.get('body', '') or ''
    
    # Build query string
    query_string = ""
    if query_params:
        query_string = "&".join(f"{k}={v}" for k, v in query_params.items() if v is not None)
    
    # Handle base64 encoded body
    if event.get('isBase64Encoded', False):
        import base64
        body = base64.b64decode(body)
    if isinstance(body, str):
        body = body.encode('utf-8')
    
    # Determine if request is secure
    is_secure = headers.get('x-forwarded-proto', '').lower() == 'https'
    
    # Build WSGI environ
    environ = {
        'REQUEST_METHOD': method,
        'PATH_INFO': path,
        'QUERY_STRING': query_string,
        'CONTENT_TYPE': headers.get('content-type', ''),
        'CONTENT_LENGTH': str(len(body)) if body else '0',
        'SERVER_NAME': headers.get('host', 'localhost'),
        'SERVER_PORT': headers.get('x-forwarded-port', '443' if is_secure else '80'),
        'SERVER_PROTOCOL': 'HTTP/1.1',
        'wsgi.version': (1, 0),
        'wsgi.url_scheme': 'https' if is_secure else 'http',
        'wsgi.input': BytesIO(body),
        'wsgi.errors': sys.stderr,
        'wsgi.multithread': False,
        'wsgi.multiprocess': True,
        'wsgi.run_once': False,
        'wsgi.binary': False,
    }
    
    # Add HTTP headers
    for header_name, header_value in headers.items():
        if header_name.lower() == 'content-type':
            environ['CONTENT_TYPE'] = header_value
        elif header_name.lower() == 'content-length':
            environ['CONTENT_LENGTH'] = str(header_value) if header_value else '0'
        else:
            # Convert to WSGI format
            wsgi_header = 'HTTP_' + header_name.upper().replace('-', '_')
            environ[wsgi_header] = str(header_value) if header_value else ''
    
    return environ

def handler(event, context):
    """
    Vercel handler function for Django application
    """
    try:
        # Get the Django application
        application = get_application()
        
        # Create WSGI environ
        environ = create_wsgi_environ(event)
        
        # Response holders
        status = [None]
        response_headers = [None]
        
        def start_response(status_str, headers, exc_info=None):
            """WSGI start_response function."""
            status[0] = status_str
            response_headers[0] = headers
            return lambda x: None  # Return a write function (we won't use it)
        
        # Execute Django application
        try:
            result = application(environ, start_response)
            body = b''.join(result)
        except Exception as e:
            # Handle Django exceptions
            import traceback
            traceback.print_exc()
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'text/plain'},
                'body': f'Django application error: {str(e)}'
            }
        
        # Extract status code
        status_code = 200
        if status[0]:
            try:
                status_code = int(status[0].split()[0])
            except (ValueError, IndexError):
                status_code = 500
        
        # Convert headers to dict
        headers_dict = {}
        if response_headers[0]:
            for header in response_headers[0]:
                if len(header) >= 2:
                    headers_dict[header[0]] = header[1]
        
        # Ensure Content-Type header exists
        if 'Content-Type' not in headers_dict:
            headers_dict['Content-Type'] = 'text/html'
        
        # Return response
        return {
            'statusCode': status_code,
            'headers': headers_dict,
            'body': body.decode('utf-8', errors='replace') if isinstance(body, bytes) else str(body),
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'text/plain'},
            'body': f'Vercel handler error: {str(e)}'
        }

# Also provide app for compatibility
app = handler

# For local development
if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mudae_project.settings')
    from django.core.management import execute_from_command_line
    import sys
    execute_from_command_line(sys.argv)