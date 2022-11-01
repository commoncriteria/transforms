import generic_pp_doc
import pp_util
from generic_pp_doc import NS


class ppmod(generic_pp_doc.generic_pp_doc):
    def __init__(self, root, workdir, output, boilerplate):
        super().__init__(root, workdir, output, boilerplate)

    def handle_unknown_depends(self, sfr, attrval):
        if self.rf("//cc:base-pp[@id='"+attrval+"']") is not None:
            # This seems to be handled already in the Edoc initialization
            base = self.edocs[attrval]
            base.add_base_dependent_sfr(sfr)
        else:
            raise Exception("Dont know how to handle: "+ sfr["cc-id"])


        
    def title(self):
        node = self.rf("//cc:PPTitle")
        if node is not None:
            return node.text
        if "target-products" in self.root.attrib:
            return "PP-Module for " + self.root.attrib["target-products"]
        else:
            return "PP-Module for " + self.root.attrib["target-product"] + "s"

    def requirement_consistency_rationale_section(self, reqs, nonmsg, edoc=None):
        if len(reqs)==0:
            self.ol("<tr><td colspan=\"2\" style=\"text-align:center\">")
            self.ol(nonmsg)
            self.ol("</td></tr>")
            return
        for req in reqs:
            self.ol("<tr>")
            self.o("<td>"+self.fcomp_cc_id(req)+"</td>")
            self.o("<td>")
            id=pp_util.get_attr_or(req, "id")
            conmods=[]
            if edoc is not None:
                conmods = edoc.node.xpath("cc:con-mod[@ref='"+id+"']", namespaces=NS)
            for conmod in conmods:
                self.handle_content(conmod)
            if len(conmods)==0:
                self.handle_content(req.find("cc:consistency-rationale", generic_pp_doc.NS))
            self.ol("</td></tr>")

    
    def template_sfrs(self, node):
        self.ol("<h2 class=\"indexable\" data-level=\"2\">Security Functional Requirements</h2>")
        self.ol("The Security Functional Requirements included in this section")
        self.ol("are derived from Part 2 of the Common Criteria for Information")
        self.o("Technology Security Evaluation, ")
        self.o(pp_util.ccver())
        self.ol(", with additional extended functional components.")
        # self.handle_content(node)
        bases = self.rfa("//cc:base-pp")
        base_fcomps = []
        for base in bases:
            base_fcomps = base_fcomps + self.handle_basepp(base)

        self.ol("<h2 id=\"man-sfrs\" class=\"indexable\" data-level=\"2\">TOE Security Functional Requirements</h2>")




        if len(self.man_sfrs)>0:
            self.ol("The following section describes the SFRs that must be satisfied by any TOE that claims conformance to this PP-Module.")
            self.ol("These SFRs must be claimed regardless of which PP-Configuration is used to define the TOE.")
            self.handle_sparse_sfrs(self.man_sfrs)
        else:
            self.ol("This PP-Module does not define any mandatory SFRs.")

            
    def apply_template_to_element(self, node):
        if node.tag == "{https://niap-ccevs.org/cc/v1}Module":
            self.template_module(node)
            return True
        else:
            return super().apply_template_to_element(node)


    def ppdoctype_short(self):
        return "PP-Module"




    def is_base(self, attr):
        b_el = self.rf("//cc:base-pp[@id='"+attr+"']")
        return b_el is not None


    def doc_specific_templates(self, node):
        if node.tag=="{https://niap-ccevs.org/cc/v1}base-pp":
            return True
        else:
            return False

        
    def handle_basepp(self, node):
        id = node.attrib["id"]
        base=self.edocs[id]
        short=base.short
        self.ol("<h2 id=\""+"secreq-"+id+"\" class=\"indexable\" data-level=\"2\">")
        self.o(short)
        self.ol(" Security Functional Requirements Direction")
        self.ol("</h2>")
        if not self.apply_templates_single(node.find("cc:sec-func-req-dir", generic_pp_doc.NS)):
            self.ol("In a PP-Configuration that includes the ")
            self.o(short)
            self.ol(",the TOE is expected to rely on some of the security functions implemented by the")
            self.ol(base.product)
            self.ol("as a whole and evaluated against the  " + short + ".")
            self.ol("The following sections describe any modifications that the ST author must make to the SFRs")
            self.ol("defined in the "+short+ "in addition to what is mandated by <a class=\"dynref\" href=\"#man-sfrs\">Section </a>.")
        self.ol("<h3 id=\"modsfr-"+id+"\" class=\"indexable\" data-level=\"3\"> Modified SFRs </h3>")
        self.ol("The SFRs listed in this section are defined in the "+short+
                " and relevant to the secure operation of the TOE.")
        if len(base.mod_sfrs)==0:
            self.ol("This PP-Module does not modify any SFRs defined by the " + short  + ".")
        else:
            self.handle_sparse_sfrs(base.mod_sfrs)
                
        if len(self.rfa("//cc:base-pp"))>1:
            self.ol("<h3 id=\"addsfr-"+id+"\" class=\"indexable\" data-level=\"3\"> Additional SFRs</h3>")
            if len(base.add_sfrs)>0:
                self.ol("This section defines additional SFRs that must be added to the TOE boundary in order to implement the functionality in any PP-Configuration where the "+short+" is claimed as the Base-PP.")
                self.handle_sparse_sfrs(base.add_sfrs)
            else:
                self.ol("This PP-Module does not define any additional SFRs for any PP-Configuration where the "+short+" is claimed as the Base-PP.")
        return base.add_sfrs + base.mod_sfrs
    
    def handle_conformance_claims(self, node):
        self.o("""
    <dl>
        <dt>Conformance Statement</dt>
        <dd>
          <p>This PP-Module inherits exact conformance as required from the specified
          Base-PP and as defined in the CC and CEM addenda for Exact Conformance, Selection-based
          SFRs, and Optional SFRs (dated May 2017).</p>
          <p>The following PPs and PP-Modules are allowed to be specified in a 
            PP-Configuration with this PP-Module. </p> <ul>
""")
        bases = self.rfa("//cc:base-pp")
        for base in bases:
            self.o("<li>")
            self.make_xref(base)
            self.ol("</li>")
        self.ol("</ul>\n")
        self.ol("</dd>")
        self.ol("<dt>CC Conformance Claims</dt>")
        self.ol("<dd>This PP-Module is conformant to Parts 2 (extended) and 3 (conformant) of Common Criteria "+pp_util.ccver()+".</dd>")
        self.ol("<dt>PP Claim </dt>")
        self.ol("<dd>This PP-Module does not claim conformance to any Protection Profile. </dd>")
        self.ol("<dt>Package Claim</dt>")
        self.ol("<dd>This PP-Module")
        pks = self.rfa("//cc:include-pkg")
        ctr=len(pks)
        if ctr == 0:
            self.o("does not claim conformance to any packages")
        else:
            lagsep=""
            for pk in pks:
                ctr=ctr-1
                self.o(lagsep)
                lagsep=","
                if ctr==2 :
                    lagsep="and"
                self.make_xref_edoc(pk)
            self.o("conformant")
        self.ol(".</dd>")
        self.ol("</dl>")


  # <xsl:template match="cc:*[@id='obj_map']" mode="hook" name="obj-req-map">
    def objectives_to_requirements(self):
        addr_bys = self.rx("//cc:SO/cc:addressed-by")
        if len(addr_bys)==0:
            return
        self.ol("<h2 id=\"obj-req-map-\" class=\"indexable\" data-level=\"2\">TOE Security Functional Requirements Rationale</h2>")
        self.o("""<p>The following rationale provides justification for each 
 security objective for the TOE, showing that the SFRs are suitable to meet and
 achieve the security objectives:</p>
  <table>
        <caption>""")
        self.create_ctr("Table", "t-obj-map")
        self.ol(": SFR Rationale</caption>")
        self.ol("<tr><th>Objective</th><th>Addressed by</th><th>Rationale</th></tr>")
        prev_parent = None
        for addr_by in addr_bys:
            self.o("<tr")
            curr_parent=addr_by.find("..")
            if prev_parent!=curr_parent:
                self.ol(" class=\"major-row\">")
                self.o("<td rowspan=\"")
                self.o(str(len(curr_parent.findall("cc:addressed-by", generic_pp_doc.NS))))
                self.o("\">")
                self.o(pp_util.make_wrappable(curr_parent.attrib["name"]))
                self.o("</td")
                prev_parent=curr_parent
            self.ol("><td>")
            self.handle_content(addr_by)
            self.o("</td><td>")
            rational=addr_by.xpath("following-sibling::cc:rationale[1]",namespaces=generic_pp_doc.NS)
            self.handle_content(rational[0])
            self.ol("</td></tr>")
        self.ol("</table>")

    def handle_consistency_row(self, base, thing):
        name=thing.attrib["name"]
        self.ol("<tr>")
        self.ol("  <td>"+name+"</td>")
        self.ol("  <td>")
        mod=base.find("cc:con-mod[@ref='"+name+"']", generic_pp_doc.NS)
        if mod is None:
            mod=thing.find("cc:consistency-rationale",generic_pp_doc.NS)
        self.handle_content(mod)
        self.ol("  </td>")
        self.ol("</tr>")

    def handle_consistency_rows(self, base, rows):
        for row in rows:
            self.handle_consistency_row(base, row)
            
    def consistency_rationale(self):
        self.ol("<h1 id=\"mod-conrat\" class=\"indexable\" data-level=\"1\">Consistency Rationale</h1>")
        bases = self.rfa("//cc:base-pp")
        for base in bases:
            id   = base.attrib["id"]
            edoc = self.edocs[id]
            self.set_underscore(edoc.short)
            self.o("<h2 id=\"conrat-"+id+"\" class=\"indexable\" data-level=\"2\">")
            self.o(edoc.short)
            self.ol("</h2>")
            self.ol("    <h3 id=\"contoe-"+id+"-\" class=\"indexable\" data-level=\"3\">")
            self.ol("Consistency of TOE Type")
            self.ol("</h3>")
            self.handle_content(base.find("cc:con-toe",generic_pp_doc.NS))
            self.ol("    <h3 id=\"consecprob-"+id+"-\" class=\"indexable\" data-level=\"3\">")
            self.ol("Consistency of Security Problem Definition")
            self.ol("</h3>")
            self.handle_content(base.find("cc:con-sec-prob",generic_pp_doc.NS))
            self.ol("<table><tr><th>PP-Module Threat, Assumption, OSP</th><th>Consistency Rationale</th></tr>")
            things = self.rx("//cc:threat[cc:description]|//cc:assumption[cc:description]|//cc:OSP[cc:description]")
            self.handle_consistency_rows(base, things)
            self.ol("</table>")

            self.ol("<h3 id=\"conobj-"+id+"\" class=\"indexable\" data-level=\"3\">")
            self.ol("Consistency of Objectives")
            self.ol("</h3>")
            self.ol("<p>")
            self.handle_content(base.find("./cc:con-obj",generic_pp_doc.NS))
            sos_des = self.rfa("//cc:SO[cc:description]")
            self.ol("</p>")
            if len(sos_des):
                self.ol("The objectives for the TOEs are consistent with the ")
                self.o(edoc.make_xref_edoc())
                self.ol(" based on the following rationale:")
                self.ol("<table><tr><th>PP-Module TOE Objective</th><th>Consistency Rationale</th></tr>")
                self.handle_consistency_rows(base, sos_des)
                self.ol("</table>")
            self.handle_content(base.find("./cc:con-op-en", generic_pp_doc.NS))
            soes = self.rfa("//cc:SOE")
            if len(soes)>0:
                self.ol("<p>The objectives for the TOE's OE are consistent with the ")
                self.o(edoc.make_xref_edoc())
                self.ol("based on the following rationale:</p>")
                self.ol("<table><tr><th>PP-Module OE Objective</th><th>Consistency Rationale</th></tr>")
                self.handle_consistency_rows(base,soes)
                self.ol("</table>")
            self.ol("<h3 id=\"conreq-"+id+"\" class=\"indexable\" data-level=\"3\">")
            self.ol("Consistency of Requirements")
            self.ol("</h3>")
            self.handle_content(base.find("./cc:con-req", generic_pp_doc.NS))
            self.ol("This PP-Module identifies several SFRs from the")
            self.o(edoc.make_xref_edoc())
            self.o(" that are needed to support ")
            self.o(self.root.attrib["target-product"])
            self.ol(" functionality.")
            self.ol("This is considered to be consistent because the functionality provided by the")
            self.o(edoc.make_xref_edoc())
            self.ol(" is being used for its intended purpose.")
            if len(edoc.mod_sfrs)>0:
                self.ol("The PP-Module also identifies a number of modified SFRs from the")
                self.o(edoc.make_xref_edoc())
                if len(edoc.add_sfrs)>0:
                    self.ol("as well as new SFRs ")
                self.ol("that are used entirely to provide functionality for")
                self.ol(edoc.get_products()+".")
            elif len(edoc.add_sfrs)>0:
                self.ol("The PP-Module identifies new SFRs that are used entirely to provide")
                self.ol("functionality for")
                self.ol(edoc.get_products()+".")
            self.ol("The rationale for why this does not conflict with the claims")
            self.o("defined by the")
            self.ol(edoc.short+" are as follows:")
            self.ol("<table>")
            self.ol("<tr><th>PP-Module Requirement</th><th>Consistency Rationale</th></tr>")
            self.ol("<tr><th colspan=\"2\"> Modified SFRs</th></tr>")
            self.requirement_consistency_rationale_section(edoc.mod_sfrs, 
               "This PP-Module does not modify any requirements when the "+\
                                                           edoc.short + " is the base.",edoc=edoc)

            self.ol("<tr><th colspan=\"2\"> Additional SFRs</th></tr>")
            self.requirement_consistency_rationale_section(edoc.add_sfrs, 
               "This PP-Module does not levy any addition requirements when the "+\
                                                           edoc.short + " is the base.",edoc=edoc)
            self.ol("<tr><th colspan=\"2\"> Mandatory SFRs</th></tr>")
            self.requirement_consistency_rationale_section(self.man_sfrs, 
                                                           "This PP-Module does not define any Mandatory requirements.")


            self.ol("<tr><th colspan=\"2\">Optional SFRs</th></tr>")
            self.requirement_consistency_rationale_section(self.opt_sfrs, 
                                                           "This PP-Module does not define any Strictly Optional requirements.")
            self.ol("<tr><th colspan=\"2\">Objective SFRs</th></tr>")
            self.requirement_consistency_rationale_section(self.obj_sfrs, 
                                                           "This PP-Module does not define any Objective requirements.")
            self.ol("<tr><th colspan=\"2\">Implementation-based SFRs</th></tr>")
            self.requirement_consistency_rationale_section(self.impl_sfrs, 
                                                           "This PP-Module does not define any Implementation-based requirements.")
            self.ol("<tr><th colspan=\"2\">Selection-based SFRs</th></tr>")
            self.requirement_consistency_rationale_section(self.sel_sfrs, 
                                                           "This PP-Module does not define any Selection-based requirements.")
            self.ol("</table>")


        
    def template_module(self, node):
        self.apply_templates(self.rx("//*[@title='Introduction']|sec:Introduction"))
        self.apply_templates(self.rx("//*[@title='Conformance Claims']|sec:Conformance_Claims"))
        self.apply_templates(self.rx("//*[@title='Security Problem Description']|sec:Security_Problem_Description"))
        self.apply_templates(self.rx("//*[@title='Security Objectives']|sec:Security_Objectives"))
        self.apply_templates(self.rx("//*[@title='Security Requirements']|sec:Security_Requirements"))
        self.objectives_to_requirements()
        self.consistency_rationale()
        # <xsl:call-template name="opt-sfrs"/>
        # <xsl:call-template name="sel-sfrs"/>
        # <xsl:call-template name="ext-comp-defs"/>
        self.apply_templates(self.rfa("//cc:appendix"))
        self.create_acronym_listing()
        self.create_bibliography()

    
        
    def handle_section_hook_base(self, title, node):
        if title=="Security Functional Requirements":
            template_sfrs(self,node)
        else:
            super().handle_section_hook_base(title,node)

            
            
