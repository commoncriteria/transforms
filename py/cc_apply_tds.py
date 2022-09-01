#!/usr/bin/env python3
import sys
import pathlib
import xml.etree.ElementTree as ET

ns = {'cc': "https://niap-ccevs.org/cc/v1",
      'sec': "https://niap-ccevs.org/cc/v1/section",
      'htm': "http://www.w3.org/1999/xhtml"}

def get_num(fullpath):
    path = pathlib.Path(fullpath)
    return int( path.stem )

def log(msg):
    sys.stderr.write(msg)
    sys.stderr.write("\n")


if __name__ == "__main__":
    if len(sys.argv)==1:
        print("Usage: <input-file> [<td1> [<td2> ...]]")
        sys.exit(0)
    doc = ET.parse(sys.argv[1])
    root = doc.getroot()
    parent_map = {c: p for p in root.iter() for c in p}


    # Need to sort
    tds = sys.argv[2:]
    tds.sort(key=get_num)
    for aa in tds:
        td = ET.parse(aa).getroot()
        replaces = td.findall(".//cc:replace", ns)
        for replace in replaces:
            for xpath_spec in replace.findall(".//cc:xpath-specified", ns):
                xpath = "."+ xpath_spec.attrib["xpath"]
                replaced = root.find(xpath, ns)
                if replaced is None:
                    log("Cannot find node")
                    continue
                parent = parent_map[replaced]
                if parent is None:
                    log("Cannot find parent")
                    continue
                kid_cache = []
                for kid in list(parent):
                    if kid == replaced:
                        for newkids in list(xpath_spec):
                            kid_cache.append(newkids)
                    else:
                        kid_cache.append(kid)
                    parent.remove(kid)
                for kid in kid_cache:
                    parent.append(kid)
    print(ET.tostring(root, encoding='unicode', method='xml'))
