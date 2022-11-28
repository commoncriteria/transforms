import generic_pp_doc
import pp_util
from generic_pp_doc import NS


class ppmod(generic_pp_doc.generic_pp_doc):
    def __init__(self, root, workdir, boilerplate):
        super().__init__(root, workdir, boilerplate)

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
            ret="<tr><td colspan=\"2\" style=\"text-align:center\">"
            ret+=nonmsg
            ret+="</td></tr>"
            return ret
        ret=""
        for req in reqs:
            ret+="<tr><td>"+self.fcomp_cc_id(req)+"</td>"
            ret+="<td>"
            id=pp_util.get_attr_or(req, "id")
            conmods=[]
            if edoc is not None:
                conmods = edoc.node.xpath("cc:con-mod[@ref='"+id+"']", namespaces=NS)
            for conmod in conmods:
                ret += self.handle_content(conmod)
            if len(conmods)==0:
                ret += self.handle_content(req.find("cc:consistency-rationale", generic_pp_doc.NS))
                ret += "</td></tr>\n"
        return ret

    
    def template_sfrs(self, node):
        ret="<h2 class=\"indexable\" data-level=\"2\">Security Functional Requirements</h2>"
        ret+="The Security Functional Requirements included in this section"
        ret+="are derived from Part 2 of the Common Criteria for Information"
        ret+="Technology Security Evaluation, "
        ret+=pp_util.ccver()
        ret+=", with additional extended functional components."
        # self.handle_content(node)
        bases = self.rfa("//cc:base-pp")
        for base in bases:
            ret+=self.handle_basepp(base)

        ret+="<h2 id=\"man-sfrs\" class=\"indexable\" data-level=\"2\">TOE Security Functional Requirements</h2>"

