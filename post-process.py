#!/usr/bin/env python3
""" 
Module that fixes internal references and counters (which are hard to do
with XSLT).
"""

from io import StringIO 
import re
import sys
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape
def err(msg):
    sys.stderr.write(msg)
    sys.exit(1)

def debug(msg):
    log(5, msg)

def log(level, msg):
    sys.stderr.write(msg)
    sys.stderr.write("\n")

def get_appendix_prefix(num):
    if num > 26:
        err("Cannot handle more than 26 appendices")
    ABC=['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
    return ABC[num] 

class State:
    def __init__(self, root):
        self.root = root
        self.parent_map = {c:p for p in self.root.iter() for c in p}
        self.create_classmapping()


    def create_classmapping(self):
        self.classmap={}
        for el in self.root.findall(".//*[@class]"):
            classes = el.attrib["class"].split(",")
            for clazz in classes:
                # If we already have this class in the classmap
                if clazz in self.classmap:
                    # Grab the old
                    clazzset = self.classmap[clazz]
                    clazzset.add(el)
                else:
                    self.classmap[clazz]={el}


    def to_html(self):
        return """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
""" + self.to_html_helper(self.root)
        

    def to_html_helper(self, elem):
        tagr = elem.tag.split('}')
        noname=tagr[len(tagr)-1]
        if noname=="br":
            return "<br/>"
        ret="<" + noname
        for attrname in elem.attrib:
            ret = ret + " " + attrname + "='"+ escape(elem.attrib[attrname])+"'"
        ret=ret+">"
        if elem.text:
            ret += escape(elem.text)
        for child in elem:
            ret += self.to_html_helper(child)
            if child.tail:
                ret += child.tail
        ret= ret + '</' + noname +'>'
        return ret

    def fix_counters(self):
        # Bail if there are no ctrs
        if not "ctr" in self.classmap:
            return
        countables = self.classmap['ctr']
        occurs={}
        for countable in countables:
            typee = countable.attrib['data-counter-type']
            if not typee in occurs:
                occurs[typee]=0
            occurs[typee]+=1
            countable.find("*[@class='counter']").text = str(occurs[typee])

            refclass=countable.attrib["data-myid"]+"-ref"
            if refclass in self.classmap:
                refs=self.classmap[refclass]
                for ref in refs:
                    ref.find("*[@class='counter']").text= str(occurs[typee])

    def fix_tooltips(self):
        if not "tooltiptext" in self.classmap:
            return
        for elem in self.classmap["tooltiptext"]:
            attribs=self.parent_map[elem].attrib
            if "class" in attribs:
                attribs["class"]=attribs["class"]+",tooltipped"
            else:
                attribs["class"]="tooltipped"

    def fix_index_refs(self):
        # Bail if there are no dynamic references
        if not "dynref" in self.classmap:
            return
        # Gather them
        brokeRefs = self.classmap["dynref"]
        for brokeRef in brokeRefs:
            linkend=brokeRef.attrib["href"][1:]
            target=root.find(".//*[@id='"+linkend+"']")
            brokeRef.text = target.text


    def fix_indices(self):
        # Find the table of contents
        toc=self.root.find(".//*[@id='toc']")
        # Initialize the index number generator
        inums=[0,0,0,0,0,0]
        # Initialize the is_alpha switch
        is_alpha=False
        # Gather all elements with a data-level
        eles=self.root.findall(".//*[@data-level]")
        #
        base=-1
        # Go through the elemeents
        for aa in range( len(eles)):
            level=eles[aa].attrib["data-level"]

            # If this is the first time we see an appendix
            if level == 'A' and not is_alpha:
                inums=[-1,0,0,0,0]
                is_alpha=True

            # Turn it into an index
            if level == 'A':
                level = 0
            else:
                level=int(level)
                if base==-1:
                    base=level
                level=level-base


            # If we have to pad out
            while level > len(inums):
                inums.append(0)
            # If we go up one set 
            if level+1 < len(inums):
                inums[level+1]=0
                
            inums[level]+=1
            
            if is_alpha and level == 0:
                prefix= "Appendix " + get_appendix_prefix(inums[0]) + " - "
            elif is_alpha:
                prefix = get_appendix_prefix(inums[0])
            else:
                prefix = str(inums[0])
            spacer=""
            for bb in range(1, level+1):
                prefix = prefix + "." + str(inums[bb])
                spacer=spacer+"&nbps;"
                
            # Fix inline index number
            spany = ET.Element("span")
            spany.text = eles[aa].text

            if eles[aa].text:
                eles[aa].text = prefix + " " + eles[aa].text
            else:
                eles[aa].text = prefix
            entry = ET.Element("a")
            entry.attrib['href'] = '#'+escape(eles[aa].attrib['id'])
            entry.attrib['style']= 'text-indent:'+str(level*10)+ 'px'

            entry.text=prefix
            entry.append(spany)
            toc.append(entry)


    def handle_element(self, elem):
        pass

def getalltext(elem):
    ret=""
    if elem.text:
        ret=elem.text
    for child in elem:
        ret=ret+getalltext(child)+child.tail


if __name__ == "__main__":
    if len(sys.argv) < 2:
        #        0                        1           
        print("Usage: <protection-profile>[::<output-file>]")
        sys.exit(0)

    # Split on colon
    out=sys.argv[1].split("::")
    infile=out[0]
    outfile=""
    if len(out) < 2:
        outfile=infile.split('.')[0]+".html"
    else:
        outfile=out[1]

    if infile=="-":
        root=ET.fromstring(sys.stdin.read())
    else:
        root=ET.parse(infile).getroot()

    

    state = State(root)
    state.fix_indices()
    state.fix_index_refs()
    state.fix_counters()
    state.fix_tooltips()
    with open(outfile, "w+") as outstream:
        outstream.write(state.to_html())

