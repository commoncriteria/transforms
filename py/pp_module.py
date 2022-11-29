import generic_pp_doc
import pp_util
from generic_pp_doc import NS

HTM_E=pp_util.get_HTM_E()

adopt=pp_util.adopt
apptext=pp_util.append_text

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

    def requirement_consistency_rationale_section(self, reqs, nonmsg, par, edoc=None):

        if len(reqs)==0:
            par.append(HTM_E.tr(HTM_E.td({"colspan":"2", "style":"text-align:center"},nonmsg)))
            return
        for req in reqs:
            tr = adopt(par, HTM_E.tr())
            tr.append(HTM_E.td(self.fcomp_cc_id(req)))
            td = adopt(tr, HTM_E.td())
            id=pp_util.get_attr_or(req, "id")
            conmods=[]
            if edoc is not None:
                conmods = edoc.node.xpath("cc:con-mod[@ref='"+id+"']", namespaces=NS)
            for conmod in conmods:
                self.handle_content(conmod, td)
            if len(conmods)==0:
                self.handle_content(req.find("cc:consistency-rationale", generic_pp_doc.NS), td)
    
    def template_sfrs(self, node ,par):
        par.append(HTM_E.h2({"class":"indexable","data-level":"2"},"Security Functional Requirements"))
        apptext(par, """The Security Functional Requirements included in this section
are derived from Part 2 of the Common Criteria for Information
Technology Security Evaluation """+pp_util.ccver()+", with additional extended functional components.")
        # self.handle_content(node)
        bases = self.rfa("//cc:base-pp")
        for base in bases:
            self.handle_basepp(base ,par)
        par.append(HTM_E.h2({"id":"man-sfrs","class":"indexable","data-level":"2"},"TOE Security Functional Requirements"))
        if len(self.man_sfrs)>0:
            apptext(par,"The following section describes the SFRs that must be satisfied by any TOE that claims conformance to this PP-Module."+
                             "These SFRs must be claimed regardless of which PP-Configuration is used to define the TOE.")
            self.handle_sparse_sfrs(self.man_sfrs, par)
        else:
            apptext(par,"This PP-Module does not define any mandatory SFRs.")
            
    def apply_template_to_element(self, node, parent):
        if node.tag == "{https://niap-ccevs.org/cc/v1}Module":
            return self.template_module(node, parent)
        else:
            return super().apply_template_to_element(node, parent)


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

        
    def handle_basepp(self, node, par):
        id = node.attrib["id"]
        base=self.edocs[id]
        short=base.short
        par.append(HTM_E.h2({"id":"secreq-"+id,
                             "class":"indexable",
                             "data-level":"2"},short+" Security Functional Requirements Direction"))
        if not self.apply_templates_single(node.find("cc:sec-func-req-dir", generic_pp_doc.NS), par):
            apptext(par,"In a PP-Configuration that includes the ")
            apptext(par,short)
            apptext(par,",the TOE is expected to rely on some of the security functions implemented by the")
            apptext(par,base.product)
            apptext(par,"as a whole and evaluated against the  " + short + ".")
            apptext(par,"The following sections describe any modifications that the ST author must make to the SFRs")
            apptext(par,"defined in the "+short+ "in addition to what is mandated by ")
            par.append(HTM_E.a({"class":"dynref","href":"#man-sfrs"},"Section "))
            apptext(par,".")
            par.append(HTM_E.h3({"id":"modsfr-"+id,"class":"indexable","data-level":"3"},"Modified SFRs"))
        apptext(par,"The SFRs listed in this section are defined in the "+short +\
            " and are relevant to the secure operation of the TOE.")
        if len(base.mod_sfrs)==0:
            apptext(par,"This PP-Module does not modify any SFRs defined by the " + short  + ".")
        else:
            self.handle_sparse_sfrs(base.mod_sfrs ,par)
                
        if len(self.rfa("//cc:base-pp"))>1:
            par.append(HTM_E.h3({"id":"addsfr-"+id,"class":"indexable","data-level":"3"},"Additional SFRs"))
            if len(base.add_sfrs)>0:
                apptext(par,"This section defines additional SFRs that must be added to the TOE boundary in order to implement the functionality in any PP-Configuration where the "+short+" is claimed as the Base-PP.")
                self.handle_sparse_sfrs(base.add_sfrs, par)
            else:
                apptext(par,"This PP-Module does not define any additional SFRs for any PP-Configuration where the "+short+" is claimed as the Base-PP.")
    
    def handle_conformance_claims(self, node, parent):
        dl=HTM_E.dl()
        parent.append(dl)
        dl.append(HTM_E.dt("Conformance Statement"))
        dd = HTM_E.dd()
        dl.append(dd)
        dd.append(HTM_E.p("""This PP-Module inherits exact conformance as required from the specified
          Base-PP and as defined in the CC and CEM addenda for Exact Conformance, Selection-based
          SFRs, and Optional SFRs (dated May 2017)."""))
        dd.append(HTM_E.p("""The following PPs and PP-Modules are allowed to be specified in a 
            PP-Configuration with this PP-Module."""))
        ul=adopt(dd, HTM_E.ul())
        bases = self.rfa("//cc:base-pp")
        for base in bases:
            li=adopt(ul, HTM_E.li())
            self.make_xref(base,li)
        dl.append(HTM_E.dt("CC Conformance Claims"))
        dl.append(HTM_E.dd("This PP-Module is conformant to Parts 2 (extended) and 3 (conformant) of Common Criteria "+pp_util.ccver()+"."))
        dl.append(HTM_E.dt("PP Claim"))
        dl.append(HTM_E.dd("This PP-Module does not claim conformance to any Protection Profile."))
        dl.append(HTM_E.dt("Package Claim"))
        dd = adopt(dl, HTM_E.dd())
        dd.text="This PP-Module "
        pks = self.rfa("//cc:include-pkg")
        ctr=len(pks)
        if ctr == 0:
            apptext(dd, "does not claim conformance to any packages")
        else:
            lagsep=""
            for pk in pks:
                ctr=ctr-1
                apptext(dd, lagsep)
                lagsep=","
                if ctr==2 :
                    lagsep="and"
                self.make_xref_edoc(pk, dd)
            apptext("conformant")
        apptext(dd,".")


  # <xsl:template match="cc:*[@id='obj_map']" mode="hook" name="obj-req-map">
    def objectives_to_requirements(self, par):
        addr_bys = self.rx("//cc:SO/cc:addressed-by")
        if len(addr_bys)==0:
            return
        par.append(HTM_E.h2({"id":"obj-req-map-","class":"indexable","data-level":"2"}, "TOE Security Functional Requirements Rationale"))
        par.append(HTM_E.p("""The following rationale provides justification for each 
 security objective for the TOE, showing that the SFRs are suitable to meet and
 achieve the security objectives:"""))
        table=adopt(par,HTM_E.table())
        caption=adopt(par,HTM_E.caption())
        self.create_ctr("Table", "t-obj-map", caption)
        apptext(caption, ": SFR Rationale")
        table.append(HTM_E.tr( HTM_E.th("Objective"), HTM_E.th("Addressed by"), HTM_E.th("Rationale")))
        prev_parent = None
        for addr_by in addr_bys:
            curr_parent=addr_by.find("..")
            if prev_parent!=curr_parent:
                tr = adopt(table, HTM_E.tr({"class":"major-row"}))
                rowspan=str(len(curr_parent.findall("cc:addressed-by", generic_pp_doc.NS)))
                content=pp_util.make_wrappable(curr_parent.attrib["name"])
                tr.append(HTM_E.td({"rowspan":rowspan}, content))
                prev_parent=curr_parent
            else:
                tr = adopt(table, HTM_E.tr())
            td = adopt(tr, HTM_E.td())
            self.handle_content(addr_by, td)
            td = adopt(tr, HTM_E.td())
            rational=addr_by.xpath("following-sibling::cc:rationale[1]",namespaces=generic_pp_doc.NS)
            self.handle_content(rational[0], td)

    def handle_consistency_row(self, base, thing, par):
        name=thing.attrib["name"]
        tr = adopt(par, HTM_E.tr())
        tr.append(HTM_E.td(name))
        td = adopt(tr, HTM_E.td())
        mod=base.find("cc:con-mod[@ref='"+name+"']", generic_pp_doc.NS)
        if mod is None:
            mod=thing.find("cc:consistency-rationale",generic_pp_doc.NS)
        self.handle_content(mod, td)

    def handle_consistency_rows(self, base, rows, par):
        for row in rows:
            self.handle_consistency_row(base, row, par)
            
    def consistency_rationale(self, par):
        par.append(
            HTM_E.h1({"id":"mod-conrat","class":"indexable","data-level":"1"},"Consistency Rationale"))
        bases = self.rfa("//cc:base-pp")
        for base in bases:
            id   = base.attrib["id"]
            edoc = self.edocs[id]
            self.set_underscore(edoc.short)
            par.append(HTM_E.h2({"id":"conrat-"+id,"class":"indexable","data-level":"2"}, edoc.short))
            par.append(HTM_E.h3({"id":"contoe-"+id+"-","class":"indexable","data-level":"3"}, "Consistency of TOE Type"))

            self.handle_content(base.find("cc:con-toe",generic_pp_doc.NS), par)
            par.append(HTM_E.h3({"id":"consecprob-"+id+"-","class":"indexable","data-level":"3"},
                                "Consistency of Security Problem Definition"))
            self.handle_content(base.find("cc:con-sec-prob",generic_pp_doc.NS), par)
            table = adopt(par, HTM_E.table())
            table.append(HTM_E.tr( HTM_E.th("PP-Module Threat, Assumption, OSP"),
                                   HTM_E.th("Consistency Rationale")))
            things = self.rx("//cc:threat[cc:description]|//cc:assumption[cc:description]|//cc:OSP[cc:description]")
            self.handle_consistency_rows(base, things, table)
            par.append(HTM_E.h3({"id":"conobj-"+id, "class":"indexable","data-level":"3"}, "Consistency of Objectives"))
            p_el = adopt(par, HTM_E.p())
            self.handle_content(base.find("./cc:con-obj",generic_pp_doc.NS), p_el)
            sos_des = self.rfa("//cc:SO[cc:description]")
            if len(sos_des):
                apptext(p_el, "The objectives for the TOEs are consistent with the ")
                edoc.make_xref_edoc(p_el)
                apptext(p_el, " based on the following rationale:")
                table=adopt(par, HTM_E.table())
                table.append(HTM_E.tr(HTM_E.th("PP-Module TOE Objective"), HTM_E.th("Consistency Rationale")))
                self.handle_consistency_rows(base, sos_des, table)
            self.handle_content(base.find("./cc:con-op-en", generic_pp_doc.NS), par)
            soes = self.rfa("//cc:SOE")
            if len(soes)>0:
                p_el = adopt(par, HTM_E.p("The objectives for the TOE's OE are consistent with the "))
                edoc.make_xref_edoc(p_el)
                apptext(p_el, " based on the following rationale:")
                table = adopt(par, HTM_E.table())
                table.append(HTM_E.tr(HTM_E.th("PP-Module OE Objective"), HTM_E.th("Consistency Rationale")))

                self.handle_consistency_rows(base,soes, table)
            par.append(HTM_E.h3({"id":"conreq-"+id, "class":"indexable","data-level":"3"}, 
                                "Consistency of Requirements"))
            self.handle_content(base.find("./cc:con-req", generic_pp_doc.NS), par)
            apptext(par,"This PP-Module identifies several SFRs from the")
            edoc.make_xref_edoc(par)
            apptext(par," that are needed to support "+self.root.attrib["target-product"])
            apptext(par," functionality.")
            apptext(par,"This is considered to be consistent because the functionality provided by the")
            edoc.make_xref_edoc(par)
            apptext(par," is being used for its intended purpose.")
            if len(edoc.mod_sfrs)>0:
                apptext(par,"The PP-Module also identifies a number of modified SFRs from the")
                edoc.make_xref_edoc(par)
                if len(edoc.add_sfrs)>0:
                    apptext(par,"as well as new SFRs ")
                apptext(par,"that are used entirely to provide functionality for "+edoc.get_products())
            elif len(edoc.add_sfrs)>0:
                apptext(par,"The PP-Module identifies new SFRs that are used entirely to provide")
                apptext(par," functionality for "+  edoc.get_products() + ".")
            apptext(par,"The rationale for why this does not conflict with the claims")
            apptext(par,"defined by the "+ edoc.short+" are as follows:")
            table = adopt(par, HTM_E.table())
            table.append(HTM_E.tr(HTM_E.th("PP-Module Requirement"),
                                  HTM_E.th("Consistency Rationale")))
            table.append(HTM_E.tr(HTM_E.th({"colspan":"2"}, "Modified SFRs")))
            self.requirement_consistency_rationale_section(
                edoc.mod_sfrs, 
                "This PP-Module does not modify any requirements when the "+\
                edoc.short + " is the base.",table, edoc=edoc)
            table.append(HTM_E.tr(HTM_E.th({"colspan":"2"}, "Additional SFRs")))
            self.requirement_consistency_rationale_section(
                edoc.add_sfrs, 
                "This PP-Module does not levy any addition requirements when the "+\
                edoc.short + " is the base.", table, edoc=edoc)
            table.append(HTM_E.tr(HTM_E.th({"colspan":"2"}, "Mandatory SFRs")))
            self.requirement_consistency_rationale_section(
                self.man_sfrs, 
                "This PP-Module does not define any Mandatory requirements.",
                table
            )
            table.append(HTM_E.tr(HTM_E.th({"colspan":"2"}, "Optional SFRs")))
            self.requirement_consistency_rationale_section(
                self.opt_sfrs, 
                "This PP-Module does not define any Strictly Optional requirements.",
                table)

            table.append(HTM_E.tr(HTM_E.th({"colspan":"2"}, "Objective SFRs")))
            self.requirement_consistency_rationale_section(
                self.obj_sfrs, 
                "This PP-Module does not define any Objective requirements.",
                table)
            table.append(HTM_E.tr(HTM_E.th({"colspan":"2"}, "Implementation-based SFRs")))
            self.requirement_consistency_rationale_section(
                self.impl_sfrs, 
                "This PP-Module does not define any Implementation-based requirements.",
                table)
            table.append(HTM_E.tr(HTM_E.th({"colspan":"2"}, "Selection-based SFRs")))
            self.requirement_consistency_rationale_section(
                self.sel_sfrs, 
                "This PP-Module does not define any Implementation-based requirements.",
                table)


        
    def template_module(self, node, parent):
        self.apply_templates(self.rx("//*[@title='Introduction']|sec:Introduction"),parent)
        self.apply_templates(self.rx("//*[@title='Conformance Claims']|sec:Conformance_Claims"),parent)
        self.apply_templates(self.rx("//*[@title='Security Problem Description']|sec:Security_Problem_Description"),parent)
        self.apply_templates(self.rx("//*[@title='Security Objectives']|sec:Security_Objectives"),parent)
        self.apply_templates(self.rx("//*[@title='Security Requirements']|sec:Security_Requirements"),parent)
        self.objectives_to_requirements(parent)
        self.consistency_rationale(parent)
        self.handle_ext_comp_defs(parent)
        self.handle_optional_requirements(parent)
        self.handle_selection_based_requirements(node, parent)
        self.apply_templates(self.rfa("//cc:appendix"), parent)
        self.create_acronym_listing(parent)
        self.create_bibliography(parent)
    
    def doctype(self):
        return "PP-Module"
        
    def handle_section_hook_base(self, title, node, parent):
        if title=="Security Functional Requirements":
            return template_sfrs(self,node, parent)
        else:
            return super().handle_section_hook_base(title,node ,parent)

            
            
