import lxml.etree as ET
import pp_util
from pp_util import NS

from lxml.builder import ElementMaker

NS = {'cc': "https://niap-ccevs.org/cc/v1",
      'sec': "https://niap-ccevs.org/cc/v1/section",
      'htm': "http://www.w3.org/1999/xhtml"}
CC="{"+NS['cc']+"}"
SEC="{"+NS['sec']+"}"

HTM_E=pp_util.get_HTM_E()
adopt=pp_util.adopt
append_text=pp_util.append_text

class Edoc:
    """
    Represents external documents. Both those defined by XML and those 
    defined just with the tag.
    """

    
    def __init__(self, node, workdir):
        """
        Constructor

        :param node: Either a cc:base-pp or cc:include-pkg element.
        :param workdir: The directory where the document can be found
        """
        self.orig = node
        if self.orig.tag==CC+"base-pp":
            self.doctype = "Protection Profile"
        else:
            self.doctype = "PP Package"
        self.root = None
        # Should this be a dictionary?
        self.decl_modsfrs={}
        self.el_with_meta = node
        if node.find("cc:git", NS) is not None:
            self.root =ET.parse(workdir+"/"+node.attrib["id"]+".xml").getroot()            
            self.el_with_meta=self.root
        else:
            for modsfrs_el in  node.findall(".//mod-sfrs", NS):
                for decl_modsfr in modsfrs_el.text.split(" "):
                    self.decl_modsfrs[decl_modsfr]=1
        self.mod_sfrs=[]
        self.add_sfrs=[]
        self.are_sfrs_sorted = False

    def get_orig_node(self):
        """
        Retrieves the original node that references this edoc.

        :returns A cc:base-pp or cc:include-pkg element.
        """
        return self.orig
        
    def get_product(self):
        """ 
        Get's the product (singular) represented by this edoc.
        
        :returns A string
        """
        return derive_product(self.el_with_meta)
    
    def get_products(self):
        """
        Get's the product class represented by this edoc.

        :returns A string
        """
        return derive_products(self.el_with_meta)

    
    def add_base_dependent_sfr(self,bsfr):
        """
        Associates an SFR with this base.

        :param bsfr: A cc:f-component element
        """
        if self.is_modified(bsfr, self.root):
            self.mod_sfrs.append(bsfr)
        else:
            self.add_sfrs.append(bsfr)
        
    def sort_sfrs(self):
        """
        Sorts the SFRs that are associated with this edoc.
        """
        self.mod_sfrs.sort(key=lambda x: x.attrib["cc-id"])
        self.add_sfrs.sort(key=lambda x: x.attrib["cc-id"])

    def short(self):
        """
        Gets the short name of this edoc.

        :return A short string that references this document.
        """
        return derive_short(self.el_with_meta)

    def get_title(self):
        """
        Gets the  formal name of this edoc.

        :return A string with the title of this document
        """
        
        ret=""
        if self.el_with_meta.find("cc:cPP", NS) is not None:
            ret="Collaborative "
        ret+= derive_title(self.el_with_meta, self.doctype)
        return ret 


    def make_xref_edoc(self, out):
        """
        Makes an anchored reference,with short name, to this document.

        :param out: The HTML output node.
        """
        url=self.orig.find("cc:url", NS).text
        out.append(HTM_E.a({"href":url}, self.short()))

    def make_xref_selectable(self, sel, out):
        """
        Makes a reference to a selectable in this document.

        :param
        """
        ancestor = pp_util.get_meaningful_ancestor(self.root, sel.attrib["id"])
    
        readable = sel.find("cc:readable", NS)
        snip = sel.find("cc:snip", NS)
        if readable is not None:
            pp_util.append_text(out, readable.text)
        elif snip is not None:
            pp_util.append_text(out, snip.text + "...")
        else:
            pp_util.append_text(out, sel.text)
        pp_util.append_text(out, " from ") 
        self.make_xref_sub("", out, target_el=ancestor)

        
            
    def make_xref_sub(self, target_id, out, target_el=None):
        if target_el == None:
            target_el = self.root.find(".//cc:*[@id='"+target_id+"']", NS)
        if target_el is None:
            print("Could not find: " + target_id  + " from " + self.root.tag)
            
        if target_el.tag == CC+"selectable":
            self.make_xref_selectable(target_el, out)
        elif target_el.tag == CC+"f-element":
            fcomp = target_el.xpath("ancestor::*[1]")[0]
            index= fcomp.xpath("cc:f-element", namespaces=NS).index(target_el)
            pp_util.append_text(out, fcomp.attrib["cc-id"].upper()+"."+str(index+1))
            if "iteration" in fcomp.attrib:
                pp_util.append_text(out, "/"+fcomp.attrib["iteration"])
            print("Fcomp: " + fcomp.tag)
        #     raise Exception("Not supported yet")
        # elif target_el.tag == CC+"management-function":
        #     raise Exception("Not supported yet")
        #     # self.make_xref_mf(target_el, out)
        # elif target_el.tag == CC+"f-component":
        #     raise Exception("Not supported yet")
        else:
            raise Exception("Not supported yet: "+target_el.tag)
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
    biggest="-1"
    date=""
    for entry in node.findall("cc:RevisionHistory/cc:entry",NS):
        ver = entry.find("cc:version", NS)
        if is_newer(ver.text, biggest):
            date=entry.find("cc:date",NS).text
            biggest=ver.text
    ret=[]
    ret.append(biggest)
    ret.append(date)
    return ret

def is_newer(ver1, ver2):
# Returns True if ver1 is newer than ver2
    if ver2 == "":
        return False
    ver1_nums = ver1.split(".")
    ver2_nums = ver2.split(".")
    ctr=0
    for ver2_num_str in ver2_nums:
        if not ctr<len(ver1_nums):            # If ver1 runs out of numbers
            return False
        
        ver1_num = int(ver1_nums[ctr])
        ver2_num = int(ver2_num_str)
        if ver1_num < ver2_num:
            return False
        if ver1_num > ver2_num:
            return True
        ctr=ctr+1
    return False
        
        
        

def is_cpp(node):
    return node.find("cc:cPP", NS) is not None

def derive_title(node, doctype):
    title = node.find("cc:title", NS)
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
