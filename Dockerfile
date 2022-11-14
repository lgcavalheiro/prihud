# setup
FROM python:3.10-alpine
WORKDIR /app
# file copy
COPY root /var/spool/cron/crontabs/root
COPY requirements.txt ./
COPY scrapper.py ./
COPY geckodriver ./
# deps install
RUN \
    apk update && \
    apk add --no-cache postgresql-libs libressl-dev musl-dev libffi-dev firefox && \
    apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev && \
    pip install --upgrade pip && \
    pip3 install --no-cache-dir -r requirements.txt && \
    apk --purge del .build-deps
# execution
CMD crond -l 2 -f