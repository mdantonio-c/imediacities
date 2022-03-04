#!/usr/bin/python3
"""
Procedure to copy a list of filenames contained in a JSON input file
from a source to a destination directory.

usage: cp_xml_records.py [-h] [-s SOURCE] [-d DEST] file
"""

import argparse
import json
import shutil
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("file", type=argparse.FileType("r"))
parser.add_argument("-s", "--source", help="copy all the files from the SOURCE")
parser.add_argument("-d", "--dest", help="copy all the files from the SOURCE into DEST")

args = parser.parse_args()
source = Path(args.source) if args.source and Path(args.source).exists() else Path.cwd()
dest = Path(args.dest) if args.dest and Path(args.dest).exists() else Path.cwd()
print(f"Copy source file(s) to: {dest}")

with open(args.file.name) as json_file:
    data = json.load(json_file)
    print(f"Total number of file to copy: {len(data)}")
    counter = 0
    for filename in data:
        file_to_copy = source.joinpath(filename)
        if not file_to_copy.exists():
            print(f"ERROR: file {filename} does NOT esist in source dir {source}")
            continue
        # print(f"write file {file_to_copy} to {dest}")
        shutil.copy(file_to_copy, dest)
        counter += 1
    print(f"Total number of file copied: {counter}")
