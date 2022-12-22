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
        adopt(par, self.sec("Security Requirements"))
        
        div = generic_pp_doc.get_convention_explainer()
        div.text= "This chapter describes the security requirements which have to be fulfilled by the product under evaluation."+\
            "Those requirements comprise functional components from Part 2 and assurance components from Part 3 of [CC]."+div.text
        par.append(div)
        adopt(par, self.sec("Security Functional Requirements"))
        self.create_audit_table_section("Mandatory", "mandatory", par)
        self.handle_sparse_sfrs(self.man_sfrs, par)
        self.objectives_to_requirements(par)
        self.end_section()
        adopt(par, self.sec("Security Assurance Requirements"))

        self.add_text(par, "The Security Objectives for the TOE in ")
        secobjs=self.get_first_section_with_title("Security Objectives")
        self.make_xref(secobjs,par)#Secrtion 4
        self.add_text(par," were constructed to address threats identified in ")
        threatsec=self.get_first_section_with_title("Threats")
        self.make_xref(threatsec,par)#Section 3.1
        self.add_text(par, ". The Security Functional Requirements (SFRs) in ")
        self.make_xref_section("sfrs_", par)#Section 5.1
        self.add_text(par, """ are a formal instantiation of the Security Objectives. The PP identifies the Security Assurance Requirements (SARs) to frame the extent to which the evaluator assesses the documentation applicable for the evaluation and performs independent testing.

 This section lists the set of Security Assurance Requirements (SARs) from Part 3 of the Common Criteria for Information Technology Security Evaluation, Version 3.1, Revision 5 that are required in evaluations against this PP. Individual evaluation activities to be performed are specified in both Section 5.1 as well as in this section.

 After the ST has been approved for evaluation, the Information Technology Security Evaluation Facility (ITSEF) will obtain the TOE, supporting environmental IT, and the administrative/user guides for the TOE. The ITSEF is expected to perform actions mandated by the CEM for the ASE and ALC SARs. The ITSEF also performs the evaluation activities contained within Section 5, which are intended to be an interpretation of the other CEM assurance requirements as they apply to the specific technology instantiated in the TOE. The evaluation activities that are captured in Section 5 also provide clarification as to what the developer needs to provide to demonstrate the TOE is compliant with the PP. 
 """)
        self.end_section()
        self.end_section()
        



        
    def template_pp(self, node, parent):
        first_intro=self.rx("//*[@title='Introduction']|sec:Introduction")[0]
        self.apply_templates_single(first_intro,parent)
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

