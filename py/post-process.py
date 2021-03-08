#!/usr/bin/env python3
"""
Module that fixes internal references and counters (which are hard to do
with XSLT).
"""

# from io import StringIO
import re
import sys
import string
import xml.etree.ElementTree as ET
from xml.sax.saxutils import quoteattr, escape


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


A_UPPERCASE = ord('A')
ALPHABET_SIZE = 26

def _decompose(number):
    """Generate digits from `number` in base alphabet, least significants
    bits first.

    Since A is 1 rather than 0 in base alphabet, we are dealing with
    `number - 1` at each iteration to be able to extract the proper digits.
    """
    while number:
        number, remainder = divmod(number-1, ALPHABET_SIZE)
        yield remainder


def base_10_to_alphabet(number):
    """Convert a decimal number to its base alphabet representation"""
    return ''.join(
            chr(A_UPPERCASE + part)
            for part in _decompose(number+1)
    )[::-1]

def backslashify(phrase):
    return re.sub("([_.^-])", r"\\\1", phrase)


class State:
    def __init__(self, root):
        self.root = root
        self.parent_map = {c: p for p in self.root.iter() for c in p}
        self.create_classmapping()
        self.abbrs = []
        self.key_terms = []
        self.plural_to_abbr = {}
        self.regex = None

    def create_classmapping(self):
        self.classmap = {}
        for el in self.root.findall(".//*[@class]"):
            classes = el.attrib["class"].split(",")
            # Go through all the classes the elment is a part of
            for clazz in classes:
                # If we already have this class in the classmap
                if clazz in self.classmap:
                    # Grab the old
                    clazzset = self.classmap[clazz]
                    # We're working with a list here, not a set
                    # Should really only not meet this if the
                    # input document has an element where a
                    # class is listed twice
                    if el not in clazzset:
                        clazzset.append(el)
                else:
                    self.classmap[clazz] = [el]

    def getElementsByClass(self, clazz):
        if clazz in self.classmap:
            return self.classmap[clazz]
        else:
            return []

    def cross_reference_cc_items(self):
        for clazz in {"assumption", "threat", "OSP", "SOE", "SO",  "componentneeded","defined"}:
            for el in self.getElementsByClass(clazz):
                if "id" in el.attrib:
                    self.add_to_regex(el.attrib["id"])

    def build_comp_regex(self):
        comps = self.getElementsByClass('reqid') +\
            self.getElementsByClass('comp')
        for comp in comps:
            if 'id' in comp.attrib:
                self.add_to_regex(comp.attrib["id"])
            else:
                # The MDF has some unorthodox items
                print("Cannot find: "+comp.text)

    def build_termtable(self):
        for term in self.getElementsByClass('term'):
            if 'data-plural' in term.attrib:
                plural = term.attrib['data-plural']
                self.plural_to_abbr[plural] = term.text
                self.add_to_regex(plural)
            self.add_to_regex(term.text)
            self.abbrs.append(term.text)

    def add_to_regex(self, word):
        if len(word) > 1 and not(word.startswith(".")):
            self.key_terms.append(backslashify(word))

    def to_html(self):
        try:
            # Sort them so longer terms are searched first so
            # that shorter terms embedded in larger terms don't
            # interfere with longer terms being found.
            self.key_terms.sort(key=len, reverse=True)
            regex_str = "(?<!-)\\b(" + "|".join(self.key_terms) + ")\\b"
            self.regex = re.compile(regex_str)
        except re.error:
            warn("Failed to compile regular expression: " +
                 regex_str[:-1]+")\\b")
        self.ancestors = []
        return """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
""" + self.to_html_helper(self.root)

    def is_in_non_xrefable_section(self):
        return \
            "a"    in self.ancestors or "abbr"    in self.ancestors or\
            "dt"   in self.ancestors or "no-link" in self.ancestors or\
            "h1"   in self.ancestors or "h2"      in self.ancestors or\
            "h3"   in self.ancestors or "h4"      in self.ancestors or\
            "head" in self.ancestors or "script"  in self.ancestors

    def handle_text(self, parent, text):
        etext = escape(text)
        if self.is_in_non_xrefable_section():
            return etext
        return self.discover_xref(etext)

    def discover_xref(self, etext):
        if self.regex is None:
            return etext
        last = 0
        ret = ""
        for mat in self.regex.finditer(etext):
            # Append the characters between the last find and this
            ret += etext[last:mat.start()]
            # Move the last indexer up
            last = mat.end()
            target = mat.group()
            if mat.group() in self.plural_to_abbr:
                target = self.plural_to_abbr[mat.group()]
            # If target maches  an abbreviation
            if target in self.abbrs:
                ret += '<abbr class="dyn-abbr"><a href="#abbr_' + target+'">'
                ret += mat.group()+'</a></abbr>'
            else:
                ret += '<a href="#'+mat.group()+'">'+mat.group()+'</a>'
        ret += etext[last:]
        return ret

    def to_html_helper(self, elem):
        """Function that turns document in HTML"""
        tagr = elem.tag.split('}')
        noname = tagr[len(tagr)-1]
        # Breaks elements are converted to empty tags
        if noname == "br":
            return "<br/>"
        if "class" in elem.attrib and elem.attrib["class"] == 'no-link':
            self.ancestors.append("no-link")
#        if noname=="span" and len(elem)==0 and elem.text is None:
#            return "JJJ"
        else:
            self.ancestors.append(noname)
        # Everything else is beginning and end tags (even if they're empty)
        ret = "<" + noname
        for attrname in elem.attrib:
            ret = ret + " " + attrname + "=" + quoteattr(elem.attrib[attrname])
        ret = ret+">"
        if elem.text:
            ret += self.handle_text(elem, elem.text)
        for child in elem:
            ret += self.to_html_helper(child)
            if child.tail:
                ret += self.handle_text(elem, child.tail)
        ret = ret + '</' + noname + '>'
        self.ancestors.pop()
        return ret

