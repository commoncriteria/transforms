#!/usr/bin/env python3
import sys
import pathlib
#import xml.etree.ElementTree as ET
import lxml.etree as ET
import argparse
import pp_module
import pp_util

            
def write_out_doc(doc, place):
    out = open(place, "w+")
    result = ET.tostring(doc,
                        xml_declaration=True,
                        doctype='<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">',
                        encoding='utf-8',
                        standalone=False,
                        with_tail=False,
                        method='xml',
                        pretty_print=True)
    out.write(result.decode())
    out.close()
    
def make_mod(path):
    print("Making mod: "+path)
    doc = ET.parse(path).getroot()
    boilerplate = ET.parse("../xsl/boilerplates.xml")
    # print("Tag is "+doc.tag)
    if doc.tag == "{https://niap-ccevs.org/cc/v1}Module":
        pp = pp_module.ppmod( doc, "../../output", boilerplate )
    else:
        raise Exception("Unhandled")
    html_doc = pp.to_html()
    
    write_out_doc(html_doc, "/tmp/abc.html")
    sd = pp.to_sd()
    write_out_doc(sd, "/tmp/abc-sd.html")
    
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
