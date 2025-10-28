"""
Production settings for Vercel deployment with Supabase
"""
from .settings import *

import os
import dj_database_url

# Force DEBUG to False in production
DEBUG = False

# Allow all hosts in Vercel environment
ALLOWED_HOSTS = ['*']

# Database configuration for Supabase
if os.environ.get('DATABASE_URL'):
    DATABASES = {
        'default': dj_database_url.parse(
            os.environ.get('DATABASE_URL'),
            conn_max_age=600,
            ssl_require=True
        )
    }
else:
    # Fallback to default configuration if no DATABASE_URL
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': '/tmp/db.sqlite3',
        }
    }

# Static files for production
STATIC_URL = '/static/'
# On Vercel, use /tmp directory which is writable
STATIC_ROOT = '/tmp/staticfiles'

# Ensure static root directory exists
if not os.path.exists(STATIC_ROOT):
    try:
        os.makedirs(STATIC_ROOT, exist_ok=True)
    except Exception:
        # If we can't create the directory, use a fallback
        STATIC_ROOT = '/tmp/static'

# Media files - use temporary directory
# In a serverless environment like Vercel, uploaded files are ephemeral
import tempfile
import os
MEDIA_ROOT = os.path.join(tempfile.gettempdir(), 'mudae_media')
os.makedirs(MEDIA_ROOT, exist_ok=True)
MEDIA_URL = '/media/'

# Use WhiteNoise for static file serving
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Security settings for production
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True