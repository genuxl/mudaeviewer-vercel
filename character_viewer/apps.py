from django.apps import AppConfig

class CharacterViewerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'character_viewer'

    def ready(self):
        # Initialize the temporary media cleanup when the app is ready
        try:
            from .cleanup import initialize_temp_media_cleanup
            initialize_temp_media_cleanup()
        except ImportError:
            pass