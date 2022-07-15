#!/bin/bash

cd /home/c1081170/EOD-OPEN-data-synch-module/master

bash harvester.sh --source=P1-UIBK-mets --repeat=false && \
bash harvester.sh --source=P1-UIBK --repeat=false && \
bash harvester.sh --source=P2-UT --repeat=false && \
bash harvester.sh --source=P3-NUK --repeat=false && \
bash harvester.sh --source=P5-EMAU --repeat=false && \
bash harvester.sh --source=P6-NLS --repeat=false && \
bash harvester.sh --source=P7-NCU --repeat=false && \
bash harvester.sh --source=P10-BNP --repeat=false && \
bash harvester.sh --source=P11-NLE --repeat=false && \
bash harvester.sh --source=P13-CVTISR --repeat=false && \
bash harvester.sh --source=P14-UREG --repeat=false && \
bash harvester.sh --source=P15-VU --repeat=false && \
bash harvester.sh --source=P1-UIBK-rawmods --repeat=false
