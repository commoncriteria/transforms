import lxml.etree as ET
import pp_util
from pp_util import NS

# Represents external documents. Both those defined by XML and those defined just with the
# tag
class Edoc:
#            basedep_sfrs = self.rx("//cc:f-component[cc:depends/@*='"+id+"']")

    def __init__(self, node, workdir):
        self.node = node
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
        self.short = Edoc.get_short(nodewithinfo)
        self.product = Edoc.derive_product(nodewithinfo)
        self.products = Edoc.derive_products(nodewithinfo)
        self.mod_sfrs=[]
        self.add_sfrs=[]
        self.are_sfrs_sorted = False

    def get_product(self):
        return self.product
    
    def get_products(self):
        return self.product
        
    def add_base_dependent_sfr(self,bsfr):
        if self.is_modified(bsfr, self.root):
            self.mod_sfrs.append(bsfr)
        else:
            self.add_sfrs.append(bsfr)
        
    def sort_sfrs(self):
        self.mod_sfrs.sort(key=lambda x: x.attrib["cc-id"])
        self.add_sfrs.sort(key=lambda x: x.attrib["cc-id"])

        
        

    def make_xref_edoc(self):
        node=self.node
        ret=""
        url=node.find("cc:url", NS).text
        ret+="<a href=\""+pp_util.make_attr_safe(url)+"\">"
        if "name" in node.attrib:
            ret+=node.attrib["name"]
            ret+=" version "
            ret+=node.attrib["version"]
        else:
            modrot = self.root.find(".//cc:Module", NS)
            if modrot is not None:
                name = modrot.attrib["name"]
                if not name.startswith("PP-Module for"):
                    name = "PP-Module for " + name
            else:
                modrot = self.root.find(".//cc:PPTitle", NS)
                if modrot is not None:
                    name = modrot.text
                else:
                    raise Exception("Somethign else " + str(node)   )
            ret+=name+", version "+self.root.find(".//cc:PPVersion", NS).text
        ret+="</a>"
        return ret
        
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
        return node.attrib["target-product"]
    
    def derive_products(node):
        if "target-products" in node.attrib:
            return node.attrib["target-products"]
        return node.attrib["target-product"]+"s"
        
    def get_short(node):
        if "short" in node.attrib:
            ret = node.attrib["short"]
            if node.find("cc:cPP", NS):
                return ret+"cPP"
            return ret+" PP"
        return node.attrib["target-product"]+" PP"

