import os
import atexit
import tempfile
import shutil
from django.conf import settings


def initialize_temp_media_cleanup():
    """Initialize the temporary media directory and register cleanup function."""
    # Check if running on Render
    if 'RENDER_EXTERNAL_HOSTNAME' in os.environ:
        # For Render, use a directory that's appropriate for the ephemeral file system
        TEMP_MEDIA_ROOT = os.path.join(tempfile.gettempdir(), 'mudae_media_render')
        os.makedirs(TEMP_MEDIA_ROOT, exist_ok=True)
    else:
        # For local development, create a temporary directory that gets cleaned up
        TEMP_MEDIA_ROOT = tempfile.mkdtemp(prefix='mudae_media_')
    
    # Store the temp directory in a global variable accessible to get_temp_media_root
    # We'll use Django's cache to store this in production environments if needed
    globals()['TEMP_MEDIA_ROOT'] = TEMP_MEDIA_ROOT
    
    # Register the cleanup function to be called when the program exits (only for local dev)
    if 'RENDER_EXTERNAL_HOSTNAME' not in os.environ:
        atexit.register(cleanup_temp_media)
        
        # Also handle cleanup on SIGTERM (when server is stopped)
        try:
            import signal
            def sigterm_handler(signum, frame):
                cleanup_temp_media()
                exit(0)
            
            signal.signal(signal.SIGTERM, sigterm_handler)
            signal.signal(signal.SIGINT, sigterm_handler)  # Handle Ctrl+C as well
        except (ImportError, AttributeError):
            # On Windows, some signals might not be available
            pass


def cleanup_temp_media():
    """Clean up the temporary media directory when the server stops."""
    temp_root = globals().get('TEMP_MEDIA_ROOT')
    if temp_root and os.path.exists(temp_root):
        try:
            shutil.rmtree(temp_root)
            print(f"Cleaned up temporary media directory: {temp_root}")
        except Exception as e:
            print(f"Error cleaning up temporary media directory: {e}")


def get_temp_media_root():
    """Get the temporary media directory for this session."""
    # For Render, we still use a temp directory but acknowledge it's ephemeral
    if 'RENDER_EXTERNAL_HOSTNAME' in os.environ:
        # Use a directory in the app root that might persist during a single deployment
        # Note: This will still be lost when the instance restarts, but may work during a single session
        temp_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'media_temp')
        os.makedirs(temp_dir, exist_ok=True)
        return temp_dir
    else:
        # For local dev, use the temp directory created at startup
        temp_root = globals().get('TEMP_MEDIA_ROOT')
        if not temp_root:
            temp_root = tempfile.mkdtemp(prefix='mudae_media_')
            globals()['TEMP_MEDIA_ROOT'] = temp_root
        return temp_root