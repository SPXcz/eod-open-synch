#!/usr/bin/env bash

python3 /home/c1081170/EOD-OPEN-data-synch-module/common_scripts/krameriusHarvester.py /home/c1081170/EOD-OPEN-data-synch-module/MZK/config.ini  && \
python3 /home/c1081170/EOD-OPEN-data-synch-module/common_scripts/uploader.py /home/c1081170/EOD-OPEN-data-synch-module/MZK/config.ini
