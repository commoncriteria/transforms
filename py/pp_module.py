import generic_pp_doc

class ppmod(generic_pp_doc.generic_pp_doc):
    def __init__(self, root, workdir, output, boilerplate):
        super().__init__(root, workdir, output, boilerplate)
        
    def title(self):
        node = self.rf("//cc:PPTitle")
        if node is not None:
            return node.text
        if "target-products" in self.root.attrib:
            return "PP-Module for " + self.root.attrib["target-products"]
        else:
            ret = "PP-Module for " +  self.root.attrib["target-product"] + "s"
            return ret

        
