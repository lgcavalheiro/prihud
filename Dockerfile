FROM python:3.10-alpine AS base
    WORKDIR /app
    EXPOSE 8000

    COPY cron /var/spool/cron/crontabs/app
    COPY requirements.txt ./
    COPY .env ./
    COPY manage.py ./
    COPY prihud ./prihud
    COPY templates ./templates
    COPY database ./database
    COPY db.sqlite3 ./
    COPY entrypoint.sh ./
    
    RUN apk update && \
        apk add --no-cache firefox busybox-suid su-exec && \
        chmod u+s /sbin/su-exec && \
        pip install --upgrade pip && \
        pip3 install --no-cache-dir -r requirements.txt && \
        chmod +x ./entrypoint.sh && \
        addgroup -S app && adduser -S app -G app

FROM base AS dockerized
    ARG DJANGO_ENV=dev

    ENV ENV $DJANGO_ENV

    COPY static ./static
    COPY gunicorn/$DJANGO_ENV.py ./gunicorn_config.py

    RUN chown -R app:app .
    USER app

    ENTRYPOINT ["./entrypoint.sh"]

FROM base AS composed
    ARG DBU_ENV=dev

    ENV ENV $DBU_ENV

    COPY static ./staticfiles
    COPY gunicorn/$DBU_ENV.py ./gunicorn_config.py

    RUN python manage.py collectstatic --no-input
    RUN chown -R app:app .
    USER app

    ENTRYPOINT ["./entrypoint.sh"]
