#!/usr/bin/env python3
""" 
Preprocesses a module.
* Downloads all remote base-pp definitions and saves them based on their relative index
"""

import sys
import xml.etree.ElementTree as ET
import urllib.request
import shutil
import os

PPNS='https://niap-ccevs.org/cc/v1'
HTMNS="http://www.w3.org/1999/xhtml"
ns={"cc":PPNS, "htm":HTMNS}


if len(sys.argv) != 3:
    #        0                        1           
    print("Usage: <protection-profile> <out-dir>")
    sys.exit(0)


if sys.argv[1]=="-":
    root=ET.fromstring(sys.stdin.read())
else:
    root=ET.parse(sys.argv[1]).getroot()

indy=0
for el in root.findall(".//cc:base-pp",ns):
    outfile=os.path.join(sys.argv[2], str(indy)+".xml")
    with urllib.request.urlopen(el.attrib['xmlurl']) as response, open(outfile, 'wb') as out_file:
        shutil.copyfileobj(response, out_file)
    indy=indy+1