#HANDLE_BASSPP
        if len(self.man_sfrs)>0:
            ret+="The following section describes the SFRs that must be satisfied by any TOE that claims conformance to this PP-Module."
            ret+="These SFRs must be claimed regardless of which PP-Configuration is used to define the TOE."
            ret+=self.handle_sparse_sfrs(self.man_sfrs)
        else:
            ret+="This PP-Module does not define any mandatory SFRs."
        return ret
            
    def apply_template_to_element(self, node):
        if node.tag == "{https://niap-ccevs.org/cc/v1}Module":
            return self.template_module(node)
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
        ret=""
        id = node.attrib["id"]
        base=self.edocs[id]
        short=base.short
        ret+="<h2 id=\""+"secreq-"+id+"\" class=\"indexable\" data-level=\"2\">"
        ret+=short
        ret+=" Security Functional Requirements Direction"
        ret+="</h2>"
        if not self.apply_templates_single(node.find("cc:sec-func-req-dir", generic_pp_doc.NS)):
            ret+="In a PP-Configuration that includes the "
            ret+=short
            ret+=",the TOE is expected to rely on some of the security functions implemented by the"
            ret+=base.product
            ret+="as a whole and evaluated against the  " + short + "."
            ret+="The following sections describe any modifications that the ST author must make to the SFRs"
            ret+="defined in the "+short+ "in addition to what is mandated by <a class=\"dynref\" href=\"#man-sfrs\">Section </a>."
        ret+="<h3 id=\"modsfr-"+id+"\" class=\"indexable\" data-level=\"3\"> Modified SFRs </h3>"
        ret+="The SFRs listed in this section are defined in the "+short +\
            " and are relevant to the secure operation of the TOE."
        if len(base.mod_sfrs)==0:
            ret+="This PP-Module does not modify any SFRs defined by the " + short  + "."
        else:
            ret+=self.handle_sparse_sfrs(base.mod_sfrs)
                
        if len(self.rfa("//cc:base-pp"))>1:
            ret+="<h3 id=\"addsfr-"+id+"\" class=\"indexable\" data-level=\"3\"> Additional SFRs</h3>"
            if len(base.add_sfrs)>0:
                ret+="This section defines additional SFRs that must be added to the TOE boundary in order to implement the functionality in any PP-Configuration where the "+short+" is claimed as the Base-PP."
                ret+=self.handle_sparse_sfrs(base.add_sfrs)
            else:
                ret+=self.ol("This PP-Module does not define any additional SFRs for any PP-Configuration where the "+short+" is claimed as the Base-PP.")
        # base.add_sfrs + base.mod_sfrs                
        return ret
    
    def handle_conformance_claims(self, node):
        ret="""
    <dl>
        <dt>Conformance Statement</dt>
        <dd>
          <p>This PP-Module inherits exact conformance as required from the specified
          Base-PP and as defined in the CC and CEM addenda for Exact Conformance, Selection-based
          SFRs, and Optional SFRs (dated May 2017).</p>
          <p>The following PPs and PP-Modules are allowed to be specified in a 
            PP-Configuration with this PP-Module. </p> <ul>
"""
        bases = self.rfa("//cc:base-pp")
        for base in bases:
            ret+="<li>"+self.make_xref(base)+"</li>"
        ret+="</ul>\n"
        ret+="</dd>"
        ret+="<dt>CC Conformance Claims</dt>"
        ret+="<dd>This PP-Module is conformant to Parts 2 (extended) and 3 (conformant) of Common Criteria "+pp_util.ccver()+".</dd>"
        ret+="<dt>PP Claim </dt>"
        ret+="<dd>This PP-Module does not claim conformance to any Protection Profile. </dd>"
        ret+="<dt>Package Claim</dt>"
        ret+="<dd>This PP-Module"
        pks = self.rfa("//cc:include-pkg")
        ctr=len(pks)
        if ctr == 0:
            ret+="does not claim conformance to any packages"
        else:
            lagsep=""
            for pk in pks:
                ctr=ctr-1
                self.o(lagsep)
                lagsep=","
                if ctr==2 :
                    lagsep="and"
                ret += self.make_xref_edoc(pk)
            ret += "conformant"
        ret+=".</dd>"
        ret+="</dl>"
        return ret


  # <xsl:template match="cc:*[@id='obj_map']" mode="hook" name="obj-req-map">
    def objectives_to_requirements(self):
        addr_bys = self.rx("//cc:SO/cc:addressed-by")
        if len(addr_bys)==0:
            return
        ret="<h2 id=\"obj-req-map-\" class=\"indexable\" data-level=\"2\">TOE Security Functional Requirements Rationale</h2>"
        ret+="""<p>The following rationale provides justification for each 
 security objective for the TOE, showing that the SFRs are suitable to meet and
 achieve the security objectives:</p>
  <table>
        <caption>"""
        ret+=self.create_ctr("Table", "t-obj-map")
        ret+=": SFR Rationale</caption>"
        ret+="<tr><th>Objective</th><th>Addressed by</th><th>Rationale</th></tr>"
        prev_parent = None
        for addr_by in addr_bys:
            ret+="<tr"
            curr_parent=addr_by.find("..")
            if prev_parent!=curr_parent:
                ret+=" class=\"major-row\">"
                ret+="<td rowspan=\""
                ret+=str(len(curr_parent.findall("cc:addressed-by", generic_pp_doc.NS)))
                ret+="\">"
                ret+=pp_util.make_wrappable(curr_parent.attrib["name"])
                ret+="</td"
                prev_parent=curr_parent
            ret+="><td>"
            ret+=self.handle_content(addr_by)
            ret+="</td><td>"
            rational=addr_by.xpath("following-sibling::cc:rationale[1]",namespaces=generic_pp_doc.NS)
            ret+=self.handle_content(rational[0])
            ret+="</td></tr>"
        ret+="</table>"
        return ret

    def handle_consistency_row(self, base, thing):
        name=thing.attrib["name"]
        ret="<tr>"
        ret+="  <td>"+name+"</td>"
        ret+="  <td>"
        mod=base.find("cc:con-mod[@ref='"+name+"']", generic_pp_doc.NS)
        if mod is None:
            mod=thing.find("cc:consistency-rationale",generic_pp_doc.NS)
        ret+=self.handle_content(mod)
        ret+="  </td>"
        ret+="</tr>"
        return ret

    def handle_consistency_rows(self, base, rows):
        ret=""
        for row in rows:
            ret+=self.handle_consistency_row(base, row)
        return ret
            
    def consistency_rationale(self):
        ret = "<h1 id=\"mod-conrat\" class=\"indexable\" data-level=\"1\">Consistency Rationale</h1>"
        bases = self.rfa("//cc:base-pp")
        for base in bases:
            id   = base.attrib["id"]
            edoc = self.edocs[id]
            self.set_underscore(edoc.short)
            ret+="<h2 id=\"conrat-"+id+"\" class=\"indexable\" data-level=\"2\">"
            ret+=edoc.short
            ret+="</h2>"
            ret+="    <h3 id=\"contoe-"+id+"-\" class=\"indexable\" data-level=\"3\">"
            ret+="Consistency of TOE Type"
            ret+="</h3>"
            ret+=self.handle_content(base.find("cc:con-toe",generic_pp_doc.NS))
            ret+="    <h3 id=\"consecprob-"+id+"-\" class=\"indexable\" data-level=\"3\">"
            ret+="Consistency of Security Problem Definition"
            ret+="</h3>"
            ret+=self.handle_content(base.find("cc:con-sec-prob",generic_pp_doc.NS))
            ret+="<table><tr><th>PP-Module Threat, Assumption, OSP</th><th>Consistency Rationale</th></tr>"
            things = self.rx("//cc:threat[cc:description]|//cc:assumption[cc:description]|//cc:OSP[cc:description]")
            ret+=self.handle_consistency_rows(base, things)
            ret+="</table>"

            ret+="<h3 id=\"conobj-"+id+"\" class=\"indexable\" data-level=\"3\">"
            ret+="Consistency of Objectives"
            ret+="</h3>"
            ret+="<p>"
            ret+=self.handle_content(base.find("./cc:con-obj",generic_pp_doc.NS))
            sos_des = self.rfa("//cc:SO[cc:description]")
            ret+="</p>"
            if len(sos_des):
                ret+="The objectives for the TOEs are consistent with the "
                ret+=edoc.make_xref_edoc()
                ret+=" based on the following rationale:"
                ret+="<table><tr><th>PP-Module TOE Objective</th><th>Consistency Rationale</th></tr>"
                ret+=self.handle_consistency_rows(base, sos_des)
                ret+="</table>"
            ret+=self.handle_content(base.find("./cc:con-op-en", generic_pp_doc.NS))
            soes = self.rfa("//cc:SOE")
            if len(soes)>0:
                ret+="<p>The objectives for the TOE's OE are consistent with the "
                ret+=edoc.make_xref_edoc()
                ret+="based on the following rationale:</p>"
                ret+="<table><tr><th>PP-Module OE Objective</th><th>Consistency Rationale</th></tr>"
                ret+=self.handle_consistency_rows(base,soes)
                ret+="</table>"
            ret+="<h3 id=\"conreq-"+id+"\" class=\"indexable\" data-level=\"3\">"
            ret+="Consistency of Requirements"
            ret+="</h3>"
            ret+=self.handle_content(base.find("./cc:con-req", generic_pp_doc.NS))
            ret+="This PP-Module identifies several SFRs from the"
            ret+=edoc.make_xref_edoc()
            ret+=" that are needed to support "
            ret+=self.root.attrib["target-product"]
            ret+=" functionality."
            ret+="This is considered to be consistent because the functionality provided by the"
            ret+=edoc.make_xref_edoc()
            ret+=" is being used for its intended purpose."
            if len(edoc.mod_sfrs)>0:
                ret+="The PP-Module also identifies a number of modified SFRs from the"
                ret+=edoc.make_xref_edoc()
                if len(edoc.add_sfrs)>0:
                    ret+="as well as new SFRs "
                ret+="that are used entirely to provide functionality for"
                ret+=edoc.get_products()+"."
            elif len(edoc.add_sfrs)>0:
                ret+="The PP-Module identifies new SFRs that are used entirely to provide"
                ret+="functionality for"
                ret+=edoc.get_products()+"."
            ret+="The rationale for why this does not conflict with the claims"
            ret+="defined by the"
            ret+=edoc.short+" are as follows:"
            ret+="<table>"
            ret+="<tr><th>PP-Module Requirement</th><th>Consistency Rationale</th></tr>"
            ret+="<tr><th colspan=\"2\"> Modified SFRs</th></tr>"
            ret+=self.requirement_consistency_rationale_section(edoc.mod_sfrs, 
               "This PP-Module does not modify any requirements when the "+\
                                                           edoc.short + " is the base.",edoc=edoc)

            ret+="<tr><th colspan=\"2\"> Additional SFRs</th></tr>"
            ret+=self.requirement_consistency_rationale_section(edoc.add_sfrs, 
               "This PP-Module does not levy any addition requirements when the "+\
                                                           edoc.short + " is the base.",edoc=edoc)
            ret+="<tr><th colspan=\"2\"> Mandatory SFRs</th></tr>"
            ret+=self.requirement_consistency_rationale_section(self.man_sfrs, 
                                                           "This PP-Module does not define any Mandatory requirements.")


            ret+="<tr><th colspan=\"2\">Optional SFRs</th></tr>"
            ret+=self.requirement_consistency_rationale_section(self.opt_sfrs, 
                                                           "This PP-Module does not define any Strictly Optional requirements.")
            ret+="<tr><th colspan=\"2\">Objective SFRs</th></tr>"
            ret+=self.requirement_consistency_rationale_section(self.obj_sfrs, 
                                                           "This PP-Module does not define any Objective requirements.")
            ret+="<tr><th colspan=\"2\">Implementation-based SFRs</th></tr>"
            ret+=self.requirement_consistency_rationale_section(self.impl_sfrs, 
                                                           "This PP-Module does not define any Implementation-based requirements.")
            ret+="<tr><th colspan=\"2\">Selection-based SFRs</th></tr>"
            ret+=self.requirement_consistency_rationale_section(self.sel_sfrs, 
                                                           "This PP-Module does not define any Selection-based requirements.")
            ret+="</table>"
        return ret


        
    def template_module(self, node):
        ret = self.apply_templates(self.rx("//*[@title='Introduction']|sec:Introduction"))
        ret+=self.apply_templates(self.rx("//*[@title='Conformance Claims']|sec:Conformance_Claims"))
        ret+=self.apply_templates(self.rx("//*[@title='Security Problem Description']|sec:Security_Problem_Description"))
        ret+=self.apply_templates(self.rx("//*[@title='Security Objectives']|sec:Security_Objectives"))
        ret+=self.apply_templates(self.rx("//*[@title='Security Requirements']|sec:Security_Requirements"))
        ret+=self.objectives_to_requirements()
        ret+=self.consistency_rationale()
        ret+=self.handle_ext_comp_defs()
        ret+=self.handle_optional_requirements()
        ret+=self.handle_selection_based_requirements(node)
        ret+=self.apply_templates(self.rfa("//cc:appendix"))
        ret+=self.create_acronym_listing()
        ret+=self.create_bibliography()
        return ret
    
    def doctype(self):
        return "PP-Module"
        
    def handle_section_hook_base(self, title, node):
        if title=="Security Functional Requirements":
            return template_sfrs(self,node)
        else:
            return super().handle_section_hook_base(title,node)

            
            
