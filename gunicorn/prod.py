wsgi_app = "project.wsgi:application"
loglevel = "info"
workers = 2
bind = "0.0.0.0:8000"
reload = False
accesslog = errorlog = "/var/log/gunicorn/dev.log"
capture_output = True
pidfile = "/var/run/gunicorn/dev.pid"
daemon = True