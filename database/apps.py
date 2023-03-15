''' Module that provides configurations for database app '''

from django.apps import AppConfig


class DatabaseConfig(AppConfig):
    ''' Class that sets configurations for the database app '''

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'database'
