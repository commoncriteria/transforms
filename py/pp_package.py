import generic_pp_doc
import pp_util
import edoc
from generic_pp_doc import NS
HTM_E=pp_util.get_HTM_E()
adopt=pp_util.adopt

class pp_package(generic_pp_doc.generic_pp_doc):
    def __init__(self, root, workdir, boilerplate):
        super().__init__(root, workdir, boilerplate)


    def apply_template_to_element(self, node, parent):
        if node.tag == generic_pp_doc.CC+"Package":
            return self.template_package(node, parent)
        else:
            return super().apply_template_to_element(node, parent)
        
    def template_package(self, node, parent):
        pass

    def doctype(self):
        return "Functional Package"

    def doctype_short(self):
        return "FP"
