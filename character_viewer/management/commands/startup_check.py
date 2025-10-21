from django.core.management.base import BaseCommand
from django.db import connection
from django.core.management import call_command
from character_viewer.models import Character
import os


class Command(BaseCommand):
    help = 'Ensures the database is properly initialized'

    def handle(self, *args, **options):
        self.stdout.write('Performing startup checks...')
        
        # Check if database tables exist
        try:
            # Try to access the Character model
            Character.objects.count()
            self.stdout.write('Database tables exist and are accessible.')
        except Exception as e:
            self.stdout.write(f'Database might not be initialized: {e}')
            # Run migrations
            self.stdout.write('Running migrations...')
            call_command('migrate', verbosity=2)
            
        # Check if we're on Render and need to do any additional setup
        if 'RENDER_EXTERNAL_HOSTNAME' in os.environ:
            self.stdout.write('Running on Render environment.')
            
        self.stdout.write(self.style.SUCCESS('Startup checks completed successfully'))