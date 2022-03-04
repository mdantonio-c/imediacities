#!.venv/bin/python3
"""
Procedure to fix and rename collection 'name' tag to 'title' for generated XML records.
A list of filename to be updated is return in xml_updates.json.

Prepare a virtual environment:
$virtualenv -p python3 .venv
$source .venv/bin/activate

usage: rename_collection_title.py file [file ...]
(.venv)$ ./rename_collection_title.py target_dir/*.xml
"""

import argparse
import json
from pathlib import Path
from xml.etree import ElementTree as ET

EFG_NAMESPACE = "http://www.europeanfilmgateway.eu/efg"
ET.register_namespace("", EFG_NAMESPACE)

parser = argparse.ArgumentParser()
parser.add_argument("file", type=argparse.FileType("r"), nargs="+")

args = parser.parse_args()
collection_counter = 0
name_counter = 0
title_counter = 0
fileset = []

for f in args.file:
    xmlTree = ET.parse(f)
    rootElement = xmlTree.getroot()
    node = rootElement.find(
        ".//{http://www.europeanfilmgateway.eu/efg}relCollection[1]"
    )
    if node is not None:
        collection_counter += 1
        name_el = node.find("{http://www.europeanfilmgateway.eu/efg}name")
        if name_el is not None:
            name_counter += 1
            # need to be updated
            name_el.tag = "{http://www.europeanfilmgateway.eu/efg}title"
            # save changes
            xmlTree.write(f.name, encoding="UTF-8", xml_declaration=True)
            # add filename to the output for reprocessing
            fileset.append(Path(f.name).name)
            continue
        title_el = node.find("{http://www.europeanfilmgateway.eu/efg}title")
        if title_el is not None:
            # it's ok: no nothing
            title_counter += 1

print(f"Number of xml to be updated: {len(fileset)}")
if len(fileset) > 0:
    with open("xml_updates.json", "w", encoding="utf-8") as out:
        json.dump(fileset, out, ensure_ascii=False, indent=2)
print(f"Total number of collections: {collection_counter}")
print(f"Total number of collection <name>: {name_counter}")
print(f"Total number of collection <title>: {title_counter}")
