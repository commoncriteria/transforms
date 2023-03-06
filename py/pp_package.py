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
            return self.template_package(parent)
        elif node.tag == generic_pp_doc.CC+"componentsneeded":
            self.template_componentsneeded(node, parent)
        else:
            return super().apply_template_to_element(node, parent)


    def template_componentsneeded(self, node, outnode):
        table = adopt(outnode, HTM.table(HTM.tr({"class":"header"},\
                                                HTM.th("Component"), HTM.th("Explanation"))))
        for comp in node.findall("cc:componentneeded", NS):
            id = comp.find("cc:componentid",NS).text
            tr = adopt(table, HTM.tr(HTM.td({"class":"componentneeded", "id":id},id)))
            td = adopt(tr, HTM.td())
            self.handle_content(comp.find("cc:notes", NS), td)

        
    def template_package(self, parent):
        self.apply_templates(self.rx("//*[@title='Introduction']|sec:Introduction"),parent)
        self.apply_templates(self.rx("//*[@title='Conformance Claims']|sec:Conformance_Claims"),parent)
        self.handle_requirements(parent)
        self.start_appendixes()
        self.handle_optional_requirements(parent)
        self.handle_selection_based_requirements(parent)
        # self.handle_ext_comp_defs(parent)
        self.apply_templates(self.rfa("//cc:appendix"), parent)
        self.create_acronym_listing(parent)
        self.create_bibliography(parent)

        
    # def handle_base_section_hook(self, title, node, parent):
    #     if title=="Security Functional Requirements":
    # 
    #     else:
    #         return super().handle_post_section_hook(title,node, parent)

    def handle_requirements(self, out):
        out.append(self.sec("Security Functional Requirements"))
        out.append(generic_pp_doc.get_convention_explainer())
        # I only expect one, but it's easier to deal with the set
        sfr_nodes = self.rfa("//sec:Security_Functional_Requirements")+self.rfa("//cc:section[@title='Security Functional Requirements']")
        noreqsecs=[]
        for aa in sfr_nodes:
            noreqsecs+=aa.xpath("*[not(cc:f-component)]", namespaces=NS)
        self.apply_templates(noreqsecs, out)
        self.handle_sparse_sfrs(self.man_sfrs, out, "man_sfrs")
        
#         out.append(self.sec("Auditable Events for Mandatory SFRs"))
#         out.append(HTM.p(\
# """The auditable events specified in this Package are included in a Security Target 
# if the incorporating PP, cPP, or PP-Module supports audit event reporting through FAU_GEN.1
# and all other criteria in the incorporating PP or PP-Module are met."""))
        # 	</h:p>
        # 	<audit-table id="at-man-audit" table="mandatory">
        # 		<h:div class="table-caption"><ctr ctr-type="Table" id="atref-mandatory">: Auditable Events for Mandatory SFRs</ctr></h:div>
        # 	</audit-table>
        # </sec:ss-audit-table>
        # self.end_section()
        self.end_section()


        
    def doctype(self):
        return "Functional Package"

    def doctype_short(self):
        return "FP"