#
# Counters:
#    Have 'class' attribute with value is 'ctr'
#    Have 'data-counter-type' attribute with value of counter-type  
#    Have a subelement with the 'class' attribute equal to counter (which is where the index is put)
#    Have 'data-myid' attribute 
#
# Counter References:
#    Have 'class' attribute with value equal to the thing their referencing plus the string '-ref'
#    Have a subelement with the 'class' attribute equal to counter (which is where the index is put)

    def fix_counters(self):
        # Bail if there are no ctrs
        occurs = {}
        # Go through all the counters
        for countable in self.getElementsByClass('ctr'):   
            # Get the type of counter
            typee = countable.attrib['data-counter-type']
            # If we haven't seen it yet
            if typee not in occurs:
                # Make a list
                occurs[typee] = 0
            # Increment by one
            occurs[typee] += 1
            # Find the subelement with the class attribute equailt to 'counter'
            # And set it's value to the counter's value.
            count_str = str(occurs[typee])
            countable.find("*[@class='counter']").text = count_str
            self.fix_this_counter_refs(countable.attrib["data-myid"], count_str)

    def fix_this_counter_refs(self, ctr_id, count_str):
        refclass = ctr_id + "-ref"
        for ref in self.getElementsByClass(refclass):
            print("Found format attribute " + safe_get_attribute(ref, "format", default="nt"))
            ref.find("*[@class='counter']").text = count_str

    def fix_tooltips(self):
        for elem in self.getElementsByClass("tooltiptext"):
            attribs = self.parent_map[elem].attrib
            if "class" in attribs:
                attribs["class"] = attribs["class"]+",tooltipped"
            else:
                attribs["class"] = "tooltipped"

    def fix_index_refs(self):
        for brokeRef in self.getElementsByClass("dynref"):
            linkend = brokeRef.attrib["href"][1:]
            target = root.find(".//*[@id='"+linkend+"']")
            if not hasattr(target, 'text'):
                print("Target does not have text field")
            if not hasattr(brokeRef, 'text')\
               or brokeRef.text == None:
                brokeRef.text = " "
            try:
                # Append ref text.
                brokeRef.text = brokeRef.text + target.text
            except AttributeError:
                warn("Failed to find an element with the id of '"+linkend+"'")

    def fix_indices(self):
        # Find the table of contents
        toc = self.root.find(".//*[@id='toc']")
        # Initialize the index number generator
        inums = [0, 0, 0, 0, 0, 0]
        # Initialize the is_alpha switch
        is_alpha = False
        # Gather all elements with a data-level
        eles = self.root.findall(".//*[@data-level]")
        #
        base = -1
        # Go through the elemeents
        for aa in range(len(eles)):
            level = eles[aa].attrib["data-level"]

            # If this is the first time we see an appendix
            if level == 'A' and not is_alpha:
                inums = [-1, 0, 0, 0, 0]
                is_alpha = True

            # Turn it into an index
            if level == 'A':
                level = 0
            else:
                level = int(level)
                if base == -1:
                    base = level
                level = level-base
            # If we have to pad out
            while level > len(inums):
                inums.append(0)
            # If we go up one set
            if level+1 < len(inums):
                inums[level+1] = 0
            inums[level] += 1
            if is_alpha and level == 0:
                prefix= "Appendix " + base_10_to_alphabet(inums[0]) + " - "
            elif is_alpha:
                prefix = base_10_to_alphabet(inums[0])
            else:
                prefix = str(inums[0])
            spacer = ""
            for bb in range(1, level+1):
                prefix = prefix + "." + str(inums[bb])
                spacer = spacer + "&nbps;"

            # Fix inline index number
            spany = ET.Element("span")
            spany.text = eles[aa].text

            if eles[aa].text:
                eles[aa].text = prefix + " " + eles[aa].text
            else:
                eles[aa].text = prefix
            entry = ET.Element("a")
            # Why would an ID have to be escaped?
            # entry.attrib['href'] = '#'+escape(eles[aa].attrib['id'])
            entry.attrib['href'] = '#'+eles[aa].attrib['id']
            entry.attrib['style'] = 'text-indent:'+str(level*10) + 'px'

            entry.text = prefix
            entry.append(spany)
            toc.append(entry)

    def handle_element(self, elem):
        pass


def getalltext(elem):
    ret = ""
    if elem.text:
        ret = elem.text
    for child in elem:
        ret = ret+getalltext(child)+child.tail

def safe_get_attribute(element, attribute, default=""):
    if attribute in element.attrib:
        return element.attrib[attribute]
    else:
        return default

if __name__ == "__main__":
    if len(sys.argv) < 2:
        #        0                        1
        print("Usage: <protection-profile>[=<output-file>]")
        sys.exit(0)
    # Split on equals
    out = sys.argv[1].split("=")
    infile = out[0]
    outfile = ""
    if len(out) < 2:
        outfile = infile.split('.')[0]+".html"
    else:
        outfile = out[1]

    if infile == "-":
        root = ET.fromstring(sys.stdin.read())
    else:
        root = ET.parse(infile).getroot()
    state = State(root)
    state.fix_indices()
    state.fix_index_refs()
    state.fix_counters()
    state.fix_tooltips()
    state.cross_reference_cc_items()
    state.build_comp_regex()
    state.build_termtable()

    if sys.version_info >= (3, 0):
        with open(outfile, "w+", encoding="utf-8") as outstream:
            outstream.write(state.to_html())
    else:
        with open(outfile, "w+") as outstream:
            outstream.write(state.to_html().encode('utf-8'))
