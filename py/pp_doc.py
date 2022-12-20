import generic_pp_doc
import pp_util
import edoc
from generic_pp_doc import NS
HTM_E=pp_util.get_HTM_E()

adopt=pp_util.adopt

class pp_doc(generic_pp_doc.generic_pp_doc):
    def __init__(self, root, workdir, boilerplate):
        super().__init__(root, workdir, boilerplate)

    def apply_template_to_element(self, node, parent):
        if node.tag == "{https://niap-ccevs.org/cc/v1}PP":
            return self.template_pp(node, parent)
        else:
            return super().apply_template_to_element(node, parent)


    def consistency_rationale(self, par):
        par.append(self.sec({"id":"mod-conrat"},"Consistency Rationale"))
        self.end_section()


    def handle_security_requirements(self, par):
        sec_sec = adopt(par, self.sec("Security Requirements"))
        sfr_sec = adopt(par, self.sec("Security Functional Requirements"))
        self.handle_sparse_sfrs(self.man_sfrs, par)
        self.end_section()
        sfr_sec = adopt(par, self.sec("Security Assurance Requirements"))
        self.end_section()
        self.end_section()
        
        
    def template_pp(self, node, parent):
        self.apply_templates(self.rx("//*[@title='Introduction']|sec:Introduction"),parent)
        self.apply_templates(self.rx("//*[@title='Conformance Claims']|sec:Conformance_Claims"),parent)
        self.apply_templates(self.rx("//*[@title='Security Problem Description']|sec:Security_Problem_Description"),parent)
        self.apply_templates(self.rx("//*[@title='Security Objectives']|sec:Security_Objectives"),parent)
        self.handle_security_requirements(parent)
#        self.apply_templates(self.rx("//*[@title='Security Requirements']|sec:Security_Requirements"),parent)
        self.consistency_rationale(parent)
        self.start_appendixes()
        self.handle_optional_requirements(parent)
        self.handle_selection_based_requirements(node, parent)
        self.handle_ext_comp_defs(parent)
        self.apply_templates(self.rfa("//cc:appendix"), parent)
        self.create_acronym_listing(parent)
        self.create_bibliography(parent)
    
    def doctype(self):
        return "Protection Profile"

    def doctype_short(self):
        return "PP"

