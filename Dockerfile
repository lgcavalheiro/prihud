FROM python:3.10-alpine AS base
    WORKDIR /app
    EXPOSE 8000

    COPY root /var/spool/cron/crontabs/root
    COPY requirements.txt ./
    COPY .env ./
    COPY manage.py ./
    COPY prihud ./prihud
    COPY templates ./templates
    COPY database ./database
    COPY db.sqlite3 ./
    
    RUN apk update && \
        apk add --no-cache firefox && \
        pip install --upgrade pip && \
        pip3 install --no-cache-dir -r requirements.txt 

FROM base AS dev
    ENV ENV dev

    COPY static ./static
    COPY gunicorn/dev.py ./gunicorn_config.py

    CMD python manage.py makemigrations database && \
        python manage.py migrate && \
        gunicorn -c gunicorn_config.py & crond -l 2 -f

FROM base AS prod
    ENV ENV prod

    COPY static ./static
    COPY gunicorn/prod.py ./gunicorn_config.py

    CMD python manage.py makemigrations database && \
        python manage.py migrate && \
        gunicorn -c gunicorn_config.py & crond -l 2 -f

FROM base AS dbu
    ARG DBU_ENV=dev

    ENV ENV $DBU_ENV

    COPY static ./staticfiles
    COPY gunicorn/$DBU_ENV.py ./gunicorn_config.py

    RUN python manage.py collectstatic --no-input

    CMD python manage.py makemigrations database && \
        python manage.py migrate && \
        gunicorn -c gunicorn_config.py & crond -l 2 -f
