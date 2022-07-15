import xml.etree.ElementTree as ET
from os import walk, mkdir, remove
from os.path import exists
from uuid import uuid4
from datetime import datetime
import requests
from base64 import b64encode, b64decode
from sys import argv
from re import sub

OAI_PREFIX = '{http://www.openarchives.org/OAI/2.0/}'
METS_PREFIX = '{http://www.loc.gov/METS/}'
ALTO_PREFIX = '{http://www.loc.gov/standards/alto/ns-v3#}'
MODS_PREFIX = '{http://www.loc.gov/mods/v3}'
DC_PREFIX = '{http://www.openarchives.org/OAI/2.0/oai_dc/}'

PATH_TO_CONFIG = argv[1].strip()
CONFIG_DATA = {'PATH_TO_LIST_OF_IDS': 'current_ids_list.txt',
                'PATH_TO_LIST_OF_NEW_IDS': 'new_ids_list.txt',
                'PATH_TO_LOG': 'uibk.log',
                'TARGET_VC':'9c7cba10-2494-456e-bec0-2835549c894e',
                'UUIDS_PATH': '/home/c1081170/EOD-OPEN-data-synch-module/UIBK_new/uuids.txt',
                'BASE_PATH': '/home/c1081170/EOD-OPEN-data-synch-module/UIBK_new',
                'LIBRARY_CODE': 'P1-UIBK-mets',
                'PATH_TO_FOXML': '/home/c1081170/EOD-OPEN-data-synch-module/MZK/foxml'}

if exists(PATH_TO_CONFIG):
    with open(PATH_TO_CONFIG, "r") as configFile:
        for line in configFile:
            if line.find("=") != -1:
                before, after = line.split("=")
                CONFIG_DATA[before] = after.strip()
PATH_TO_OAI = '/home/c1081170/EOD-OPEN-data-synch-module/common_scripts/data/' + CONFIG_DATA['LIBRARY_CODE']


def logString(mssg, error = False):
    with open(CONFIG_DATA["PATH_TO_LOG"], "a+") as logFile:
        if error is False:
            logFile.write("[" + datetime.today().isoformat() + "] " + "[INFO] " + "[" + CONFIG_DATA["LIBRARY_CODE"] + "] " + mssg + "\n")
        else:
            logFile.write("[" + datetime.today().isoformat() + "] " + "[ERROR] " + "[" + CONFIG_DATA["LIBRARY_CODE"] + "] " + mssg + "\n")

def altoToText(alto):
    root = ET.fromstring(alto)
    if root.find(ALTO_PREFIX + 'Layout') is None:
        return ""
    lines = []
    for line in root.find(ALTO_PREFIX + 'Layout').find(ALTO_PREFIX + 'Page').find(ALTO_PREFIX + 'PrintSpace').find(ALTO_PREFIX + 'TextBlock').findall(ALTO_PREFIX + 'TextLine'):
        words = []
        for word in line.findall(ALTO_PREFIX + 'String'):
            words.append(word.get('CONTENT'))
        lines.append(" ".join(words))
    return "\n".join(lines)

globalData = {
    "date" : "",
    "vc" : CONFIG_DATA['TARGET_VC']
}

#if(not exists("collections.txt")):
#    globalData["vc"] = str(uuid4())
#    with open("collections.txt", "w+") as fw:
#        fw.write("vc:" + globalData["vc"] + "\n")
#    mkdir('data/vc:' + globalData["vc"])
#else:
#    with open("collections.txt", "r") as fr:
#        globalData["vc"] = fr.readline()
newIds = set()
with open(CONFIG_DATA['PATH_TO_LIST_OF_NEW_IDS'], "r") as frNewIDs:
    for oaiId in frNewIDs:
        newIds.add(oaiId.replace("\n", ""))
if newIds:
    logString("Starting to create FOXML.")

workCount = 0
if not exists(CONFIG_DATA['PATH_TO_FOXML']):
    mkdir(CONFIG_DATA['PATH_TO_FOXML'])
