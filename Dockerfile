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
    pip install --upgrade pip && \
    pip3 install --no-cache-dir -r requirements.txt
# execution
CMD crond -l 2 -f
