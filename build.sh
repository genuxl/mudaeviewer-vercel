#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

# Run collectstatic, which may fail during build but that's ok
# The important thing is that dependencies are installed
if python manage.py collectstatic --no-input --settings=mudae_project.settings; then
    echo "Collectstatic completed successfully"
else
    echo "Collectstatic failed during build (expected during initial deployment), continuing..."
fi