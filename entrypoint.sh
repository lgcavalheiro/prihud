#!/bin/sh

cron
python manage.py makemigrations database
python manage.py migrate
gunicorn -c gunicorn_config.py 
