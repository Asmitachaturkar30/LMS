from django.apps import AppConfig
from ci_loan import settings 

class MastersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Masters'

    # def ready(self):
    #     # if not settings.TESTING:  # Don't run in tests
    #     from .scheduler import start_scheduler
    #     start_scheduler()

