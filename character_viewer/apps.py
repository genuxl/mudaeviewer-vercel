from django.apps import AppConfig

class CharacterViewerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'character_viewer'

    def ready(self):
        # No initialization needed for temporary media cleanup
        # We're using simple temporary directories now
        pass