FROM docker.io/alpine:3.16

LABEL maintainer="Ondrej Chudacek <chudacek@mzk.cz>"

#Installing Python 3
ENV PYTHONUNBUFFERED=1
RUN apk add --no-cache python3 && ln -sf python3 /usr/bin/python
RUN python3 -m ensurepip
RUN pip3 install --no-cache --upgrade pip setuptools

#Creating necessary folders
RUN mkdir /opt/eod_open_data_synch
RUN mkdir /opt/eod_open_data_synch/data
RUN mkdir /opt/eod_open_data_synch/import_vol
RUN mkdir /opt/eod_open_data_synch/logs

#Uploading scripts
COPY common_scripts/uploader.py /opt/eod_open_data_synch/uploader.py
COPY common_scripts/secret.txt /opt/eod_open_data_synch/secret.txt
COPY MZK/krameriusHarvester.py /opt/eod_open_data_synch/krameriusHarvester.py
COPY MZK/current_ids_list.txt /opt/eod_open_data_synch/current_ids_list.txt
RUN chmod 744 /opt/eod_open_data_synch

#Creating config.ini inside container. It is defined as a volume in Docker-compose.
RUN touch /opt/eod_open_data_synch/config.ini

#Uploading master script with definition of a Cron job
COPY MZK/runscript.sh /runscript.sh
RUN chmod +x /runscript.sh
RUN chmod 755 runscript.sh

ENTRYPOINT ["sh", "/runscript.sh"]