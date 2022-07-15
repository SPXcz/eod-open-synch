#!/usr/bin/env bash

python3 /home/c1081170/EOD-OPEN-data-synch-module/common_scripts/change_detector.py /home/c1081170/EOD-OPEN-data-synch-module/UIBK_new/config.ini && \
python3 /home/c1081170/EOD-OPEN-data-synch-module/UIBK_new/foxmlCreator.py /home/c1081170/EOD-OPEN-data-synch-module/UIBK_new/config.ini && \
python3 /home/c1081170/EOD-OPEN-data-synch-module/common_scripts/uploader.py /home/c1081170/EOD-OPEN-data-synch-module/UIBK_new/config.ini
