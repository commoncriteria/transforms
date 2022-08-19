#!/usr/bin/env python3
import sys
import xml.etree.ElementTree as ET

ns = {'cc': "https://niap-ccevs.org/cc/v1",
      'sec': "https://niap-ccevs.org/cc/v1/section",
      'htm': "http://www.w3.org/1999/xhtml"}


if __name__ == "__main__":
    if len(sys.argv)==1:
        print("Usage: <input-file> [<td1> [<td2> ...]]")
        sys.exit(0)
    doc = ET.parse(sys.argv[1])
    root = doc.getroot()
    # Need to sort
    for aa in sys.argv[2:]:
        td = ET.parse(aa).getroot()
        replaces = td.findall(".//cc:replace", ns)
        for replace in replaces:
            for xpath_spec in replace.findall(".//cc:xpath-specified", ns):
                xpath = "."+ xpath_spec.attrib["xpath"]
                replaced = root.find(xpath)
                if replaced is not None:
                    for kid in list(replaced):
                        replaced.remove(kid)
                    for kid in xpath_spec:
                        replaced.append(kid)
    print(ET.tostring(root, encoding='unicode', method='xml'))
