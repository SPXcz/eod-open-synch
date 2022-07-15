#!/usr/bin/env python3

from os import walk, mkdir
from os.path import exists
import xml.etree.ElementTree as ET
from datetime import datetime
from sys import argv

PATH_TO_OAI = '/home/c1081170/EOD-OPEN-data-synch-module/common_scripts/data'
OAI_PREFIX = '{http://www.openarchives.org/OAI/2.0/}'
PATH_TO_CONFIG = argv[1].strip()
CONFIG_DATA = {'PATH_TO_LIST_OF_IDS': 'current_ids_list.txt',
                'PATH_TO_LIST_OF_NEW_IDS': 'new_ids_list.txt',
                'PATH_TO_LOG':'uibk.log',
                'LIBRARY_CODE': 'P1-UIBK-mets'}

def logString(mssg, error = False):
    with open(CONFIG_DATA["PATH_TO_LOG"], "a+") as logFile:
        if error is False:
            logFile.write("[" + datetime.today().isoformat() + "] " + "[INFO] " + "[" + CONFIG_DATA["LIBRARY_CODE"] + "] " + mssg + "\n")
        else:
            logFile.write("[" + datetime.today().isoformat() + "] " + "[ERROR] " + "[" + CONFIG_DATA["LIBRARY_CODE"] + "] " + mssg + "\n")

if exists(PATH_TO_CONFIG):
    with open(PATH_TO_CONFIG, "r") as configFile:
        for line in configFile:
            if line.find("=") != -1:
                before, after = line.split("=")
                CONFIG_DATA[before] = after.strip()


if not exists(CONFIG_DATA['PATH_TO_LIST_OF_IDS']):
    with open(CONFIG_DATA['PATH_TO_LIST_OF_IDS'], "w+") as fNew:
        fNew.write("")

logString("Searching for changes.")
isChanged = False

with open(CONFIG_DATA['PATH_TO_LIST_OF_IDS'], "r") as fileListOfCurrent:
    fLC = fileListOfCurrent.read().strip()
    with open(CONFIG_DATA['PATH_TO_LIST_OF_NEW_IDS'], "w+") as fileOutput:
        for rootData, dirsData, filesData in walk(PATH_TO_OAI + "/"  + CONFIG_DATA['LIBRARY_CODE']):
                for intividualFile in filesData:
                    root = ET.parse(rootData + "/" + intividualFile).getroot()
                    for record in root.find(OAI_PREFIX + 'ListRecords').iter(OAI_PREFIX + 'record'):
                        recordID = record.find(OAI_PREFIX + 'header').find(OAI_PREFIX + 'identifier').text
                        recordIdStripped = recordID.strip()
                        if recordIdStripped not in fLC:
                            print(recordIdStripped)
                            isChanged = True
                            fileOutput.write(recordID + "\n")

#Logging
if not isChanged:
    logString("No changes to be made.")