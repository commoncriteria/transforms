#!/usr/bin/env python3
import sys
import pathlib
#import xml.etree.ElementTree as ET
import lxml.etree as ET
import argparse
import pp_module
import pp_util


            
        
    
def make_mod(path):
    print("Making mod: "+path)
    doc = ET.parse(path).getroot()
    boilerplate = ET.parse("/home/kevin/commoncriteria/bluetooth/transforms/xsl/boilerplates.xml")
    # print("Tag is "+doc.tag)
    if doc.tag == "{https://niap-ccevs.org/cc/v1}Module":
        pp = pp_module.ppmod( doc, "../../output", boilerplate )
    else:
        raise Exception("Unhandled")

    out = open("/tmp/abc.xml", "w+")
    out.write(pp.to_html())
    out.close()
    
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert an XML Protection Profile Definition to a readable HTML document')
    # parser.add_argument('integers', metavar='N', type=int, nargs='+',
    #                     help='an integer for the accumulator')
    # parser.add_argument('--sum', dest='accumulate', action='store_const',
    #                     const=sum, default=max,
    #                     help='sum the integers (default: find the max)')
    parser.add_argument('-w', nargs="?")
    parser.add_argument('output-file', nargs="?", help="Path to output file")
    parser.add_argument('input-file' , help="Path to the XML definition")
    args = parser.parse_args()
    make_mod(vars(args)["input-file"])
    print(str(args))

    # print(args.accumulate(args.integers))
