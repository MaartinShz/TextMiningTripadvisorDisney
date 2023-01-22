FROM python:3.9-slim-buster

RUN apt-get update && apt-get -y install cron
COPY crontab /etc/cron.d/crontab
COPY async_scrap.py ./async_scrap.py

RUN chmod 0644  /etc/cron.d/crontab
RUN chmod 0644  ./async_scrap.py
RUN /usr/bin/crontab etc/cron.d/crontab

CMD ["cron", "-f"]