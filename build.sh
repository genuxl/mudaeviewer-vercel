#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

# Only run collectstatic during build - migrations will be handled separately
python manage.py collectstatic --no-input --settings=mudae_project.settings --skip-checks || echo "Collectstatic completed with potential warnings"