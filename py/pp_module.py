import generic_pp_doc
import pp_util

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
            return "PP-Module for " + self.root.attrib["target-product"] + "s"

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




        man_fcomps = self.rx("//cc:f-component[not(cc:depends)]")
        if len(man_fcomps)>0:
            self.ol("The following section describes the SFRs that must be satisfied by any TOE that claims conformance to this PP-Module.")
            self.ol("These SFRs must be claimed regardless of which PP-Configuration is used to define the TOE.")
            self.handle_sparse_sfrs(man_fcomps)
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


    def get_declared_modified_sfrs(self, base):
        modsfrs =  base.find(".//mod-sfrs")
        if not modsfrs:
            return []
        return modsfrs.text.split(" ")


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
        if id in self.edocs:
            broot = self.edocs[id]
            short = self.get_short(broot)
        else:
            raise Exception("Can't do this basepp")
        self.ol("<h2 id=\""+"secreq-"+id+"\" class=\"indexable\" data-level=\"2\">")
        self.o(short)
        self.ol(" Security Functional Requirements Direction")
        self.ol("</h2>")
        if not self.apply_templates_single(node.find("cc:sec-func-req-dir", generic_pp_doc.NS)):
            self.ol("In a PP-Configuration that includes the ")
            self.o(short)
            self.ol(",the TOE is expected to rely on some of the security functions implemented by the")
            self.get_product(self.root)
            self.ol("as a whole and evaluated against the  " + short + ".")
            self.ol("The following sections describe any modifications that the ST author must make to the SFRs")
            self.ol("defined in the "+short+ "in addition to what is mandated by <a class=\"dynref\" href=\"#man-sfrs\">Section </a>.")


            #     <xsl:variable name="b_id" select="@id"/>
        #     <xsl:variable name="doc" select="concat($work-dir,'/',@id,'.xml')"/>
        

        basedep_sfrs = self.rx("//cc:f-component[cc:depends/@*='"+id+"']")
        declared_modified = self.get_declared_modified_sfrs(node)
        add_sfrs=[]
        mod_sfrs=[]
        for bsfr in basedep_sfrs:
            if self.is_modified(bsfr, declared_modified, broot):
                mod_sfrs.append(bsfr)
            else:
                add_sfrs.append(bsfr)
        mod_sfrs.sort(key=lambda x: x.attrib["cc-id"])
        add_sfrs.sort(key=lambda x: x.attrib["cc-id"])

        self.ol("<h3 id=\"modsfr-"+"@id"+"\" class=\"indexable\" data-level=\"3\"> Modified SFRs </h3>")
        self.ol("The SFRs listed in this section are defined in the "+short+
                " and relevant to the secure operation of the TOE.")
        if len(mod_sfrs)==0:
            self.ol("This PP-Module does not modify any SFRs defined by the " + short  + ".")
        else:
            self.handle_sparse_sfrs( mod_sfrs)
                
        if len(self.rfa("//cc:base-pp"))>1:
            self.ol("<h3 id=\"addsfr-"+id+"\" class=\"indexable\" data-level=\"3\"> Additional SFRs</h3>")
            if len(add_sfrs)>0:
                self.ol("This section defines additional SFRs that must be added to the TOE boundary in order to implement the functionality in any PP-Configuration where the "+short+" is claimed as the Base-PP.")
                self.handle_sparse_sfrs(add_sfrs)
            else:
                self.ol("This PP-Module does not define any additional SFRs for any PP-Configuration where the "+short+" is claimed as the Base-PP.")
        return add_sfrs + mod_sfrs
    
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
                self.show_package(pk)
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

        
        

        
    def template_module(self, node):
        self.apply_templates(self.rx("//*[@title='Introduction']|sec:Introduction"))
        self.apply_templates(self.rx("//*[@title='Conformance Claims']|sec:Conformance_Claims"))
        self.apply_templates(self.rx("//*[@title='Security Problem Description']|sec:Security_Problem_Description"))
        self.apply_templates(self.rx("//*[@title='Security Objectives']|sec:Security_Objectives"))
        self.apply_templates(self.rx("//*[@title='Security Requirements']|sec:Security_Requirements"))
        self.objectives_to_requirements()
        # <xsl:call-template name="mod-sars"/>
        # <xsl:call-template name="consistency-rationale"/>
        # <xsl:call-template name="opt-sfrs"/>
        # <xsl:call-template name="sel-sfrs"/>
        # <xsl:call-template name="ext-comp-defs"/>
        # self.apply-templates select="//cc:appendix"/>
        # <xsl:call-template name="acronyms"/>
        self.create_bibliography()

    
        
    def handle_section_hook_base(self, title, node):
        if title=="Security Functional Requirements":
            template_sfrs(self,node)
        else:
            super().handle_section_hook_base(title,node)

            
            
