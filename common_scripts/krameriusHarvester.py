#!/usr/bin/env python3

import requests as req
import xml.etree.ElementTree as ET
from os.path import exists
from urllib.parse import quote
from os import rename, remove, mkdir
from datetime import datetime
from sys import argv

RDF_PREFIX = '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}'
FOXML_PREFIX = '{info:fedora/fedora-system:def/foxml#}'
OAI_PREFIX = '{http://www.openarchives.org/OAI/2.0/}'
KRAMERIUS_PREFIX = '{http://www.nsdl.org/ontologies/relationships#}'
PATH_TO_CONFIG = argv[1].strip()
CONFIG_DATA = {'ORIGINAL_VC': 'vc:b1adb6f0-01db-45fd-bc4a-d36fa3eab050',
                'URL_TO_SRC': 'https://kramerius.mzk.cz',
                'PATH_TO_LIST_OF_IDS': 'current_ids_list.txt',
                'PATH_TO_LIST_OF_NEW_IDS': 'new_ids_list.txt', 
                'PATH_TO_LOG': 'mzk.log',
                'LIBRARY_CODE': 'P4-MZK',
                'PATH_TO_FOXML': '/home/c1081170/EOD-OPEN-data-synch-module/MZK/foxml'}

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

#Harvesting
url = CONFIG_DATA['URL_TO_SRC'] + "/search/api/v5.0/search?q=*:*&fq=(fedora.model:monograph OR fedora.model:periodical OR fedora.model:graphic OR fedora.model:map OR fedora.model:sheetmusic OR fedora.model:soundrecording OR fedora.model:archive OR fedora.model:manuscript OR fedora.model:convolute OR fedora.model:monographunit) AND (collection:\"{collection_id}\")&fl=PID&facet=true&facet.mincount=1&facet.field=keywords&facet.field=language&facet.field=dnnt-labels&facet.field=mods.physicalLocation&facet.field=geographic_names&facet.field=facet_autor&facet.field=model_path&facet.field=dostupnost&sort=created_date desc&rows={rows}&start=0"
initResponse = req.get(url.format(
   collection_id = CONFIG_DATA['ORIGINAL_VC'],
   rows = "1"      
)).text

rootXML = ET.fromstring(initResponse) 
numFound = rootXML.find("result").get("numFound")

finalRootResponse = req.get(url.format(
   collection_id = CONFIG_DATA['ORIGINAL_VC'],
   rows = numFound      
)).text
rootXML = ET.fromstring(finalRootResponse)

with open(CONFIG_DATA['PATH_TO_LIST_OF_NEW_IDS'], "w+") as fw:
    for doc in rootXML.find("result").findall("doc"):
        fw.write(doc.find("str").text + "\n")

#Comparison
filteredList = []
if exists(CONFIG_DATA['PATH_TO_LIST_OF_IDS']):
    with open(CONFIG_DATA['PATH_TO_LIST_OF_NEW_IDS'], "r") as newFile:
        with open(CONFIG_DATA['PATH_TO_LIST_OF_IDS'], "r") as originalFile:
            readOriginalFile = originalFile.read()
            for uuid in newFile:
                if uuid.rstrip() not in readOriginalFile:
                    filteredList.append(uuid)
else:
    with open(CONFIG_DATA['PATH_TO_LIST_OF_NEW_IDS'], "r") as newFile:
        for uuid in newFile:
            filteredList.append(uuid)

#Get FOXML
workCount = 0
importDir = "importset_0"
if not exists(CONFIG_DATA['PATH_TO_FOXML']):
    mkdir(CONFIG_DATA['PATH_TO_FOXML'])
for uuid in filteredList:
    if workCount % 30 == 0:
        mkdir(CONFIG_DATA['PATH_TO_FOXML'] + "/importset_" + str(workCount // 30))
        importDir = "importset_" + str(workCount // 30)
    uuid = uuid.replace("\n", "")
    uuidNoIndicator = uuid.replace("uuid:", "")
    urlFoxml = CONFIG_DATA['URL_TO_SRC'] + "/search/api/v5.0/item/" + uuid + "/foxml"
    foxmlResource = req.get(urlFoxml).text
    mkdir(CONFIG_DATA['PATH_TO_FOXML'] + "/" + importDir + "/" + uuidNoIndicator)
    with open(CONFIG_DATA['PATH_TO_FOXML'] + "/" + importDir + "/" + uuidNoIndicator  + "/" + uuidNoIndicator  + ".xml", "w+") as rootFile:
        rootFile.write(foxmlResource)
    rootFoxml = ET.fromstring(foxmlResource)
    rdfDatastream = None
    for datastream in rootFoxml.findall(FOXML_PREFIX + "datastream"):
        if datastream.get("ID") == "RELS-EXT":
            rdfDatastream = datastream

    for page in rdfDatastream.find(FOXML_PREFIX + "datastreamVersion").find(FOXML_PREFIX + "xmlContent").find(RDF_PREFIX + "RDF").find(RDF_PREFIX + "Description").findall(KRAMERIUS_PREFIX + "hasPage"):
        resource = page.get(RDF_PREFIX + "resource").replace("info:fedora/", "")
        resourceNoIndicator = resource.replace("uuid:", "")
        pageResponse = req.get(CONFIG_DATA['URL_TO_SRC'] + "/search/api/v5.0/item/" + resource + "/foxml").text
        with open(CONFIG_DATA['PATH_TO_FOXML'] + "/" + importDir + "/" + uuidNoIndicator + "/" + resourceNoIndicator + ".xml", "w+") as pageFile:
            pageFile.write(pageResponse)
    workCount = workCount + 1

#Logging 
if not filteredList:
    logString("No changes to be made.")
else:
    logString(str(workCount) + " works added to Kramerius.")

rename(CONFIG_DATA['PATH_TO_LIST_OF_NEW_IDS'], CONFIG_DATA['PATH_TO_LIST_OF_IDS'])