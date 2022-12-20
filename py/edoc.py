import lxml.etree as ET
import pp_util
from pp_util import NS

from lxml.builder import ElementMaker
HTM_E=pp_util.get_HTM_E()

adopt=pp_util.adopt
append_text=pp_util.append_text
# Represents external documents. Both those defined by XML and those defined just with the
# tag
class Edoc:
#            basedep_sfrs = self.rx("//cc:f-component[cc:depends/@*='"+id+"']")

    def __init__(self, node, workdir):
        self.orig = node
        self.root = None
        # Should this be a dictionary?
        self.decl_modsfrs={}
        nodewithinfo=node
        if node.find("cc:git", NS) is not None:
            self.root =ET.parse(workdir+"/"+node.attrib["id"]+".xml").getroot()            
            nodewithinfo=self.root
        else:
            for modsfrs_el in  node.findall(".//mod-sfrs", NS):
                for decl_modsfr in modsfrs_el.text.split(" "):
                    self.decl_modsfrs[decl_modsfr]=1
        print("Nodewithinfo is " + str(nodewithinfo))
        # self.short = Edoc.get_short(nodewithinfo)
        # self.product = derive_product(nodewithinfo)
        # self.products = derive_products(nodewithinfo)
        self.mod_sfrs=[]
        self.add_sfrs=[]
        self.are_sfrs_sorted = False

    def get_orig_node(self):
        return self.orig
        
    def get_product(self):
        if root is not None:
            return derive_product(root)
        else:
            return derive_product(orig)
    
    def get_products(self):
        if root is not None:
            return derive_products(root)
        else:
            return derive_products(orig)

        
    def add_base_dependent_sfr(self,bsfr):
        if self.is_modified(bsfr, self.root):
            self.mod_sfrs.append(bsfr)
        else:
            self.add_sfrs.append(bsfr)
        
    def sort_sfrs(self):
        self.mod_sfrs.sort(key=lambda x: x.attrib["cc-id"])
        self.add_sfrs.sort(key=lambda x: x.attrib["cc-id"])

    def make_xref_edoc(self, parent):
        url=self.orig.find("cc:url", NS).text
        print("Orig is :"+self.orig.attrib["id"])
        if self.root is None:
            parent.append(HTM_E.a({"href":url}, derive_short(self.orig)))
        else:
            parent.append(HTM_E.a({"href":url}, derive_short(self.root)))

        # if root
        # print("Node tag: " + node.tag)
        # if "name" in self.orig.attrib:
        #     ret =self.orig.attrib["name"]
        #     ret+=", version"
        #     ret+=self.orig.attrib["version"]
        # else:
        #     modrot = self.root.find(".//cc:Module", NS)
        #     if modrot is not None:
        #         name = modrot.attrib["name"]
        #         if not name.startswith("PP-Module for"):
        #             name = "PP-Module for " + name
        #     else:
        #         modrot = self.root.find(".//cc:PPTitle", NS)
        #         if modrot is not None:
        #             name = modrot.text
        #         else:
        #             raise Exception("Somethign else " + str(node)   )
        #     ret=name+", version "+self.root.find(".//cc:PPVersion", NS).text
        # node.text = ret
        # parent.append(node)
        
    def is_modified(self, sfr, broot):
        cc_id = sfr.attrib["cc-id"]
        xp_iter=""
        if "iteration" in sfr.attrib:
            iteration=sfr.attrib["iteration"]
            if (cc_id+"/"+iteration) in self.decl_modsfrs:
                return True
            xp_iter = " and @iteration='"+iteration+"'"
        else:
            if cc_id in self.decl_modsfrs:
                return True
        if broot is not None:
            xpath = "//cc:f-component[@cc-id='"+cc_id+"'"+xp_iter + "]"
            orig = broot.xpath(xpath, namespaces=NS)
            ret = len(orig) > 0
            return ret
        return False

def derive_product(node):
    print("Tag: " + node.tag)
    return node.find("cc:product_class", NS).text

    
def derive_products(node):
    plural=node.find("cc:plural", NS)
    if plural is not None:
        return plural.text
    return derive_product(node)+"s"

def derive_version_and_date(node):
    ver=node.find("cc:version", NS)
    if ver is not None:
        return [ver.text]
    biggest=0.0
    date=""
    for entry in node.findall("cc:RevisionHistory/cc:entry",NS):
        ver = entry.find("cc:version", NS)
        try:
            ver_float = float(ver.text)
            if biggest<ver_float:
                date=entry.find("cc:date",NS).text
                biggest=ver_float
        except ValueError:
            return [ver.text, entry.find("cc:date",NS).text]
    print("Returning: ")
    print("Biggest:"+str(biggest))
    print("Date: " + date)
    ret=[]
    ret.append(str(biggest))
    ret.append(date)
    return ret

def is_cpp(node):
    return node.find("cc:cPP", NS) is not None

def derive_title(node, doctype):
    title = node.find("cc:title", NS)
    print("Namespace is " + str(NS))
    print("Node is "+ node.tag + " " + node[0].tag)
    if title is not None:
        return title.text
    return doctype + " for " + derive_products(node) 

def derive_short(node):
    short = node.find("cc:short", NS)
    if short is not None:
        return short.text
    name = derive_products(node)
    sep = " "
    if is_cpp(node):
        sep="c"
    return name+sep+"PP"
