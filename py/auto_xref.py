import re
import pp_util

HTM_E=pp_util.get_HTM_E()

def backslashify(phrase):
    """
    Makes a phrase suitable for searching with regular expressions by
    adding the necessary backslashes.

    :param phrase: The phrase in question
    :returns: A string that can be searched using regex
    """
    return re.sub("([][_.^()-/])", r"\\\1", phrase)


class auto_xreffer:

    
    def __init__(self):
        # self.discoverables_to_ids = {}        # List of terms we're looking for
        self.root = None

    def xrefs_in_text(self, node, content, regex, insertspot=0):
        """
        Discovers keywords in nodes and adds anchors appropriately.

        :param  node: The node in question
        :param  content: The original text content of the node
        :param  regex: The regular expression that finds keywords
        :param  insertspot: Index where new nodes should go.
        :returns What should go in the node's text field
        """
        if self.root == None:
            self.root = node
        
        if regex is None or content is None:
            return content
        matches = regex.finditer(content)
        try:
            match=next(matches)
        except:
            return content
        origtext = content
        ret = origtext[:match.start()]
        last=match.end()
        matchtext = match.group()
        id = self.discoverables_to_ids[matchtext]
        
        prevnode = self.make_disco_link(id, matchtext)
        newnodes=[prevnode]
        for match in matches:
            prevnode.tail = origtext[last:match.start()]
            last = match.end()
            id = self.discoverables_to_ids[match.group()]
            prevnode = self.make_disco_link(id, match.group())
            newnodes.append(prevnode)
        prevnode.tail = origtext[match.end():]
        for newkids in newnodes:
            node.insert(insertspot, newkids)
            insertspot+=1
        return ret
            
    def add_xrefs_recur(self, node, regex):
        """
        Discovers xrefs in the text of the current node
        and its descendants.
        
        :param  node: The root of the subtree
        :param  regex: The regular expresssion that finds
        keywords
        """
        
        if self.is_non_xrefable_section(node):
            return
        origchildren = node.iterchildren()
        node.text = self.xrefs_in_text(node, node.text, regex)
        for child in origchildren:
            self.add_xrefs_recur(child, regex)
            insertspot=node.index(child)+1
            child.tail = self.xrefs_in_text(node, child.tail, regex, insertspot)

        
    
    def register_keyterm(self, word, id):
        """
        Regisers a keyword with the automatic cross-referencer.
        
        :param  word: The string to look for.
        :param  id: The ID that is the target.
        """
        pass
        # if len(word) > 1 and not(word.startswith(".")):
        #     self.discoverables_to_ids[word]=id


    def is_non_xrefable_section(self, node):
        """
        Decides whether the current node can contain an anchor tag.

        :param node: The HTML node in question.
        :returns True if we can put an anchor tag. False otherwise.
        """
        
        if node.tag == "a"    or node.tag == "abbr"    or\
           node.tag == "dt"   or node.tag == "no-link" or\
           node.tag == "h1"   or node.tag == "h2"      or\
           node.tag == "h3"   or node.tag == "h4"      or\
           node.tag == "head" or node.tag == "script"  or\
           node.tag == "svg"  or node.tag == "th": 
            return True

        if has_class(node.attrib, "term"):
            return True

        # if "class" in node.attrib and node.attrib["class"]:
        #     classes = node.attrib["class"].split(" ")
        #     if "term" in classes:
                # return True
        return False

    def make_disco_link(self, id, matchtext):
        """
        Makes a XRef link for a discovered keyword.
        It should looks like ie <a href='#{id}'>${matchtext}</a>.

        :param  id: The ID of the target node 
        :param  matchtext: The text that should be linked
        :returns An HTML anchor element.
        """
        
        attrs={"class":"discovered", "href":"#"+id}
        full_el = self.root.find(".//*[@id='long_"+id+"']")
        if full_el is not None:
            attrs["class"]="discovered abbr"
            attrs["title"]=full_el.text
        return HTM_E.a(attrs, matchtext)
    

    
    def add_discoverable_xrefs(self, node):
        """
        Starts the process of finding keywords and adds appropriate 
        hyperlinks to them.
        
        :param node: The root HTML node
        :param abbrs: Dictionary for tooltips
        """
        # if len(self.discoverables_to_ids)==0:
        #     return

        self.discoverables_to_ids={}
        find_definitions(node, self.discoverables_to_ids)
        keys=sorted(self.discoverables_to_ids.keys(), key=len, reverse=True)
#        regex=re.compile('\\B\\b\\B')

        withseps=""
        withouts=""
        for key in keys:
            if "[" in key:
                withseps+=backslashify(key)+"|"
            else:
                withouts+=backslashify(key)+"|"
        regex_str=""
        if withseps != "":
            regex_str="("+withseps[:-1]+")|"
        if withouts != "":
            regex_str+="(?<!-)\\b("+withouts[:-1]+")\\b|"
        regex_str=regex_str[:-1]
                
        # keys = sorted(self.discoverables_to_ids.keys(), key=len, reverse=True)
        # bracketed=set()
        # for key in keys:
        #     if key[0]=='[':
        #         keys.remove(key)
        #         bracketed.add(key)
        # biblio_part=""
        # if len(bracketed)>0:
        #     biblio_part = "("+"|".join(map(backslashify,bracketed))+")|"
        # regex_str = biblio_part+"(?<!-)\\b("+"|".join(map(backslashify, keys))+")\\b"
        # print("Regex string is: "+regex_str )
        regex = re.compile(regex_str)
        self.add_xrefs_recur(node, regex)        

defreg = re.compile("\\bdefinition\\b")

def find_full_abbrs(defdict, root):
    ret={}
    for name in defdict:
        id=defdict[name]
        print(f"Iterating through {name}: {id}")
    return ret

def has_class(attrib, clazz):
    """
    :returns True if is in the class
    """
    if "class" not in attrib:
        return False
    regex=re.compile("\\b"+clazz+"\\b")
    matches=regex.search(attrib["class"])
    return matches is not None
    
def find_definitions(root, defdict):
    if has_class(root.attrib, "definition"):
        defdict[root.text]=root.attrib["id"]
        if "data-others" in root.attrib:
            for altval in root.attrib["data-others"].split(","):
                defdict[altval]=root.attrib["id"]

        
    for child in root:
        find_definitions(child, defdict)
    
