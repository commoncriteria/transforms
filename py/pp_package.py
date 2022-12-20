import generic_pp_doc
import pp_util
import edoc
from generic_pp_doc import NS
HTM=pp_util.get_HTM_E()
adopt=pp_util.adopt

class pp_package(generic_pp_doc.generic_pp_doc):
    def __init__(self, root, workdir, boilerplate):
        super().__init__(root, workdir, boilerplate)


    def apply_template_to_element(self, node, parent):
        if node.tag == generic_pp_doc.CC+"Package":
            return self.template_package(node, parent)
        elif node.tag == generic_pp_doc.CC+"componentsneeded":
            self.template_componentsneeded(node, parent)
        else:
            return super().apply_template_to_element(node, parent)


    def template_componentsneeded(self, node, outnode):
        table = adopt(outnode, HTM.table(HTM.tr({"class":"header"},\
                                                HTM.th("Component"), HTM.th("Explanation"))))
        
        
    def template_package(self, node, parent):
        self.apply_templates(self.rx("//*[@title='Introduction']|sec:Introduction"),parent)
        self.apply_templates(self.rx("//*[@title='Conformance Claims']|sec:Conformance_Claims"),parent)
        self.apply_templates(self.rx("//*[@title='Security Functional Requirements']|sec:Security_Functional_Requirements"),parent)
        # self.consistency_rationale(parent)
        self.start_appendixes()
        self.handle_optional_requirements(parent)
        self.handle_selection_based_requirements(node, parent)
        # self.handle_ext_comp_defs(parent)
        self.apply_templates(self.rfa("//cc:appendix"), parent)
        self.create_acronym_listing(parent)
        self.create_bibliography(parent)

    def doctype(self):
        return "Functional Package"

    def doctype_short(self):
        return "FP"
