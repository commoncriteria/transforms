#!/usr/bin/env python3
"""
Parses a PP retrieves the packages or PPs that are requirements.
"""

# from io import StringIO
import sys
import requests
import xml.etree.ElementTree as ET


def warn(msg):
    log(2, msg)


def err(msg):
    sys.stderr.write(msg)
    sys.exit(1)


def debug(msg):
    log(5, msg)


def log(level, msg):
    sys.stderr.write(msg)
    sys.stderr.write("\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        #        0                        1
        print("Usage: <protection-profile> [directory]")
        sys.exit(0)
    # Split on equals
    if sys.argv[1] == "-":
        root = ET.fromstring(sys.stdin.read()).getroot()
    else:
        root = ET.parse(sys.argv[1]).getroot()
    ns = { 'cc':"https://niap-ccevs.org/cc/v1",
        'sec':"https://niap-ccevs.org/cc/v1/section",
        'htm':"http://www.w3.org/1999/xhtml" }
    ctr = 1;
    for pkg in root.findall(".//cc:include-pkg/cc:raw-url" , ns):
       url = "".join(pkg.text.split())
       open( str(ctr)+".xml", 'wb').write( requests.get( url ) )
       ctr = ctr + 1

