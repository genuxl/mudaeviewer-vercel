#!/usr/bin/env python
"""
Test script to verify Django setup
"""
import os
import sys

def test_django_setup():
    print("Testing Django setup...")
    
    # Add project directory to Python path
    project_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, project_dir)
    
    # Set Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mudae_project.vercel_settings')
    
    try:
        import django
        print("Django imported successfully")
        
        # Setup Django
        django.setup()
        print("Django setup completed successfully")
        
        # Test importing models
        from django.contrib.auth.models import User
        print("Django models imported successfully")
        
        # Test database connection
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            print(f"Database connection successful: {result}")
            
        return True
        
    except Exception as e:
        print(f"Django setup failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_django_setup()