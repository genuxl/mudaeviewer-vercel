import os
import dj_database_url
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# Check if running on Render by looking for RENDER_EXTERNAL_HOSTNAME environment variable
if 'RENDER_EXTERNAL_HOSTNAME' in os.environ:
    # Production settings for Render
    DATABASES = {
        'default': dj_database_url.config(
            default=os.environ.get('DATABASE_URL'),
            conn_max_age=600
        )
    }
else:
    # Local development settings
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }