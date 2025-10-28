import sys
import os

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set Django settings module before importing Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mudae_project.vercel_settings')

# Now import Django and setup
import django
django.setup()

from django.core.wsgi import get_wsgi_application
from django.conf import settings
import traceback
from io import BytesIO

# Get the WSGI application
application = get_wsgi_application()

def django_view_handler(event, context):
    """
    Handles requests to the Django application on Vercel.
    """
    try:
        # Prepare WSGI environ dictionary from the Vercel event
        method = event.get('httpMethod', 'GET')
        path = event.get('path', '/')
        headers = event.get('headers', {}) or {}
        query_params = event.get('queryStringParameters', {}) or {}
        
        # Build query string
        query_string = ""
        if query_params:
            query_string = "&".join(f"{k}={v}" for k, v in query_params.items() if v is not None)
        
        # Get request body
        body = event.get('body', '') or ''
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
            'CONTENT_LENGTH': str(len(body)),
            'SCRIPT_NAME': getattr(settings, 'SCRIPT_NAME', ''),
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
        }
        
        # Add HTTP headers to environ
        for header_name, header_value in headers.items():
            if header_name == 'content-type':
                environ['CONTENT_TYPE'] = header_value
            elif header_name == 'content-length':
                environ['CONTENT_LENGTH'] = str(header_value) if header_value else '0'
            else:
                # Convert header to WSGI HTTP header format
                wsgi_header = 'HTTP_' + header_name.upper().replace('-', '_')
                environ[wsgi_header] = str(header_value) if header_value else ''
        
        # Response holder
        status = [None]
        response_headers = [None]
        
        def start_response(status_str, headers):
            status[0] = status_str
            response_headers[0] = headers
        
        # Execute Django application
        result = application(environ, start_response)
        body = b''.join(result) if hasattr(result, '__iter__') else result
        
        # Extract status code
        status_code = 200
        if status[0]:
            status_code = int(status[0].split()[0])
        
        # Convert headers to dict format for Vercel
        headers_dict = {}
        if response_headers[0]:
            headers_dict = {header[0]: header[1] for header in response_headers[0]}
        
        # Return response in Vercel format
        return {
            'statusCode': status_code,
            'headers': headers_dict,
            'body': body.decode('utf-8') if isinstance(body, bytes) else body,
            'isBase64Encoded': False
        }
    except Exception as e:
        # Log the error for debugging
        print(f"Error in Django handler: {str(e)}")
        print(traceback.format_exc())
        
        # Return error response
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'text/plain'},
            'body': 'Internal Server Error',
            'isBase64Encoded': False
        }
    
# The main handler for Vercel
def handler(event, context):
    return django_view_handler(event, context)