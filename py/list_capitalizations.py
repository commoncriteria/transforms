#!/usr/bin/env python3
"""
Extracts all the defined capitalizations (also incorrectly known as acronyms) from a PP
"""

import sys
import xml.etree.ElementTree as ET
import os

def extract_from_doc(path):
    ns = {'cc': "https://niap-ccevs.org/cc/v1",
      'sec': "https://niap-ccevs.org/cc/v1/section",
      'htm': "http://www.w3.org/1999/xhtml"}
    root = ET.parse(path).getroot()
    for term in root.findall(".//cc:term", ns):
        if "abbr" in term.attrib:
            print(term.attrib["abbr"])
        if "plural" in term.attrib:
            print(term.attrib["plural"])

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: <protection-profile>")
        sys.exit(0)
    else:
        for arg in sys.argv[1:]:
            extract_from_doc(arg)
