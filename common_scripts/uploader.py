#!/usr/bin/env python3

import requests as req
from os import walk, mkdir, listdir, system
from os.path import exists
from shutil import move
from datetime import datetime
from sys import argv

SECRET = '/home/c1081170/EOD-OPEN-data-synch-module/common_scripts/secret.txt'
IMPORT_VOL_DIR = "/home/c1081170/s2i-kramerius/import_vol"
DESTINATION_URL = "http://backend.ds-coil.uibk.ac.at/search"
DATE = datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
PATH_TO_CONFIG = argv[1].strip()
CONFIG_DATA = {"LIBRARY_CODE": "MZK",
                "PATH_TO_FOXML": "/home/c1081170/EOD-OPEN-data-synch-module/MZK/foxml"}
with open(SECRET, "r") as passwords:
    LOGIN = (passwords.readline().strip(), passwords.readline().strip())

if exists(PATH_TO_CONFIG):
    with open(PATH_TO_CONFIG, "r") as configFile:
        for line in configFile:
            if line.find("=") != -1:
                before, after = line.split("=")
                CONFIG_DATA[before] = after.strip()

def logString(mssg, error = False):
    with open(CONFIG_DATA["PATH_TO_LOG"], "a+") as logFile:
        if error is False:
            logFile.write("[" + datetime.today().isoformat() + "] " + "[INFO] " + "[" + CONFIG_DATA["LIBRARY_CODE"] + "] " + mssg + "\n")
        else:
            logFile.write("[" + datetime.today().isoformat() + "] " + "[ERROR] " + "[" + CONFIG_DATA["LIBRARY_CODE"] + "] " + mssg + "\n")

importVols = []

for root, dirs, files in walk(CONFIG_DATA["PATH_TO_FOXML"]):
    tempStr = root.replace(CONFIG_DATA["PATH_TO_FOXML"], "")
    if tempStr.count("/") == 1 and "importset_" in tempStr:
        importVols.append(tempStr)

#importVols = filter(lambda direc: direc.count("/") == 1, roots)
if importVols:
    mkdir(IMPORT_VOL_DIR + "/" + CONFIG_DATA["LIBRARY_CODE"] + "_" + DATE)
    for direc in listdir(CONFIG_DATA["PATH_TO_FOXML"]):
        move(CONFIG_DATA["PATH_TO_FOXML"] + "/" + direc, IMPORT_VOL_DIR + "/" + CONFIG_DATA["LIBRARY_CODE"] + "_" + DATE)
    system("chmod -R 770 " + IMPORT_VOL_DIR + "/" + CONFIG_DATA["LIBRARY_CODE"] + "_" + DATE)
    system("chown -R 8983:input " + IMPORT_VOL_DIR + "/" + CONFIG_DATA["LIBRARY_CODE"] + "_" + DATE)

if importVols:
    logString("Uploading " + CONFIG_DATA["LIBRARY_CODE"] + "_" + DATE)

for direc in importVols:
    
    json = {
        "mapping":{
            "importDirectory":"/opt/app-root/src/.kramerius4/import/" + CONFIG_DATA["LIBRARY_CODE"] + "_" + DATE + direc,
            "startIndexer": "true",
            "updateExisting": "false"}
        }
    header = {
        "Content-Type": "application/json"
        }

    response = req.post(DESTINATION_URL + "/api/v4.6/processes?def=parametrizedimport", json=json, auth=LOGIN, headers=header)
    if response.status_code >= 300:
        logString(CONFIG_DATA["LIBRARY_CODE"] + "_" + DATE + direc + " not uploaded. Error " + str(response.status_code), True)