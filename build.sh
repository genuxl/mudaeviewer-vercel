#!/bin/bash
set -o errexit

# Set up Python environment
pip install -r requirements.txt

# Run Django migrations
python manage.py migrate --no-input

# Collect static files
python manage.py collectstatic --no-input

echo "Build completed successfully"