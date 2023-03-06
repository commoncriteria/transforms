import generic_pp_doc
import pp_util
import edoc
import css_content
from generic_pp_doc import NS

HTM_E=pp_util.get_HTM_E()

adopt=pp_util.adopt


class ppmod(generic_pp_doc.generic_pp_doc):
    def __init__(self, root, workdir, boilerplate):
        """
        Creates a new PP module XML thing

        :param root: The root node of the XML Element tree
        :param workdir: The directory to find dependent documents.
        :param boilerplate: The boilerplate document
        :returns: 
        """

        super().__init__(root, workdir, boilerplate)
        self.bases = self.make_edocs(workdir)

    def handle_unknown_depends(self, sfr, attrval):
        """
        A hook from the generic_pp_doc. 
        It attempts to handle SFRs based on a base.

        :param  sfr: The f-component in question.
        :param  attrval: The ID that the sfr is dependent on.
        """
        if self.rf("//cc:base-pp[@id='"+attrval+"']") is not None:
            # This seems to be handled already in the Edoc initialization
            base = self.edocs[attrval]
            base.add_base_dependent_sfr(sfr)
        else:
            raise Exception("Dont know how to handle: "+ sfr["cc-id"])

    def make_edocs(self, workdir):
        """
        Makes only the edocs. The base handles include_pkg elements.
        :param  workdir: The directory that has the other documents
        where the id in the document is the root name of the 
        external document.
        :returns A Dictionary where the 'id' of the document is 
        mapped to the Edoc object representing the external document.
        """
        ret = super().make_edocs(workdir)
        nonxmldocs = self.rfa("//cc:base-pp[@name]")
        for doc in nonxmldocs:
            ret[doc.attrib["id"]] = edoc.Edoc(doc, workdir)
        return ret
    

    def requirement_consistency_rationale_section(self, reqs, nonmsg_end, par, edoc=None):
        """
        Writes a consistency rationale section for modified and additional requirements.

        :param  reqs: The SFRs for this section
        :param  nonmsg_end: The end of a message when there are no sfrs
        :param  par: The output HTML element.
        :param  edoc: The edoc that's associated with this. If it's None, some data will not
        be written out.
        """
        if len(reqs)==0:
            nonmsg = "This PP-Module does not "+nonmsg_end
            par.append(HTM_E.tr(HTM_E.td({"colspan":"2", "style":"text-align:center"},nonmsg)))
            return
        for req in reqs:
            tr = adopt(par, HTM_E.tr())
            tr.append(HTM_E.td(self.fcomp_cc_id(req)))
            td = adopt(tr, HTM_E.td())
            id=pp_util.get_attr_or(req, "id")
            conmods=[]
            if edoc is not None:
                edoc_node = edoc.get_orig_node()
                conmods = edoc_node.xpath("cc:con-mod[@ref='"+id+"']", namespaces=NS)
            for conmod in conmods:
                self.handle_content(conmod, td)
            if len(conmods)==0:
                self.handle_content(req.find("cc:consistency-rationale", generic_pp_doc.NS), td)


    def sd_handle_bases(self, out):
        """
        Handles bases for the supporting document
        :param  out: The HTML output node
        """
        for base_id in self.bases:
            base = self.bases[base_id]
            out.append(self.sec(base.get_title()))
            out.append(HTM_E.p(
                """The EAs defined in this section are only applicable 
                in cases where the TOE claims conformance to a PP-Configuration 
                that includes the """\
                + base.short()+"."))
            out.append(self.sec({"id": base_id+"_mod_sfrs-"},"Modified SFRs"))
            mods = base.mod_sfrs
            if len(mods) == 0:
                out.append(HTM_E.p("The PP-Module does not modify any requirements when the "+base.short() + " is the base."))
            else:
                self.handle_sparse_sfrs(mods, out, base_id+"__mod_sfrs", True)
            self.end_section()
            out.append(self.sec({"id": base_id+"_add_sfrs-"},"Additional SFRs"))
            adds = base.add_sfrs
            if len(adds) == 0:
                out.append(HTM_E.p("The PP-Module does levy any additional requirements when the "+base.short() + " is the base."))
            else:
                self.handle_sparse_sfrs(adds, out, base_id+"__add_sfrs",True)
            self.end_section()
            self.end_section()
        return

                
    def template_sfrs(self, out):
        """
        Writes out all the SFRs associated with this PP Module to 
        an HTML tree.

        :param node: ignored
        :param out: The HTML ElementTree output node
        """
        bases = self.rfa("//cc:base-pp")
        for base in bases:
            self.handle_basepp(base ,out)
        out.append(self.sec({"id":"man-sfrs"},"TOE Security Functional Requirements"))
        if len(self.man_sfrs)>0:
            self.add_text(out,"The following section describes the SFRs that must be satisfied by any TOE that claims conformance to this PP-Module."+
                             "These SFRs must be claimed regardless of which PP-Configuration is used to define the TOE.")
            self.handle_sparse_sfrs(self.man_sfrs, out, "man_sfrs")
        else:
            self.add_text(out," This PP-Module does not define any mandatory SFRs.")
        self.end_section()

    # Not sure if this should be handled this way. We're missing
    # the comment check that's defined in generic_pp_doc.
    def apply_template_to_element(self, node, out):
        """
        Converts an XML ElementTree to an HTML output ElementTree.

        :param node: The input ElementTree.
        :param out: The HTML output ElementTree node
        :returns: Whether there was content to write out.
        """
        if node.tag == "{https://niap-ccevs.org/cc/v1}Module":
            return self.template_module(out)
        elif node.tag == "{https://niap-ccevs.org/cc/v1}sec-func-req-dir":
            self.handle_content(node, out)
        else:
            return super().apply_template_to_element(node, out)


    def is_base(self, attr):
        """
        Tests whether the attribute specified is the ID of a base.

        :param attr: The String value of a possible base ID.
        :returns True if it is associated with a base, False otherwise.
        """
        b_el = self.rf("//cc:base-pp[@id='"+attr+"']")
        return b_el is not None

    def handle_basepp(self, node, out):
        """
        Converts a cc:base-pp Element tree to an HTML output subtree.
        
        :param  node: The cc:base-pp ElementTree Element
        :param  out: ElementTree root of the HTML output subtree.
        """
        id = node.attrib["id"]
        base=self.bases[id]
        short=base.short()
        out.append(self.sec({"id":"secreq-"+id},short+" Security Functional Requirements Direction"))
        if not self.apply_templates_single(node.find("cc:sec-func-req-dir", generic_pp_doc.NS), out):
            self.add_text(out,"In a PP-Configuration that includes the ")
            self.add_text(out,short)
            self.add_text(out,",the TOE is expected to rely on some of the security functions implemented by the")
            self.add_text(out,base.get_product())
            self.add_text(out," as a whole and evaluated against the  " + short + ".")
            self.add_text(out," The following sections describe any modifications that the ST author must make to the SFRs")
            self.add_text(out," defined in the "+short+" in addition to what is mandated by ")
            out.append(HTM_E.a({"class":"dynref","href":"#man-sfrs"},"section "))
            self.add_text(out,".")
            
        out.append(self.sec({"id":"modsfr-"+id},"Modified SFRs"))
        self.add_text(out,"The SFRs listed in this section are defined in the "+short +\
                " and are relevant to the secure operation of the TOE.")
        if len(base.mod_sfrs)==0:
            self.add_text(out," This PP-Module does not modify any SFRs defined by the " + short  + ".")
        else:
            self.handle_sparse_sfrs(base.mod_sfrs ,out, id+"__mod_sfrs")
        self.end_section()
                
        if len(self.rfa("//cc:base-pp"))>1:
            out.append(self.sec({"id":"addsfr-"+id},"Additional SFRs"))
            if len(base.add_sfrs)>0:
                self.add_text(out,"This section defines additional SFRs that must be added to the TOE boundary in order to implement the functionality in any PP-Configuration where the "+short+" is claimed as the Base-PP.")
                self.handle_sparse_sfrs(base.add_sfrs, out, id+"__add_sfrs")
            else:
                self.add_text(out,"This PP-Module does not define any additional SFRs for any PP-Configuration where the "+short+" is claimed as the Base-PP.")
            self.end_section()
        self.end_section()
    



    def handle_consistency_row(self, base, thing, out):
        """
        Writes out a consistency row in a table.

        :param  base: The base document that is being altered
        :param  thing: ElementTree of the aspect being altered. It case a cc:consistency-rationale.
        :param  out: The root of the HTML output ElementTree node
        """
        name=thing.attrib["name"]
        tr = adopt(out, HTM_E.tr())
        tr.append(HTM_E.td(name))
        td = adopt(tr, HTM_E.td())
        mod=base.find("cc:con-mod[@ref='"+name+"']", generic_pp_doc.NS)
        if mod is None:
            mod=thing.find("cc:consistency-rationale",generic_pp_doc.NS)
        self.handle_content(mod, td)

    def handle_consistency_rows(self, base, rows, out):
        """
        Writes out a bunch of rows in the consistency table.

        :param  base: The base document that is being altered
        :param  thing: ElementTree of the aspect being altered. It case a cc:consistency-rationale.
        :param  out: The root of the HTML output ElementTree node
        """
        for row in rows:
            self.handle_consistency_row(base, row, out)

    def consistency_of_toe_type(self, out, base, id):
        """
        Writes out consistency of toe type section.
        
        :param  out: The root of the HTML output ElementTree node
        :param  base: The base being written out
        :param  id: Unique id of the base.
        :returns
        """
        out.append(self.sec({"id":"contoe-"+id+"-"}, "Consistency of TOE Type"))
        self.handle_content(base.find("cc:con-toe",generic_pp_doc.NS), out)
        self.end_section()

    def consistency_of_security_problem_def(self, out, base, id):
        """
        Writes out the section for "Consistency of Security Problem Defintion.

        :param  out: The root of the HTML output ElementTree node        
        :param  base: eDoc of the base pp_doc 
        :param  id: Value to base the created IDs on (usually the id of the base)
        """
        out.append(self.sec({"id":"consecprob-"+id+"-"},
                            "Consistency of Security Problem Definition"))
        self.handle_content(base.find("cc:con-sec-prob",generic_pp_doc.NS), out)
        table = adopt(out, HTM_E.table())
        table.append(HTM_E.tr( HTM_E.th("PP-Module Threat, Assumption, OSP"),
                               HTM_E.th("Consistency Rationale")))
        things = self.rx("//cc:threat[cc:description]|//cc:assumption[cc:description]|//cc:OSP[cc:description]")
        self.handle_consistency_rows(base, things, table)
        self.end_section()


    def consistency_of_requirements(self, out, base, id, edoc):
        """
        Writes out the section for "Consistency of Requirements"
        
        :param  out: The root of the HTML output ElementTree node
        :param  base: The base being written out
        :param  id: Value to base the created IDs on (usually the id of the base)
        :param  edoc
        """
        out.append(self.sec({"id":"conreq-"+id}, 
                            "Consistency of Requirements"))
        self.handle_content(base.find("./cc:con-req", generic_pp_doc.NS), out)
        self.add_text(out,"This PP-Module identifies several SFRs from the")
        edoc.make_xref_edoc(out)
        self.add_text(out," that are needed to support "+self.rf("cc:product_class").text)
        self.add_text(out," functionality.")
        self.add_text(out," This is considered to be consistent because the functionality provided by the")
        edoc.make_xref_edoc(out)
        self.add_text(out," is being used for its intended purpose.")
        if len(edoc.mod_sfrs)>0:
            self.add_text(out," The PP-Module also identifies a number of modified SFRs from the")
            edoc.make_xref_edoc(out)
            if len(edoc.add_sfrs)>0:
                self.add_text(out,"as well as new SFRs ")
            self.add_text(out,"that are used entirely to provide functionality for "+edoc.get_products())
        elif len(edoc.add_sfrs)>0:
            self.add_text(out," The PP-Module identifies new SFRs that are used entirely to provide")
            self.add_text(out," functionality for "+  edoc.get_products() + ".")
        self.add_text(out," The rationale for why this does not conflict with the claims")
        self.add_text(out," defined by the "+ edoc.short()+" are as follows:")
        table = adopt(out, HTM_E.table())
        table.append(HTM_E.tr(HTM_E.th("PP-Module Requirement"),
                              HTM_E.th("Consistency Rationale")))
        table.append(HTM_E.tr(HTM_E.th({"colspan":"2"}, "Modified SFRs")))
        self.requirement_consistency_rationale_section(
            edoc.mod_sfrs, 
            "modify any requirements when the "+\
            edoc.short() + " is the base.",table, edoc=edoc)
        table.append(HTM_E.tr(HTM_E.th({"colspan":"2"}, "Additional SFRs")))
        self.requirement_consistency_rationale_section(
            edoc.add_sfrs, 
            "levy any addition requirements when the "+\
            edoc.short() + " is the base.", table, edoc=edoc)
        table.append(HTM_E.tr(HTM_E.th({"colspan":"2"}, "Mandatory SFRs")))
        self.requirement_consistency_rationale_section(
            self.man_sfrs, 
            "define any Mandatory requirements.",
            table
        )
        table.append(HTM_E.tr(HTM_E.th({"colspan":"2"}, "Optional SFRs")))
        self.requirement_consistency_rationale_section(
            self.opt_sfrs, 
            "define any Strictly Optional requirements.",
            table)

        table.append(HTM_E.tr(HTM_E.th({"colspan":"2"}, "Objective SFRs")))
        self.requirement_consistency_rationale_section(
            self.obj_sfrs, 
            "define any Objective requirements.",
            table)
        table.append(HTM_E.tr(HTM_E.th({"colspan":"2"}, "Implementation-based SFRs")))
        self.requirement_consistency_rationale_section(
            self.impl_sfrs, 
            "define any Implementation-based requirements.",
            table)
        table.append(HTM_E.tr(HTM_E.th({"colspan":"2"}, "Selection-based SFRs")))
        self.requirement_consistency_rationale_section(
            self.sel_sfrs, 
            "define any Implementation-based requirements.",
            table)
        self.end_section()


    def consistency_of_objectives(self, out, base, id, edoc):
        """
        Writes out the section for "Consistency of Objectives"
        
        :param  out: The root of the HTML output ElementTree node
        :param  base: The base being written out
        :param  id: Value to base the created IDs on (usually the id of the base)
        :param  edoc: The edoc objective of the base
        :returns
        """
        out.append(self.sec({"id":"conobj-"+id}, "Consistency of Objectives"))
        p_el = adopt(out, HTM_E.p())
        self.handle_content(base.find("./cc:con-obj",generic_pp_doc.NS), p_el)
        sos_des = self.rfa("//cc:SO[cc:description]")
        if len(sos_des):
            self.add_text(p_el, "The objectives for the TOEs are consistent with the ")
            edoc.make_xref_edoc(p_el)
            self.add_text(p_el, " based on the following rationale:")
            table=adopt(out, HTM_E.table())
            table.append(HTM_E.tr(HTM_E.th("PP-Module TOE Objective"), HTM_E.th("Consistency Rationale")))
            self.handle_consistency_rows(base, sos_des, table)
        self.handle_content(base.find("./cc:con-op-en", generic_pp_doc.NS), out)
        soes = self.rfa("//cc:SOE")
        if len(soes)>0:
            p_el = adopt(out, HTM_E.p("The objectives for the TOE's OE are consistent with the "))
            edoc.make_xref_edoc(p_el)
            self.add_text(p_el, " based on the following rationale:")
            table = adopt(out, HTM_E.table())
            table.append(HTM_E.tr(HTM_E.th("PP-Module OE Objective"), HTM_E.th("Consistency Rationale")))
            self.handle_consistency_rows(base,soes, table)
        self.end_section()

        
    def base_consistency_rationale(self, out, base):
        """
        Writes out sections for "Consistency Rationale" section for a base.
        
        :param  out: The root of the HTML output ElementTree node
        :param  base: The edoc of the base document.
        """
        id   = base.attrib["id"]
        edoc = self.bases[id]
        self.set_shortcut(edoc.get_orig_node())
        out.append(self.sec({"id":"conrat-"+id}, edoc.short))
        self.consistency_of_toe_type(out, base, id)
        self.consistency_of_security_problem_def(out, base, id)
        self.consistency_of_objectives(out,base,id, edoc)
        self.consistency_of_requirements(out,base,id, edoc)
        self.end_section()

    def consistency_rationale(self, out):
        """
        Writes out the "Consistency Rationale" section.
        :param  out: The root of the HTML output ElementTree node
        """
        out.append(self.sec({"id":"mod-conrat"},"Consistency Rationale"))
        bases = self.rfa("//cc:base-pp")
        for base in bases:
            self.base_consistency_rationale(out, base)
        self.end_section()

    def template_module(self, out):
        """
        Writes out a PP Module to a formal document.
        
        :param  out: The root of the HTML output ElementTree node
        """
        self.apply_templates(self.rx("//*[@title='Introduction']|sec:Introduction"),out)
        self.apply_templates(self.rx("//*[@title='Conformance Claims']|sec:Conformance_Claims"),out)
        self.apply_templates(self.rx("//*[@title='Security Problem Description']|sec:Security_Problem_Description"),out)
        self.apply_templates(self.rx("//*[@title='Security Objectives']|sec:Security_Objectives"),out)
        self.apply_templates(self.rx("//*[@title='Security Requirements']|sec:Security_Requirements"),out)
        self.consistency_rationale(out)
        self.start_appendixes()
        self.handle_optional_requirements(out)
        self.handle_selection_based_requirements(out)
        self.handle_ext_comp_defs(out)
        self.apply_templates(self.rfa("//cc:appendix"), out)
        self.create_acronym_listing(out)
        self.create_bibliography(out)


    def sd_sars(self, out):
        """
        Writes out a sars section for a Support Document

        :param  out: The root of the HTML output ElementTree node
        """
        out.append(self.sec({"id":"eas_for_sars-"}, "Evaluation Activities for SARs"))
        pp = adopt(out, HTM_E.p("The PP-Module does not define any SARs beyond those defined within the "))
        if len(self.bases)==1:
            for base_id in self.bases:
                base = self.bases[base_id]
            self.add_text(pp ,"base ")
            base.make_xref_edoc(pp)
            # <x:apply-templates mode="short" select="//cc:base-pp"/>
            self.add_text(pp," to which it must claim conformance.  ")
            self.add_text(pp,"It is important to note that a TOE that is evaluated against the PP-Module is ")
            self.add_text(pp,"inherently evaluated against this Base-PP as well.  ")
            self.add_text(pp,"The  ")
            base.make_xref_edoc(pp)
            self.add_text(pp," includes a number of Evaluation Activities associated with both SFRs and SARs. ")
            self.add_text(pp,"Additionally, the PP-Module includes a number of SFR-based Evaluation Activities  ")
            self.add_text(pp,"that similarly refine the SARs of the Base-PPs. ")
            self.add_text(pp,"The evaluation laboratory will evaluate the TOE against the Base-PP ")
        else:
            self.add_text(pp,"base-PP to which it must claim conformance. ")
            self.add_text(pp,"It is important to note that a TOE that is evaluated against the PP-Module is ")
            self.add_text(pp,"inherently evaluated against the Base-PP as well. ")
            self.add_text(pp,"The Base-PP includes a number of Evaluation Activities associated with both SFRs and SARs. ")
            self.add_text(pp,"Additionally, the PP-Module includes a number of SFR-based Evaluation Activities  ")
            self.add_text(pp,"that similarly refine the SARs of the Base-PPs. ")
            self.add_text(pp,"The evaluation laboratory will evaluate the TOE against the chosen Base-PP ")

        self.add_text(pp,"and supplement that evaluation with the necessary SFRs that are taken from the PP-Module. ")
        self.end_section()
        
        
    def doctype(self):
        """
        Gets a string version of this type of document.
        :returns "PP-Module"
        """
        return "PP-Module"

    def handle_section_hook_base(self, title, node, out):
        """
        Insert boilerplates into sections.

        :param  title: The effective title of the section
        :param  node: The ElementTree of the section being added
        :param  out: The root of the HTML output ElementTree node
        """
        if title=="Security Functional Requirements":
            self.template_sfrs(out)
        elif title=="Organizational Security Policies":
            out.append(HTM_E.p("An organization deploying the TOE is expected to satisfy the organizational security policy listed below in addition to all organizational security policies defined by the claimed Base-PP."))
        elif title=="Security Requirements":
            out.append(generic_pp_doc.get_convention_explainer())
        else:
            super().handle_section_hook_base(title,node ,out)

    def handle_post_section_hook(self, title, node, out):
        """
        Insert boilerplates into the end of sections.

        :param  title: The effective title of the section
        :param  node: The ElementTree of the section being added
        :param  out: The root of the HTML output ElementTree node
        """
        if title=="Security Requirements":
            self.objectives_to_requirements(out)
        else:
            super().handle_post_section_hook(title,node ,out)


    def write_base_intro(self, out):
        """
        Writes out the intro section of the base.

        :param  out: The root of the HTML output ElementTree node
        """
        if len(self.bases)==1:
            maybe_s = ""
        else:
            maybe_s = s
        wurds= "The PP-Module is intended for use with the following Base-PP"+maybe_s+":"
        out.append(HTM_E.p(wurds))
        ul_el = adopt(out, HTM_E.ul())
        for base_id in self.bases:
            base = self.bases[base_id]
            li_el = adopt(ul_el, HTM_E.li())
            base.make_xref_edoc(li_el)
        wurds="""This SD is mandatory for evaluations of TOEs that claim conformance to a 
PP-Configuration that includes the PP-Module for :"""
        out.append(HTM_E.p(wurds))
        products = self.derive_plural()
        version = edoc.derive_version_and_date(self.root)[0]
        out.append(HTM_E.ul(HTM_E.li(products+", Version "+version)))
        out.append(HTM_E.p("""As such it defines Evaluation Activities for the functionality described in
 the PP-Module as well as any impacts to the Evaluation Activities to the Base-PP(s) it modifies."""))
        return
        
    def doctype_short(self):
        """
        Gets a string version of the type of document.

        :returns "PP-Mod"
        """
        return "PP-Mod"


        
            
