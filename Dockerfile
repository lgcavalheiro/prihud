FROM python:3.11.2-bullseye AS base
    WORKDIR /app
    EXPOSE 8000

    ARG TZ=Europe/London
    ENV TZ $TZ

    COPY cron /var/spool/cron/crontabs/root
    COPY templates ./templates
    COPY database ./database
    COPY prihud ./prihud
    COPY static ./static
    COPY requirements.txt .env manage.py db.sqlite3 entrypoint.sh ./

    RUN apt update && \
        apt upgrade -y && \
        apt install -y firefox-esr cron && \
        pip install --upgrade pip && \
        pip install --no-cache-dir -r requirements.txt && \
        python manage.py collectstatic --no-input && \
        chmod +x ./entrypoint.sh && \
        chmod u+s /usr/sbin/cron && \
        addgroup --system app && \
        adduser --system app --ingroup app

FROM base AS dockerized
    ARG DJANGO_ENV=dev
    ENV ENV $DJANGO_ENV

    COPY gunicorn/$DJANGO_ENV.py ./gunicorn_config.py

    RUN chown -R app:app .
    USER app

    ENTRYPOINT ["./entrypoint.sh"]

FROM base AS composed
    ARG DBU_ENV=dev
    ENV ENV $DBU_ENV

    COPY gunicorn/$DBU_ENV.py ./gunicorn_config.py

    RUN chown -R app:app .
    USER app

    ENTRYPOINT ["./entrypoint.sh"]
