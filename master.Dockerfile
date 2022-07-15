FROM docker.io/alpine:3.16

LABEL maintainer="Ondrej Chudacek <chudacek@mzk.cz>"

USER ROOT

#Installing bash
RUN apk update & apk add bash

USER nobody

#Uploading OAI harvesting scripts
RUN mkdir /opt/eod_open_data_synch
RUN mkdir /opt/eod_open_data_synch/data
COPY master/eod.sh /opt/eod_open_data_synch/eod.sh
COPY master/harvester.sh /opt/eod_open_data_synch/harvester.sh

#Creating harvester.ini inside container. It is defined as a volume in Docker-compose
RUN touch /opt/eod_open_data_synch/harvester.ini

#Uploading master script with definition of a Cron job
COPY master/runscript.sh /runscript.sh
RUN chmod +x /runscript.sh
RUN chmod 755 runscript.sh

ENTRYPOINT ["bash", "/runscript.sh"]