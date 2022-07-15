#!/bin/bash

echo "1 0 * * * /opt/eod_open_data_synch/runscript.sh" >> /etc/crontabs/root
crond -l 2 -f > /dev/stdout 2> /dev/stderr &
bash /opt/eod_open_data_synch/eod.sh