# setup
FROM python:3.10-alpine
WORKDIR /app
EXPOSE 8000
# file copy
COPY root /var/spool/cron/crontabs/root
COPY requirements.txt ./
COPY .env ./
COPY manage.py ./
COPY prihud ./prihud
COPY database ./database
COPY db.sqlite3 ./
# deps install
RUN apk update && \
    apk add --no-cache firefox && \
    pip install --upgrade pip && \
    pip3 install --no-cache-dir -r requirements.txt 
# execution
CMD python manage.py makemigrations database && \
    python manage.py migrate && \
    python manage.py runserver & crond -l 2 -f
