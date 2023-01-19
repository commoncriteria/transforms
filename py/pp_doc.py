import generic_pp_doc
import pp_util
import edoc
from generic_pp_doc import NS
HTM_E=pp_util.get_HTM_E()

adopt=pp_util.adopt

SR_TITLE="Security Requirements"
SFR_TITLE="Security Functional Requirements"
SAR_TITLE="Security Assurance Requirements"
class pp_doc(generic_pp_doc.generic_pp_doc):
    def __init__(self, root, workdir, boilerplate):
        super().__init__(root, workdir, boilerplate)
        self.modules={}
        for mod_node in self.rfa("//cc:module"):
            self.modules[mod_node.attrib["id"]]=edoc.Edoc(mod_node, workdir)

    def apply_template_to_element(self, node, parent):
        if node.tag == "{https://niap-ccevs.org/cc/v1}PP":
            return self.template_pp(node, parent)
        else:
            return super().apply_template_to_element(node, parent)


    def consistency_rationale(self, par):
        par.append(self.sec({"id":"mod-conrat"},"Consistency Rationale"))
        self.end_section()

 
    def handle_security_requirements(self, par):
        firstfcomp=self.rf("//cc:f-component")
        sr_sec = firstfcomp.xpath("ancestor::*[3]")[0]
        attrs={"id":self.derive_id(sr_sec)}
        title=self.get_section_title(sr_sec)
        adopt(par, self.sec(title, attrs))
        div = generic_pp_doc.get_convention_explainer()
        div.text= "This chapter describes the security requirements which have to be fulfilled by the product under evaluation."+\
            "Those requirements comprise functional components from Part 2 and assurance components from Part 3 of [CC]."+div.text
        par.append(div)
        sfr_sec = firstfcomp.xpath("ancestor::*[2]")[0]
        attrs={"id":self.derive_id(sfr_sec)}
        title=self.get_section_title(sfr_sec)
        adopt(par, self.sec(title, attrs))
        secs_no_fcomps = sfr_sec.xpath(".//sec:*[not(.//cc:f-component)]|.//cc:section[not(.//cc:f-component)]", namespaces=NS)
        self.apply_templates(secs_no_fcomps, par)
        self.handle_sparse_sfrs(self.man_sfrs, par)
        self.objectives_to_requirements(par)
        self.end_section()
        self.handle_sars(par)
        self.end_section()
        


    def handle_sars(self, out):
        firstfcomp=self.rf("//cc:f-component")
        sfr_sec = firstfcomp.xpath("ancestor::*[2]")[0]
        sfr_id = self.derive_id(sfr_sec)
        
        first_acomp=self.rf("//cc:a-component")
        sar_sec = first_acomp.xpath("ancestor::*[2]")[0]
        attrs={"id":self.derive_id(sar_sec)}
        title=self.get_section_title(sar_sec)
        adopt(out, self.sec(title,attrs))
        par = adopt(out, HTM_E.p("The Security Objectives for the TOE in "))
        secobjs=self.get_first_section_with_title("Security Objectives")
        self.make_xref(secobjs,par)#Secrtion 4
        self.add_text(par," were constructed to address threats identified in ")
        threatsec=self.get_first_section_with_title("Threats")
        self.make_xref(threatsec,par)#Section 3.1
        self.add_text(par, ". The Security Functional Requirements (SFRs) in ")
        self.make_xref_section(sfr_id, par)#Section 5.1
        self.add_text(par, """ are a formal instantiation of the Security Objectives. The PP identifies the Security Assurance Requirements (SARs) to frame the extent to which the evaluator assesses the documentation applicable for the evaluation and performs independent testing.""")
        par = adopt(out, HTM_E.p("This section lists the set of "+\
                                 "Security Assurance Requirements (SARs) from Part 3 of the Common "+\
                                 "Criteria for Information Technology Security Evaluation, Version 3."+\
                                 "1, Revision 5 that are required in evaluations against this PP. "+\
                                 "Individual evaluation activities to be performed are specified in "+\
                                 "both "))
        self.make_xref_section(sfr_id, par)#Section 5.1
        self.add_text(par,"as well as in this section.")
        par = adopt(out, HTM_E.p("After the ST has been approved for "+\
                                 "evaluation, the Information Technology Security Evaluation "+\
                                 "Facility (ITSEF) will obtain the TOE, supporting environmental IT, "+\
                                 "and the administrative/user guides for the TOE. The ITSEF is "+\
                                 "expected to perform actions mandated by the CEM for the ASE and ALC "+\
                                 "SARs. The ITSEF also performs the evaluation activities contained "+\
                                 "within "))
        self.make_xref_section(sfr_id,par) # Section 5
        self.add_text(par,", which are intended to be an interpretation of the "+\
                      "other CEM assurance requirements as they apply to the specific "+\
                      "technology instantiated in the TOE. The evaluation activities that "+\
                      "are captured in Section 5 also provide clarification as to what the "+\
                      "developer needs to provide to demonstrate the TOE is compliant with "+\
                      "the PP. ")
        sar=self.find_first_section_with_title(SAR_TITLE)
        self.apply_templates(sar.xpath("cc:section[not(.//cc:a-component)]|sec:*[not(.//cc:a-component)]", namespaces=generic_pp_doc.NS), par)
        afrs = self.rx("//cc:a-component")
        self.handle_sparse_sfrs(afrs, par)
        self.end_section()
        
        

        
    def template_pp(self, node, parent):
        first_intro=self.find_first_section_with_title("Introduction")
        self.apply_templates_single(first_intro,parent)
        self.apply_templates(self.find_sections_with_title("Conformance Claims"),parent)
        self.apply_templates(self.find_sections_with_title("Security Problem Description"),parent)
        self.apply_templates(self.find_sections_with_title("Security Objectives"),parent)
        self.handle_security_requirements(parent)
#        self.apply_templates(self.rx("//*[@title='Security Requirements']|sec:Security_Requirements"),parent)
#        self.consistency_rationale(parent)
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

