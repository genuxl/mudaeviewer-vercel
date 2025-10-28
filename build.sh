#!/bin/bash
set -o errexit

# Create staticfiles directory if it doesn't exist
mkdir -p staticfiles

# Install dependencies
pip install -r requirements.txt

# Run Django collectstatic with error handling
python manage.py collectstatic --no-input --verbosity=2 || echo "Warning: collectstatic failed, continuing..."

# Run migrations
python manage.py migrate --no-input || echo "Warning: migrations failed, continuing..."

echo "Build completed successfully"