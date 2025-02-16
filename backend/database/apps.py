from django.apps import AppConfig
from django.db import connection

class DatabaseConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "database"
    
    def ready(self):
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT populate_database();")
        except Exception as e:
            print(f"Error populating database: {e}")