for root, dirs, files in walk(PATH_TO_OAI):
    for fil in files:
        root = ET.parse(PATH_TO_OAI + "/" + fil).getroot()
        for record in root.find(OAI_PREFIX + 'ListRecords').iter(OAI_PREFIX + 'record'):
            recordIdentifier = record.find(OAI_PREFIX + 'header').find(OAI_PREFIX + 'identifier').text
            if recordIdentifier in newIds:
                thisBookUuid = str(uuid4())
                childUuids = []
                page_number = 0
                if workCount % 30 == 0:
                    mkdir(CONFIG_DATA['PATH_TO_FOXML'] + '/importset_' + str(workCount // 30))
                logString("Record Identifier: " + recordIdentifier + " uuid: " + thisBookUuid)
                mkdir(CONFIG_DATA['PATH_TO_FOXML'] + '/' + '/importset_' + str(workCount // 30) + '/' + thisBookUuid)
                with open(CONFIG_DATA['UUIDS_PATH'], "a+") as col:
                    col.write(thisBookUuid + " | " + recordIdentifier + "\n")
                for page in record.find(OAI_PREFIX + 'metadata').find(METS_PREFIX + 'mets').find(METS_PREFIX + 'structMap').find(METS_PREFIX + 'div').findall(METS_PREFIX + 'div'):
                    pageUUID = str(uuid4())
                    childUuids.append(pageUUID)
                    page_number += 1
                    right_left = 'right' if page_number % 2 == 0 else 'left'
                    pageID = page.get('ID').replace('phys', '')
                    #print("Page ID: " + pageID + " :: " + pageUUID)
                    img_full = 'https://diglib.uibk.ac.at/ulbtirol/download/webcache/1504/' + pageID
                    image_name = pageID + '.jpg'
                    img_preview = 'https://diglib.uibk.ac.at/ulbtirol/download/webcache/1000/' + pageID
                    thumb = 'https://diglib.uibk.ac.at/ulbtirol/image/largethumb/' + pageID
                    alto_base64 = str(b64encode(requests.get('https://diglib.uibk.ac.at/ulbtirol/download/fulltext/alto3/' + pageID).text.encode(encoding='UTF-8'))).replace("b'", "").replace("'", "")
                    text_ocr_base64 = str(b64encode(altoToText(requests.get('https://diglib.uibk.ac.at/ulbtirol/download/fulltext/alto3/' + pageID).text).encode(encoding='UTF-8'))).replace("b'", "").replace("'", "")
                    #print(b64decode(b64encode(altoToText(requests.get('https://diglib.uibk.ac.at/ulbtirol/download/fulltext/alto3/' + pageID).text).encode(encoding='UTF-8'))).decode('utf-8'))

                    with open(CONFIG_DATA["BASE_PATH"] + "/foxml-model.xml", "r") as template:
                        modelText = template.read()
                    
                    globalData["date"] = datetime.now().isoformat()
                    replacedText = modelText.format(DATE = globalData["date"],
                                                    THUMB = thumb,
                                                    PREVIEW = img_preview,
                                                    IMG_FULL = img_full,
                                                    TEXT_OCR_BASE64 = text_ocr_base64,
                                                    ALTO_BASE64 = alto_base64,
                                                    UUID = pageUUID,
                                                    RIGHT_LEFT = right_left,
                                                    PAGE_NUMBER = page_number,
                                                    IMAGE_NAME = image_name,
                                                    VIRTUAL_COLLECTION = globalData["vc"])
                    
                    with open(CONFIG_DATA['PATH_TO_FOXML'] + '/importset_' + str(workCount // 30) + '/' + thisBookUuid + '/' + pageUUID + '.xml', 'w+') as pageFile:
                        pageFile.write(replacedText)
                #mods = record.find(OAI_PREFIX + 'metadata').find(METS_PREFIX + 'mets').find(METS_PREFIX + 'dmdSec').find(METS_PREFIX + 'mdWrap').find(METS_PREFIX + 'xmlData').find(MODS_PREFIX + 'mods').text
                dcRaw = requests.get('https://diglib.uibk.ac.at/ulbtirol/oai?verb=GetRecord&metadataPrefix=oai_dc&identifier=' + recordIdentifier.replace("oai:diglib.uibk.ac.at/:", "")).text
                oai_dc = dcRaw.split("oai_dc:dc")[1].replace('xmlns:oai_dc="http://www.openarchives.org/OAI/2.0/oai_dc/" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/oai_dc/ http://www.openarchives.org/OAI/2.0/oai_dc.xsd">', '')[:-2]
                modsRaw = requests.get('https://diglib.uibk.ac.at/oai/?verb=GetRecord&metadataPrefix=mods&identifier=' + recordIdentifier.replace("oai:diglib.uibk.ac.at/:", "")).text
                modsWithoutBeginning = sub(r'< xmlns:mods[^>]*>', '', '<' + modsRaw.split("mods:mods")[1][:-2])
                mods = sub(r'<mods:extension>.*<\/mods:extension>', '', modsWithoutBeginning)
                children_rdf = ''
                with open(CONFIG_DATA["BASE_PATH"] + "/rdf-resource-model.xml", "r") as rdfModel:
                    rdfModelText = rdfModel.read()
                for pageUID in childUuids:
                    children_rdf += rdfModelText.format(UUID = pageUID) + "\n\t"
                with open(CONFIG_DATA["BASE_PATH"] + "/master-foxml-model.xml", "r") as masterModel:
                    masterModelText = masterModel.read()
                globalData["date"] = datetime.now().isoformat()
                replacedTextMaster = masterModelText.format(MODS = mods,
                                                            OAI_DC = oai_dc,
                                                            CHILDREN_RDF = children_rdf,
                                                            VIRTUAL_COLLECTION = globalData["vc"],
                                                            DATE = globalData["date"],
                                                            UUID = thisBookUuid)
                with open(CONFIG_DATA['PATH_TO_FOXML'] + '/importset_' + str(workCount // 30) + '/' + thisBookUuid + '/' + thisBookUuid + '.xml', "w+") as rootFOXMLfile:
                    print('Opened ' + CONFIG_DATA['PATH_TO_FOXML'] + '/importset_' + str(workCount // 30) + '/' + thisBookUuid + '/' + thisBookUuid + '.xml')
                    rootFOXMLfile.write(replacedTextMaster)
                workCount += 1

with open(CONFIG_DATA["PATH_TO_LIST_OF_IDS"], "a+") as fw:
    fw.write('\n'.join(newIds) + "\n")