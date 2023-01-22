#!/bin/sh

python manage.py makemigrations database
python manage.py migrate
gunicorn -c gunicorn_config.py &
crond -l 2 -f
