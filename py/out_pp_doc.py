import lxml.etree as ET
# Ours
import css_content
import pp_util
import edoc

HTM_E=pp_util.get_HTM_E()

def make_main_doc(doc, boilerplate):
    return out_pp_doc(boilerplate).to_html(doc)


def wrap_body_in_html(title, extra_css, body):
    head = HTM_E.head(
            HTM_E.meta({"content":"text/html;charset=utf-8", "http-equiv":"Content-Type"}),
            HTM_E.meta({"content":"utf-8","http-equiv":"encoding"}),
            HTM_E.title(title)
    )
    ret = HTM_E.html(head)
    pp_util.add_js(head)
    css_text = css_content.fx_pp_css()
    style=HTM_E.style({"type":"text/css"},css_text + extra_css)
    head.append(style)
    ret.append(body)
    return ret 



class out_pp_doc(object):
    def __init__(self, boilerplate):
        # Holds the things that need a counter
        self.globaltags = {}
        self.boilerplate = boilerplate
        self.test_titles={}
        self.are_sfrs_mingled = False
        self.node_to_ccid={}
        self.group_audit_map={}
        self.discoverables_to_ids = {}        # List of terms we're looking for
        #        self.test_number_stack = [0]
        self.counters={}
        # Keeping: tuple( target_node, output anchor, element , 
        self.broken_refs=set()
    


    def to_html(self, doc):
        self.doc = doc
        doc_html = self.start()
        # self.fix_numbered_xrefs(doc_html)
        # self.add_discoverable_xrefs(doc_html)
        # convert_none_text_to_emptys(doc_html)
        # return doc_html
        return doc_html


    
    def handle_comments(self, body):
        comments_els = self.doc.rfa("//cc:comment")
        if not comments_els:
            return
        div=HTM_E.div({"id":"commentbox-"})
        ctr=0
        for comment_el in comment_els:
            id=self.doc.derive_id(comment_el)
            div.append(HTM_E.a({"href":"#"+id},"Comment: " + id))
            div.append(HTM_E.br())
        return ret

    
    def fx_body_begin(self, body):
        self.handle_comments(body)
        body.append(HTM_E.h1({"class":"title", "style":"page-break-before:auto;"}, self.title()))
        body.append(HTM_E.noscript(HTM_E.h1, {"style":"text-align:center; border-style: dashed; border-width: medium; border-color: red;"},"This page is best viewed with JavaScript enabled!"))
              
        body.append(self.make_logo())
        self.apply_templates(self.rfa("//cc:foreword"), body)
        body.append(HTM_E.h2("Revision History"))
        self.write_revision_history(body)
        body.append(HTM_E.h2("Contents"))
        self.toc = adopt(body, (HTM_E.div({"class":"toc","id":"toc"})))
        return 

    
    def start(self):
        self.outline = [0]
        self.is_appendix = False
        body=HTM_E.body({"onload":"init()"})
        title = self.doc.title()
        self.fx_body_begin(body, title)
        # # self.apply_templates([self.root], body)
        extra_css = self.doc.get_text_or("//cc:extra-css")
        html_el = wrap_body_in_html(title, extra_css, body)        
        return html_el

        

    def make_logo(self):
        version_date = edoc.derive_version_and_date(self.doc.root)
        return HTM_E.div({"class":"center"},
                         HTM_E.img({"src":"images/niaplogo.png","alt":"NIAP Logo"}),
                         HTM_E.br(),
                         "Version: "+version_date[0],
                         HTM_E.br(),
                         "     "+version_date[1],
                         HTM_E.br(),
                         HTM_E.b(self.doc.derive_author()),
                         HTM_E.br())    


        


    def handle_comments(self, body):
        comments_els = self.doc.rfa("//cc:comment")
        if not comments_els:
            return
        div=HTM_E.div({"id":"commentbox-"})
        ctr=0
        for comment_el in comment_els:
            id=self.doc.derive_id(comment_el)
            div.append(HTM_E.a({"href":"#"+id},"Comment: " + id))
            div.append(HTM_E.br())
        return ret

        
    def fx_body_begin(self, body, title):
        self.handle_comments(body)
        body.append(HTM_E.h1({"class":"title", "style":"page-break-before:auto;"}, title))
        body.append(HTM_E.noscript(HTM_E.h1, {"style":"text-align:center; border-style: dashed; border-width: medium; border-color: red;"},"This page is best viewed with JavaScript enabled!"))
              
        body.append(self.make_logo())
        self.apply_templates(self.rfa("//cc:foreword"), body)
        body.append(HTM_E.h2("Revision History"))
        self.write_revision_history(body)
        body.append(HTM_E.h2("Contents"))
        self.toc = adopt(body, (HTM_E.div({"class":"toc","id":"toc"})))
        return 




    def maybe_make_usecase_appendixes(self, out):
        usecases_with_config = self.rfa("//cc:usecase/cc:config")
        if len(usecases_with_config)==0:
            return
        usecases = self.rfa("//cc:usecase")
        out.append(self.sec("Use Case Templates", {"id":"Use_Case_Templates-"}))
        for usecase in usecases:
            uc_id = usecase.attrib["id"]
            out.append(self.sec({"id":"app-"+uc_id+"-"}, usecase.attrib["title"]))
            config_in = usecase.find("./cc:config", NS)
            if config_in is None:
                self.add_text(out, "The use case ")
                self.make_xref(uc_id, out)
                self.add_text(out," makes no changes to the base requirements.")
            else:
                self.add_text(out, "The configuration for ")
                self.make_xref(uc_id, out)
                self.add_text(out," modifies the base requirements as follows:")
                out_div = adopt(out, HTM_E.div())
                self.apply_use_case_templates(config_in, out_div)
            self.end_section()
        self.end_section()
        


        
    def get_next_counter(self, ctr_type):
        print("Counter type is " + ctr_type)
        if ctr_type in self.counters:
            self.counters[ctr_type]+=1
            return self.counters[ctr_type]
        else:
            self.counters[ctr_type]=1
            return 1

                
    def get_all_abbr_els(self):
        return self.rfa("//cc:term[@abbr]")+\
            self.boilerplate.findall("//cc:cc-terms/cc:term[@abbr]", NS)

    def register_threats_assumptions_objectives_policies(self):
        for aa in self.rfa("//cc:threat")+self.rfa("//cc:assumption")+self.rfa("//cc:SO")+self.rfa("//cc:SOE")+self.rfa("//cc:OSP"):
            if aa.find("cc:description", NS) is not None:
                ccname = aa.attrib["name"]
                self.register_keyterm(ccname, ccname)

    def add_text(self, node, text):
        pp_util.append_text(node,text)


    
    def handle_unknown_depends(self, sfr, attr):
        raise Exception("Can't handle this dependent sfr:"+sfr.attrib["cc-id"])


    def is_non_xrefable_section(self, node):
        if node.tag == "a"    or node.tag == "abbr"    or\
           node.tag == "dt"   or node.tag == "no-link" or\
           node.tag == "h1"   or node.tag == "h2"      or\
           node.tag == "h3"   or node.tag == "h4"      or\
           node.tag == "head" or node.tag == "script"  or\
           node.tag == "svg"  or node.tag == "th": 
            return True
        if "class" in node.attrib and node.attrib["class"]:
            classes = node.attrib["class"].split(" ")
            if "term" in classes:
                return True
        return False

    def make_disco_link(self, id, matchtext):
        attrs={"class":"discovered", "href":"#"+id}
        if matchtext in self.abbrs:
            attrs["class"]="discovered abbr"
            attrs["title"]=self.abbrs[matchtext]
        return HTM_E.a(attrs, matchtext)
    
    def xrefs_in_text(self, node, content, regex, insertspot=0):
        # Returns what should go in the node's text field
        if regex is None or content is None:
            return content
        matches = regex.finditer(content)
        try:
            match=next(matches)
        except:
            return content
        origtext = content
        ret = origtext[:match.start()]
        last=match.end()
        matchtext = match.group()
        id = self.discoverables_to_ids[matchtext]
        
        prevnode = self.make_disco_link(id, matchtext)
        newnodes=[prevnode]
        for match in matches:
            prevnode.tail = origtext[last:match.start()]
            last = match.end()
            id = self.discoverables_to_ids[match.group()]
            prevnode = self.make_disco_link(id, match.group())
            newnodes.append(prevnode)
        prevnode.tail = origtext[match.end():]
        for newkids in newnodes:
            node.insert(insertspot, newkids)
            insertspot+=1
        return ret
            
    def add_xrefs_recur(self, node, regex):
        if self.is_non_xrefable_section(node):
            return
        origchildren = node.iterchildren()
        node.text = self.xrefs_in_text(node, node.text, regex)
        for child in origchildren:
            self.add_xrefs_recur(child, regex)
            insertspot=node.index(child)+1
            child.tail = self.xrefs_in_text(node, child.tail, regex, insertspot)


    
    def meta_data(self, parent):
        div = HTM_E.div(
            {"style":"text-align: center; margin-left: auto; margin-right: auto;"},
            HTM_E.h1({"class":"title","style":"page-break-before:auto;"},"Supporting Document",HTM_E.br(), "Mandatory Technical Document"),
            HTM_E.img({"src":"images/niaplogo.png","alt":"NIAP"}),
            HTM_E.hr({"width":"50%"}),
            HTM_E.noscript(HTM_E.h1({"style":"text-align:center; border-style: dashed; border-width: medium; border-color: red;"},"This page is best viewed with JavaScript enabled!")),HTM_E.br())
        self.add_text(div, self.title())
        div.append(HTM_E.br())
        version_date = edoc.derive_version_and_date(self.root)
        pp_util.append_text(div, "Version: "+version_date[0])
        div.append(HTM_E.br())
        pp_util.append_text(div, version_date[1])
        div.append(HTM_E.br())
        div.append(HTM_E.b(self.derive_author()))
        parent.append(div)


    def write_forward(self, out):
        div = HTM_E.div(attrs("foreword"))
        div.append(HTM_E.h1({"style":"text-align: center"},"Foreword"))
        div.append(HTM_E.p("""This is a Supporting Document (SD), intended to complement
 the Common Criteria version 3 and the associated Common Evaluation Methodology for
 Information Technology Security Evaluation."""))
        div.append(HTM_E.p("""SDs may be “Guidance Documents”, that highlight specific approaches
 and application of the standard to areas where no mutual recognition of
 its application is required, and as such, are not of normative nature, 
 or “Mandatory Technical Documents”, whose application is mandatory for evaluations 
 whose scope is covered by that of the SD.
 The usage of the latter class is not only mandatory, but certificates
 issued as a result of their application are recognized under the CCRA."""))
        div.append(HTM_E.p(HTM_E.b("Technical Editor:"),HTM_E.br(),"National Information Assurance Partnership (NIAP)"))
        rev_his = HTM_E.div({"style":"page-break-before:always;"},HTM_E.b("Revision History:"))
        self.write_revision_history(rev_his)
        div.append(rev_his)

        wurds = "The purpose of this SD is to define evaluation methods for the functional behavior of "+                      edoc.derive_product(self.root)+  " products."                   
        p_genpurp = HTM_E.p(HTM_E.b("General Purpose:"), HTM_E.br(),wurds)
        div.append(p_genpurp)

        wurds = "This SD was developed with support from NIAP "+\
            edoc.derive_products(self.root) +\
            " Technical Community members, with representatives from "+\
            "industry, government agencies, Common Criteria Test Laboratories"+\
            ", and members of academia."
        p_ack = HTM_E.p(HTM_E.b("Acknowledgments:"), HTM_E.br(), wurds)
        div.append(p_ack)
        out.append(div)


    def write_base_intro(self, out):
        return

            
    def add_discoverable_xrefs(self, node):
        if len(self.discoverables_to_ids)==0:
            return
        keys = sorted(self.discoverables_to_ids.keys(), key=len, reverse=True)
        bracketed=set()
        for key in keys:
            if key[0]=='[':
                keys.remove(key)
                bracketed.add(key)
        biblio_part=""
        if len(bracketed)>0:
            biblio_part = "("+"|".join(map(backslashify,bracketed))+")|"
        regex_str = biblio_part+"(?<!-)\\b("+"|".join(map(backslashify, keys))+")\\b"
        regex = re.compile(regex_str)
        self.add_xrefs_recur(node, regex)        

    def fix_numbered_xrefs(self, doc):
        for broken_ref in self.broken_refs:
            self.fix_xref(doc, broken_ref[0], broken_ref[1], broken_ref[2])

    def fix_xref(self, doc, refid, link, ref):
#        refid=self.derive_id(orig)
        # print("Fixing " + refid)
        link.attrib["href"]="#"+refid
        reffed = doc.find(".//*[@id='"+refid+"']")
        if reffed is None:
            print("Could not find dynamic reference: " + refid)
            return
        label_node = reffed.find("./*[@class='dynid_']")
        if label_node is None:
            text = pp_util.flatten(reffed)
        else:
            text = pp_util.flatten(label_node)
        pp_util.append_text(link,text)
#        pp_util.append_text(link, " "+text)

            #     dynrefs = doc.xpath(".//*[contains(@class,'dynref')]")
    #     for dynref in dynrefs:
    #         refid = dynref.attrib["href"][1:]
    #         # print("Looking for " + refid)

    # def fix_broken_refs(self, doc):
            
    def to_html(self):
        doc = self.start()
        self.fix_numbered_xrefs(doc)
        self.add_discoverable_xrefs(doc)
        convert_none_text_to_emptys(doc)
        return doc
    
    def rf(self, findexp):
        return self.doc.rf(findexp)
    
    def rfa(self, findexp):
        return self.doc.rfa(findexp)

    def rx(self, xpath):
        return self.doc.rx(xpath)

    def maybe_register_sfr_with_fam(self, sfr):
        if sfr.find("cc:comp-lev",NS) is None:
            return
        if sfr.find("cc:notnew", NS) is not None:
            return
        fam = sfr.attrib["cc-id"].split(".")[0]
        if fam not in self.fams_to_sfrs:
            self.fams_to_sfrs[fam]=[]
        self.fams_to_sfrs[fam].append(sfr)


    
    def sec(self, *args):
        return sec_impl(self.outline, self.is_appendix, self.toc, HTM_E.h2(*args))
        
    def end_section(self):
        if len(self.outline)==0:
            print("Popping from zero.")
        else:
            self.outline.pop()


    def objectives_to_requirements(self, par):
        addr_bys = self.rx("//cc:SO/cc:addressed-by")
        if len(addr_bys)==0:
            return
        par.append(self.sec({"id":"obj-req-map-"}, "TOE Security Functional Requirements Rationale"))
        par.append(HTM_E.p("""The following rationale provides justification for each 
 security objective for the TOE, showing that the SFRs are suitable to meet and
 achieve the security objectives:"""))
        table=adopt(par,HTM_E.table())
        caption=adopt(table,HTM_E.caption())
        self.create_ctr("Table", "t-obj-map", caption, "Table ")
        self.add_text(caption, "SFR Rationale")
        table.append(HTM_E.tr( HTM_E.th("Objective"), HTM_E.th("Addressed by"), HTM_E.th("Rationale")))
        prev_parent = None
        for addr_by in addr_bys:
            curr_parent=addr_by.find("..")
            if prev_parent!=curr_parent:
                tr = adopt(table, HTM_E.tr({"class":"major-row"}))
                rowspan=str(len(curr_parent.findall("cc:addressed-by", NS)))
                content=pp_util.make_wrappable(curr_parent.attrib["name"])
                tr.append(HTM_E.td({"rowspan":rowspan}, content))
                prev_parent=curr_parent
            else:
                tr = adopt(table, HTM_E.tr())
            td = adopt(tr, HTM_E.td())
            self.handle_content(addr_by, td)
            td = adopt(tr, HTM_E.td())
            rational=addr_by.xpath("following-sibling::cc:rationale[1]",namespaces=NS)
            self.handle_content(rational[0], td)
        self.end_section()


    def handle_figure(self, el, par):
        id=el.attrib["id"]
        div=adopt(par, HTM_E.div({"class":"figure","id":"div_fig_"+id}))
        attrs={"id":"fig_"+id, "src":el.attrib["entity"]}
        div.append(HTM_E.img(attrs))
        div.append(HTM_E.br())
        self.create_ctr("figure", id, div, "Figure ")
        self.add_text(div, el.attrib["title"])



    def write_revision_history(self, body):
        table = HTM_E.table(HTM_E.tr({"class":"header"},
                                     HTM_E.th("Version"),
                                     HTM_E.th("Date"),
                                     HTM_E.th("Comment")))
        for entry in self.rfa("//cc:RevisionHistory/cc:entry"):
            tr=HTM_E.tr()
            for abc in ["version", "date", "subject"]:
                td = HTM_E.td()
                self.handle_content(entry.find("cc:"+abc,NS), td)
                tr.append(td)
            table.append(tr)
        body.append(table)
    

                
    def handle_content(self, node, out,defcon=""):
        if node is None:
            self.add_text(out, defcon)
            return False
        if node.text is None and len(node)==0:
            return False
        self.add_text(out, node.text)
        for child in node:
            self.apply_templates_single(child,out)
            self.add_text(out,child.tail)
        return True
            
    def handle_section(self, node, title, id, parent):
        title_el = self.sec({"id":id},title)
        parent.append(title_el)
        self.handle_section_hook(title, node, parent)
        self.handle_content(node, parent)
        self.handle_post_section_hook(title, node, parent)
        self.end_section()

    def handle_post_section_hook(self, title, node, parent):
        pass
        
    def handle_section_hook(self, title, node, parent):
        if "boilerplate" in node.attrib and node.attrib["boilerplate"]=="no":
            return 
        self.handle_section_hook_base(title, node, parent)

    def handle_conformance_claims(self, node, parent):
        dl=HTM_E.dl()
        parent.append(dl)
        dl.append(HTM_E.dt("Conformance Statement"))
        self.handle_conformance_statement(dl)
        # dd = HTM_E.dd()
        # dl.append(dd)
        bases = self.rfa("//cc:base-pp")
        if len(bases)>0:
            dd.append(HTM_E.p("This "+self.doctype()+" inherits exact conformance as required "+\
                              "from the specified Base-PP and as defined in the CC and CEM "+\
                              "addenda for Exact Conformance, Selection-based "+
                              "SFRs, and Optional SFRs (dated May 2017)."))
            dd.append(HTM_E.p("The following PPs and PP-Modules are allowed to be specified in a "+\
            "PP-Configuration with this "+self.doctype()+"."))
            ul=adopt(dd, HTM_E.ul())
            for base in bases:
                li=adopt(ul, HTM_E.li())
                self.make_xref(base,li)
        dl.append(HTM_E.dt("CC Conformance Claims"))
        dl.append(HTM_E.dd("This "+self.doctype()+" is conformant to Parts 2 (extended) and 3 (conformant) of Common Criteria "+pp_util.ccver()+"."))
        dl.append(HTM_E.dt("PP Claim"))
        dl.append(HTM_E.dd("This "+self.doctype()+" does not claim conformance to any Protection Profile."))
        dl.append(HTM_E.dt("Package Claim"))
        dd = adopt(dl, HTM_E.dd())
        dd.text="This "+self.doctype()+" "
        pks = self.rfa("//cc:include-pkg")
        ctr=len(pks)
        if ctr == 0:
            self.add_text(dd, "does not claim conformance to any packages")
        else:
            lagsep=""
            for pk in pks:
                ctr=ctr-1
                self.add_text(dd, lagsep)
                lagsep=","
                if ctr==2 :
                    lagsep="and"
                self.make_xref_edoc(pk, dd)
            self.add_text("conformant")
        self.add_text(dd,".")


        
    def handle_section_hook_base(self, title, node, parent):
        if title=="Conformance Claims":
            self.handle_conformance_claims(node, parent)
        elif title=="Implicity Satisfied Requirements":
            self.handle_implicitly_satisfied_requirements(parent)
        elif title=="Security Objectives Rationale":
            self.handle_security_objectives_rationale(node, parent)
        elif title=="Security Objectives for the Operational Environment":
            self.handle_security_objectives_operational_environment(parent)
        elif title=="Assumptions":
            self.add_text(parent, "These assumptions are made on the Operational Environment (OE) in order to be able to ensure that the security functionality specified in the "+self.doctype_short()+" can be provided by the TOE. If the TOE is placed in an OE that does not meet these assumptions, the TOE may no longer be able to provide all of its security functionality.")
        elif title=="Validation Guidelines":
            self.handle_rules_appendix(parent) 

    
    def make_ecd_table(self, par, ecdsecs):
        par.append(self.sec({"id":"ext-comp-defs-bg-"},"Extended Components Table"))
        self.add_text(par,"All extended components specified in the "+self.doctype()+" are listed in this table:")
        par.append(HTM_E.br())
        # b_el = adopt(par, HTM_E.div({"class":"table_caption"}))
        table = adopt(par, HTM_E.table({"class":"sort_kids_"}))
        caption = adopt(table, HTM_E.caption())
        self.create_ctr("Table","t-ext-comp_map-", caption, "Table ")
        self.add_text(caption, "Extended Component Definitions")
        table.append(HTM_E.tr({"data-sortkey":"#1"},
                              HTM_E.th("Functional Class"),
                              HTM_E.th("Functional Components")))
        
        # <!-- section is compatible with the new section styles b/c the new section style is not allowed to 
        #      for sections that directly contain f-components and a-components -->
        defsec = HTM_E.div()
        last=""
        for sec in ecdsecs:
            title = sec.attrib["title"]
            if title == last:
                continue
            last = title
            # Old style and new style both need to use @title b/c the presence of parenthesis
            ecds=self.rx("//*[@title='"+title+"']/cc:ext-comp-def")
            add_grouping_row(table, title, len(ecds))
            for ecd in ecds:
                table.append(HTM_E.tr( HTM_E.td(ecd.attrib["fam-id"]+ " - " + ecd.attrib["title"])))
        self.end_section()

    
    
    def handle_ext_comp_defs(self ,par):
        if self.rf("//cc:ext-comp-def") is None:
            return ""
        par.append(self.sec({"id":"ext-comp-defs"},"Extended Component Definitions"))
        self.add_text(par, "This appendix contains the definitions for all extended requirements specified in the " + self.doctype()+".\n")

        ecdsecs = self.rx("//*[cc:ext-comp-def]")
        ecdsecs.sort(key=lambda sec: sec.attrib["title"])
        self.make_ecd_table(par, ecdsecs)
        
        par.append(self.sec({"id":"ext-comp-defs-bg"}, "Extended Component Definitions"))
        last = ""
        for sec in ecdsecs:
            title = sec.attrib["title"]
            if title == last:
                continue
            last = title
            ecds=self.rx("//*[@title='"+title+"']/cc:ext-comp-def")
            classid = sec.attrib["title"].split(")")[0].split("(")[1]
            span=adopt(par, HTM_E.span({"data-sortkey":sec.attrib["title"]}))
            span.append(self.sec({"id":"ext-comp-"+classid},sec.attrib["title"]))
            self.add_text(span, "This "+self.doctype() +\
                          " defines the following extended components as part of the "+\
                          classid + " class originally defined by CC Part 2:" )

            for ecd in ecds:
                self.handle_ecd(ecd, classid, span)
            self.end_section()
        self.end_section()
        self.end_section()
        
    def handle_ecd(self, famnode, classid, span):
        famId = famnode.attrib["fam-id"]
        desc = famnode.find("cc:class-description",NS)
        self.handle_content(desc, span)
        span.append(self.sec({"id":"ecd-"+famId}, famId+" "+famnode.attrib["title"]))

        div = adopt(span, HTM_E.div())
        # div = adopt(span, HTM_E.div({"style":"margin-left: 1em;"}))
        famBi = famnode.find("cc:fam-behavior",NS)
        if famBi is not None:
            div.append(HTM_E.h4("Family Behavior"))
            div_fam = adopt(div, HTM_E.div())
            self.handle_content(famBi, div_fam)
            sfrs = self.fams_to_sfrs[famId.lower()]
            sfrs.sort(key=lambda fcom: make_sort_key_stringnum(fcom.attrib["cc-id"]))
            div_fam.append(HTM_E.h4("Component Leveling"))
            svg_el=SVG_E.svg(style="max-height: "+str(20*len(sfrs)+10)+"px;")
            drawbox(svg_el, 20*math.floor(len(sfrs)/2), famId, 0)
            ctr=0
            complevel_text=HTM_E.div()
            sfr_mng_aud_text=HTM_E.div()
            for sfr in sfrs:
                cc_id = self.fcomp_cc_id(sfr)
                text = cc_id.split(".")[1]
                drawbox(svg_el, ctr*20, text, 20*math.floor(len(sfrs)/2), xbase=230 )
                ctr+=1
                p_el = adopt(complevel_text, HTM_E.p(cc_id+", " + sfr.attrib["name"]+", "))
                self.handle_content(sfr.find("cc:comp-lev",NS),p_el)
                self.get_mng_aud(sfr, cc_id, sfr_mng_aud_text)
            div_fam.append(svg_el)
            div_fam.append(complevel_text)
            div_fam.append(sfr_mng_aud_text)
        else:
            self.handle_content(famnode.find("cc:mod-def",NS), div)
        self.end_section()
        
    def get_mng_aud(self, sfr, cc_id, par):
        par.append(HTM_E.h4("Management: "+cc_id))
        p_el = adopt(par, HTM_E.p())
        self.handle_content(sfr.find("cc:management",NS),p_el,
                            defcon="There are no management functions foreseen.")
        par.append(HTM_E.h4("Audit: "+cc_id))
        p_el = adopt(par, HTM_E.p())
        self.handle_content(sfr.find("cc:audit",NS),p_el,
                            defcon="There are no audit events foreseen.")
        par.append(HTM_E.h4(cc_id+" "+sfr.attrib["name"]))
        div = adopt(par, HTM_E.div({"style":"margin-left: 1em;"}))
        p_el = adopt(div, HTM_E.p("Hierarchical to: "))
        self.handle_content(sfr.find("cc:heirarchical-to",NS), p_el, defcon="No other components.")
        p_el = adopt(div, HTM_E.p("Dependencies to: "))
        self.handle_content(sfr.find("cc:dependencies",NS), p_el, defcon="No dependencies.")
        ctr=1
        for fel in sfr.findall("cc:f-element", NS):
            fel_id = self.get_ccid_for_ccel(fel)
            par.append(HTM_E.h4({"id":"ext-comp-"+fel_id+"-"},fel_id))
            ecd_title = fel.find("cc:ext-comp-def-title/cc:title",NS)
            if ecd_title is None:
                ecd_title=fel.find("cc:title",NS)
                if ecd_title is None:
                    raise Exception("Can't find title")
            self.handle_content(ecd_title, par)
            ctr+=1

    def start_appendixes(self):
        self.outline[0]=-1
        self.is_appendix = True

    def implementation_based_section(self, id, out):
        attrs={"id":id}
        out.append(self.sec(attrs, "Implementation-based Requirements"))
        features=self.rfa("//cc:feature")
        if len(features)==0:
            self.add_text(out, "This "+self.doctype_short()+" does not define any Implementation-based SFRs.\n")
        for feature in features:
            out.append(self.sec(feature.attrib["title"]))
            self.handle_content(feature,out)
            f_id=feature.attrib["id"]
            sfrs = self.rx(".//cc:f-component[./cc:depends/@*='"+f_id+"']")
            self.handle_sparse_sfrs(sfrs, out, "impl_sfrs")
            self.end_section()
        self.end_section()

    def add_optional_appendix_explainer(self, par, opt_id, obj_id, imple_id):
        pass

    def handle_sfr_section(self, sfrs, none_msg, audittype, title, out, idval):
        if len(sfrs)==0:
            self.add_text(out, none_msg)
        else:
            if audittype is not None:
                self.create_audit_table_section(title, audittype, out)
            self.handle_sparse_sfrs(sfrs, out, idval)

    # QQQQ
    def sfr_appendix(self,title,sfrs,preamble,audittype,idval,par):
        # attrset=attrs(None,title.replace(" ","-")+"-")
        attrset={"id":idval}
        par.append(self.sec(attrset,title+" Requirements"))
        self.add_text(par, preamble)
        none_msg = "This "+self.doctype_short()+" does not define any "+title+" SFRs.\n"
        self.handle_sfr_section(sfrs, none_msg, audittype, title, par, idval)
        self.end_section()

    def handle_optional_requirements(self, par):
        par.append(self.sec({"id":"optional-appendix-"},"Optional SFRs"))
        opt_title = "Strictly Optional"
        opt_id=opt_title.replace(" ","-")+"-"
        obj_title = "Objective"
        obj_id=obj_title.replace(" ","-")+"-"
        impl_id="implementation-based-"
        self.add_optional_appendix_explainer(par, opt_id, obj_id, impl_id)
        self.sfr_appendix(opt_title,    self.opt_sfrs , "","optional", opt_id,par)
        self.sfr_appendix("Objective",            self.obj_sfrs , "","objective", obj_id, par)
        self.implementation_based_section(impl_id, par)
        self.end_section()

    def create_audit_table_section(self, title, audittable, par):
        title_sfrs = self.get_title_n_sfrs(audittable)
        title = title_sfrs[0]
        sfrs  = title_sfrs[1]
        sfrs_event_map = self.get_sfrs_with_audit_events(sfrs, audittable)
        if len(sfrs_event_map)==0:
            return

        
        par.append(self.sec("Auditable Events for "+ title + " Requirements"))
        self.template_audit_table(None, par, audittable)
        self.end_section()
        
    def sel_appendix_preamble(self):
        DT=self.doctype()
        return "As indicated in the introduction to this "+DT+\
            ", the baseline requirements (those that must be performed by the TOE or its "+\
            "underlying platform) are contained in the body of this "+DT+\
            ". There are additional requirements based on selections in the body of "+\
            "the "+DT+": if certain selections are made, then additional "+\
            "requirements below must be included."
        
    def handle_selection_based_requirements(self, node, par):
        words=self.sel_appendix_preamble()
        return self.sfr_appendix("Selection-based", self.sel_sfrs, words,"sel-based","sel-based-", par)


    OE_PREAMBLE="""The OE of the TOE implements technical and procedural measure
to assist the TOE in correctly providing its security functionality
(which is defined by the security objectives for the TOE).
The security objectives for the OE consist of a set of statements
describing the goals that the OE should achieve.
This section defines the security objectives that are to be
addressed by the IT domain or by non-technical or procedural means.
The assumptions identified in Section 3 are incorporated as
security objectives for the environment.
"""
    
    def handle_security_objectives_operational_environment(self, parent):
        soes=self.rfa("//cc:SOE")
        if len(soes)>0:
            self.add_text(parent,generic_pp_doc.OE_PREAMBLE)
        else:
            self.add_text(parent, "This "+self.doctype()+" does not define any objectives for the OE.")

        
    def create_ctr(self, ctrtype, id ,parent, prefix, sep=": ", child=None):
        print("Creating counter for: " + id)
        ctrcount = str(self.get_next_counter(ctrtype))
        span = HTM_E.span({"class":"ctr",
                           "data-counter-type":"ct-"+ctrtype,
                           "id":id}, prefix,
                          HTM_E.span({"class":"counter"},ctrcount)
                          )
        parent.append(span)
        self.add_text(span, sep)
        self.handle_content(child, span)
        
    def handle_conformance_statement(self, node):
        node.append(HTM_E.dd("An ST must claim exact conformance to this "+self.doctype()+", as defined in the CC "+
                        "and CEM addenda for Exact Conformance, Selection-based SFRs, and Optional SFRs (dated May 2017)."))
        

        
    def create_bibliography(self, par):
        par.append(self.sec({"id":"appendix-bibliography"},"Bibliography"))
        table = adopt(par, HTM_E.table())
        table.append(HTM_E.tr(HTM_E.th("Identifier"),HTM_E.th("Title")))
        entries = (self.rfa("//cc:bibliography/cc:entry") +
                   self.boilerplate.xpath("//*[@id='cc-docs']/cc:entry",namespaces=NS))
        entries.sort(key=lambda x: pp_util.flatten(x.find("cc:description", NS)))
        for entry in entries:
            keyterm= "["+entry.find("cc:tag", NS).text+"]"
            entry_id = self.derive_id(entry)            
            self.register_keyterm(keyterm, entry_id)
            
            tr = adopt(table, HTM_E.tr())
            tr.append(HTM_E.td( HTM_E.span({"id":entry_id},keyterm)))

            td = adopt(tr, HTM_E.td())
            self.handle_content(entry.find("cc:description",NS), td)
        self.end_section()


            
    def create_acronym_listing(self, par):
        par.append(self.sec({"id":"acronyms"},"Acronyms"))
        table = adopt(par, HTM_E.table())
        table.append(HTM_E.tr(HTM_E.th("Acronym"), HTM_E.th("Meaning")))
        suppress_el=self.rf("//cc:suppress")
        if suppress_el is None or suppress_el.text is None:
            suppress_list=[]
        else:
            suppress_list=suppress_el.text.split(",")
        term_els = self.get_all_abbr_els()
        term_els.sort(key=lambda t_el:t_el.attrib["abbr"].upper())
        for term_el in term_els:
            full=term_el.attrib["full"]
            abbr=term_el.attrib["abbr"]            
            if full in suppress_list:
                continue
            tr = adopt(table, HTM_E.tr())

            attrs = {"class":"term", "id":"abbr_"+abbr}
            # pp_util.maybe_add_attr(attrs, term_el, "plural")
            # pp_util.maybe_add_attr(attrs, term_el, "lower")
            tr.append(HTM_E.td(HTM_E.span(attrs, abbr)))
            tr.append(HTM_E.td(HTM_E.span({"id":"long_abbr_"+abbr}, full)))
        self.end_section()
            
    def handle_security_objectives_rationale(self, node, parent):
        self.add_text(parent, """This section describes how the assumptions, threats, and organizational 
security policies map to the security objectives.""")
        table = adopt(parent, HTM_E.table())
        caption = adopt(table, HTM_E.caption())
        self.create_ctr("Table","t-sec-obj-rat-", caption, "Table ")
        self.add_text(caption, "Security Objectives Rationale")
        tr = adopt(table, HTM_E.tr({"class":"header"}))
        tr.append(HTM_E.td("Threat, Assumption, or OSP"))
        tr.append(HTM_E.td("Security Objectives"))
        tr.append(HTM_E.td("Rationale"))
        objrefers=self.rx("//cc:threat/cc:objective-refer | //cc:OSP/cc:objective-refer | //cc:assumption/cc:objective-refer")
        firstcol=""
        for objrefer in objrefers:
            parent = objrefer.find("..")
            pname = parent.attrib["name"]
            attrs={}
            if pname != firstcol:
                tr = adopt(table, HTM_E.tr({"class":"major-row"}))
                firstcol=pname
                numkids = len(parent.findall("cc:objective-refer", NS))
                pname_wrap = pp_util.make_wrappable(pname)
                from_el = parent.find("cc:from", NS)
                if not from_el is None:
                    pname_wrap+=" (from "+from_el.attrib["base"]+")"
                tr.append(HTM_E.td({"rowspan":str(numkids)},pname_wrap))
            else:
                tr = adopt(table,HTM_E.tr())
            adopt(tr, HTM_E.td(pp_util.make_wrappable(objrefer.attrib["ref"])))
            td = adopt(tr,HTM_E.td())
            self.handle_content(objrefer.find("cc:rationale",NS), td)

        
    def handle_implicitly_satisfied_requirements(self):
       ret="<p>This appendix lists requirements that should be considered satisfied by products\n"
       ret+="successfully evaluated against this "+self.doctype_short()+". These requirements are not featured\n"
       ret+="explicitly as SFRs and should not be included in the ST. They are not included as \n"
       ret+="standalone SFRs because it would increase the time, cost, and complexity of evaluation.\n"
       ret+="This approach is permitted by <a href=\"#bibCC\">[CC]</a> Part 1, 8.2 Dependencies between components.</p>\n"
       ret+="<p>This information benefits systems engineering activities which call for inclusion of particular\n"
       ret+="security controls. Evaluation against the "+self.doctype_short()+" provides evidence that these controls are present \n"
       ret+="and have been evaluated.</p>\n"
       return ret
       
        
    def template_assumptions_cclaims_threats_OSPs_SOs_SOEs(self, node, parent):
        defs = node.findall("cc:*[cc:description]", NS)
        if len(defs)>0:
            dl = adopt(parent, HTM_E.dl())
            for defined in defs:
                classtype=pp_util.localtag(defined.tag)
                name= defined.attrib["name"]
                dl.append(HTM_E.dt({"class":classtype+" defined","id":name}, name))
                dd = adopt(dl, HTM_E.dd())
                self.apply_templates(defined.findall("./cc:description",NS), dd)
                self.apply_templates(defined.findall("./cc:appnote",NS), dd)
        else:
            self.add_text(parent, "This document does not define any additional " + pp_util.localtag(node.tag))
            
        
    def template_xref(self, node, parent):
        attrs = {}
        if "to" in node.attrib:
            to=node.attrib["to"]
        else:
            to=node.attrib["g"]
            if to=='CC':
                parent.append(HTM_E.a({'href':'#bibCC'},"[CC]"))
                return
        if "format" in node.attrib:
            attrs["data-post"]=node.attrib["format"]
        refs = self.rx(".//cc:*[@id='"+to+"']|.//sec:*[local-name()='"+to+"']")
        if len(refs)==0:
            pp_util.log("Failed to find a reference to "+to)
            parent.append( HTM_E.a(attrs))
            return 
        elif len(refs)>1:
            pp_util.log("Found multipled targets for "+ to)
        self.make_xref(refs[0], parent, node)

        
    def get_list_of(self, fulltag):
        if fulltag in self.globaltags:
            return self.globaltags[fulltag]
        nodes = self.root.findall(".//"+fulltag)
        self.globaltags[fulltag] = nodes
        return nodes


    
    def get_global_index(self, node):
        allof = self.get_list_of(node.tag)
        return allof.index(node)+1

        
    def get_section_title(self, node):
        if "title" in node.attrib:
            return node.attrib["title"]
        return node.tag.split("}")[1].replace("_", " ")
    
    def template_oldsection(self, node, parent):
        if "id" in node.attrib:
            id=node.attrib["id"]
        else:
            id="sec_"+str(get_global_index(node))+"-"
        return self.handle_section(node,node.attrib["title"],id ,parent)
        
    def template_newsection(self, node, parent):
        id = pp_util.localtag(node.tag)
        title = pp_util.get_attr_or(node, "title", id.replace("_", " "))
        return self.handle_section(node, title, id, parent)

    def make_term_table(self, term_els, parent, ignores=""):
        terms=[]
        termdic={}
        for termdef in term_els:
            term = termdef.attrib["full"]
            if (","+ term +",") in ignores:
                continue
            uppered = term.upper()
            terms.append(uppered)
            termdic[uppered]=termdef
        terms.sort()
        for term in terms:
            self.template_glossary_entry(termdic[term], parent)
        
    def template_tech_terms(self, node, parent):
        divy = HTM_E.div({"class":"no-link"})
        parent.append(divy)
        divy.append(self.sec({"id":"glossary"}, "Terms"))
        self.add_text(divy,"The following sections list Common Criteria and technology terms used in this document.")
        divy.append(self.sec({"id":"cc-terms"},"Common Criteria Terms"))
        tabley = HTM_E.table()
        divy.append(tabley)
        igs=""
        suppress_el = self.rf("//cc:suppress")
        if suppress_el is not None:
            igs = ","+suppress_el.text+","
        fromdoc = self.rx(".//cc:cc-terms/cc:term[text()]")
        builtin=self.boilerplate.xpath(".//cc:cc-terms/cc:term[text()]", namespaces=NS)
        self.make_term_table(fromdoc+builtin, tabley, ignores=igs,)
        self.end_section()
        divy.append(self.sec({"id":"tech-terms"},"Technical Terms"))
        tabley = HTM_E.table({"style":"width: 100%"})
        divy.append(tabley)
        self.make_term_table(node.xpath(".//cc:term[text()]", namespaces=NS), tabley)
        self.end_section()
        self.end_section()
        
    def template_glossary_entry(self, node, parent):
        full = node.attrib["full"]
        tr = HTM_E.tr()
        parent.append(tr)
        id=full.replace(" ", "_")
        td = adopt(tr, HTM_E.td())
        div = adopt(td, HTM_E.div({"id":id}))
        self.add_text(div, full)
        if "abbr" in node.attrib:
            self.add_text(div, " ("+node.attrib["abbr"]+")")
        deftd = adopt(tr, HTM_E.td())
        self.handle_content(node, deftd)


      
    def template_html(self, node ,parent):
        depends = node.findall("cc:depends", NS)
        if len(depends)>0:
            parent = adopt(parent, HTM_E.div({"class":"dependent"}))
            self.depends_explainer(parent, node)
        tag = pp_util.localtag(node.tag)
        html_el = ET.Element(tag, node.attrib)
        parent.append(html_el)
        self.handle_content(node, html_el)

    def add_refs(self, ref_ids, out):
        ul_out = adopt(out, HTM_E.ul())
        for ref_id in ref_ids:
            print("Ref_id is " + str(ref_id))
            ref = self.rf("//cc:*[@id='"+ref_id+"']")
            self.make_xref(ref, adopt(ul_out, HTM_E.li()))
        
    def depends_explainer(self,parent, node,
                          words="The following content should be included if:"):
        depends_ids = self.get_all_dependencies(node)
        choices=depends_ids[0]
        selections=depends_ids[1]
        features=depends_ids[2]
        externals=depends_ids[3]
        bases=depends_ids[4]
        self.add_text(parent, words)
        if len(choices)>0:
            self.add_refs(choices, parent);
            parent.append(HTM_E.div("choices are made"))
        if len(externals)>0:
            self.add_refs(externals, parent);
            parent.append(HTM_E.div("selections are are made in base"))
        if len(selections)>0:
            self.add_refs(selections, parent);
            parent.append(HTM_E.div("selections are made"))
        if len(features)>0:
            self.add_refs(features, parent);
            parent.append(HTM_E.div("features are implemented"))
        if len(bases)>0:
            baselist = ""
            for base in bases:
                basenode = self.rf("//cc:*[@id='"+base+"']")
                self.make_xref(basenode, parent)
            parent.append(HTM_E.div("is a base. "))            

    def apply_templates(self, nodelist, parent):
        if nodelist is None:
            return
        for node in nodelist:
            self.apply_templates_single(node, parent)
    
    def template_usecases(self, node, parent):
        dl=HTM_E.dl()
        parent.append(dl)
        ctr = 1
        for usecase in node.findall("cc:usecase", NS):
            id = usecase.attrib["id"]
            dl.append(HTM_E.dt({"id":id},"[USE CASE "+str(ctr)+"] "+usecase.attrib["title"]))
            dd=HTM_E.dd()
            dl.append(dd)
            self.apply_templates(usecase.findall("./cc:description",NS), dd)
            config = node.find("./cc:config", NS)
            if config is not None:
                dd.append(HTM_E.p("For changes to included SFRs, selections, and assignments required for this use case, see", HTM_E.a({"href":"#appendix-"+id, "class":"dynref"}),"."))
            ctr += 1
    # def get_plural(self, node):
    #     if "target-products" in node.attrib:
    #         return node.attrib["target-products"]
    #     return node.attrib["target-product"]+"s"

    # def get_short(self, node):
    #     if "short" in node.attrib:
    #         return node.attrib["short"]
    #     return self.get_plural(node)

    def handle_felement(self, fel_el,  par):
        formal_id = self.get_ccid_for_ccel(fel_el)
        print("Handling f-element: " + formal_id)
        div_fel=adopt(par, HTM_E.div({"class":"element"}))
        reqid=self.derive_id(fel_el)
        div_fel.append(
            HTM_E.div({"class":"formal_id","id":reqid},
                      HTM_E.a({"href":"#"+formal_id,"class":"abbr"}, formal_id))
        )
        div_reqdesc = adopt(div_fel, HTM_E.div({"class":"reqdesc"}))
        title=fel_el.find("cc:title", NS)
        self.handle_content(title, div_reqdesc)
        # apply_templates_single(title)
        notes = fel_el.findall("cc:note" , NS)
        if len(notes) > 0:
            div_reqdesc.append(HTM_E.br())
            last_char_in_ccid=formal_id.split("/")[0][-1]
            if last_char_in_ccid=="D":
                note_title="Developer"
            elif last_char_in_ccid=="E":
                note_title="Evaluator"
            else:
                note_title="Application"
            div_reqdesc.append(HTM_E.span({"class":"note-header"},note_title+" Note: "))
            for note in notes:
                self.handle_content(note, div_reqdesc)
            mfs = fel_el.findall(".//cc:management-function[cc:app-note]",NS)
            if len(mfs)>0:
                adopt(div_reqdesc,HTM_E.div("Function-specific Application Notes"))
                for mf in mfs:
                    self.set_shortcut(mf)
                    note_head = adopt(div_reqdesc,HTM_E.div({"class":"mf-spec-note"}))
                    self.make_xref(mf, note_head)
                    self.handle_content(mf.find("cc:app-note", NS), div_reqdesc)

        rule_out = HTM_E.span()
        self.add_rules(fel_el, rule_out)
        if not is_empty(rule_out):
            div_reqdesc.append(HTM_E.div("Validation Guidelines"))
            div_reqdesc.append(rule_out)

    def get_fcomp_status_mingled(self, node, out):
        if node in self.sel_sfrs:
            self.add_text(out, "This is a selection-based component. Its inclusion depends upon selection from:")
            for dependsId in node.xpath("cc:depends/@*", namespaces=NS):
                fcomp = self.rx("//cc:f-element[.//cc:selectable//@id='"+dependsId+"']") 
                if len(fcomp)>0:
                    self.add_text(out, " " + self.fel_cc_id(fcomp[0]))
            if is_optional(node):
                self.add_text(out, "This component may also be optionally be included in the ST as if optional.")
        elif node in self.obj_sfrs:
            self.add_text(out,"This is an objective component.")
        elif node in self.opt_sfrs:
            self.add_text(out, "This is an optional component.")
        return None


    def get_fcomp_status_isolated(self, node, out):
        if node in self.sel_sfrs:
            self.add_text(out, "The inclusion of this selection-based component depends upon selection in:")
            for dependsId in node.xpath("cc:depends/@*", namespaces=NS):
                fels = self.rx("//cc:f-element[.//cc:selectable//@id='"+dependsId+"']")
                if len(fels)==1:
                    self.add_text(out, " " + self.fel_cc_id(fels[0]))
                else:
                    print("WARNING: Failed to find exactly one element that contains a selectable with the id: "+dependsId)
            self.add_text(out, ".")
            if is_optional(node):
                self.add_text(out, "This component may also be optionally be included in the ST as if optional.")

    
    def get_fcomp_status(self, node, out):
        if self.are_sfrs_mingled:
            self.get_fcomp_status_mingled(node, out)
        else:
            self.get_fcomp_status_isolated(node, out)

    def add_rule_longref(self, rule, out_el, ruleindex=None):
        out = adopt(out_el, HTM_E.div({"class":"ruleref"}))
        if ruleindex==None:
            ruleindex = self.get_rule_index(rule)
        attrs={"href":"#"+self.derive_id(rule), "class":"ruleref"}
        out.append(HTM_E.a(attrs,"Rule #"+ruleindex))
        desc = rule.find("cc:description", NS)
        if desc is not None:
            self.add_text(out, ": ")
            self.handle_content(desc, out)
        
    def add_rules(self, fel_el, out):
        ids=set()
        harvest_ids(ids, fel_el)
        ctr=0
        for rule in self.rfa("//cc:rule"):
            ctr+=1
            if does_rule_contain_id(rule, ids):
                self.add_rule_longref(rule, out, ruleindex=str(ctr))
                
    
    def handle_component(self, node, par):
        formal = self.fcomp_cc_id(node)
        div = adopt(par, HTM_E.div({"class":"comp", "id":formal}))
        div.append(HTM_E.h4(formal + " "+ node.attrib["name"]))
        status_el = HTM_E.div({"class":"statustag"})
        self.get_fcomp_status(node, status_el)
        if not is_empty(status_el):
            div.append(status_el)
        self.handle_content(node, par)
        if node.tag==CC+"f-component":
            for f_el in node.findall(".//cc:f-element", NS):
                self.handle_felement(f_el, div)
        else:
            self.handle_aelements(node.findall("cc:a-element",NS), formal, par)
        self.handle_fcomp_activities(node, formal, par)

    def sd_handle_component(self, sfr, out):
        formal = self.fcomp_cc_id(sfr)
        div = adopt(out, HTM_E.div({"class":"comp", "id":formal}))
        div.append(HTM_E.h4(formal + " "+ sfr.attrib["name"]))
        self.write_fcomp_activities_out(sfr, formal, out)




# ####################
# #
# ################
#    <xsl:template match="cc:or" mode="use-case">
#     <table class="uc_table_or" style="border: 1px solid black">
#       <tr> <td class="or_cell" rowspan="{count(cc:*)+1}">DECISION <xsl:apply-templates select="." mode="or_path"/></td><td style="display:none"></td></tr>
#       <xsl:for-each select="cc:*">
# 	<tr><td style="width: 99%">
# 	  <div class="choicelabel">CHOICE <xsl:apply-templates mode="choice-path" select="."/></div>
# 	<xsl:apply-templates select="." mode="use-case"/></td></tr>
#       </xsl:for-each>
#     </table>
#   </xsl:template>
 
# ####################
# #
# ################
#   <xsl:template match="cc:config"  mode="choice-path"/>
#   <xsl:template match="cc:*" mode="choice-path">
#     <xsl:if test="parent::cc:or"><xsl:apply-templates mode="or_path" select=".."/><xsl:value-of select="count(preceding-sibling::cc:*)+1"/></xsl:if>
#   </xsl:template>

# ####################
# #
# ################
#   <!-- <xsl:template match="cc:or/cc:*"/> -->

#   <xsl:template match="cc:or" mode="or_path">
#     <xsl:number count="cc:or" level="any" format="A"/>
#   </xsl:template>

  
# ####################
# #
# ################
#   <xsl:template match="*" mode="handle-ancestors">
#     <xsl:message>Definitely shouldn't be here</xsl:message>
#   </xsl:template>


# ####################
# #
# ################
#   <xsl:template match="cc:*[@id]" mode="handle-ancestors">
#     <xsl:param name="prev-id"/>
#     <xsl:param name="not"/>

#     <xsl:variable name="sclass">uc_sel<xsl:if test="ancestor::cc:management-function"> uc_mf</xsl:if></xsl:variable>
#     <!-- if the anscestor is in a PP-->
#     <xsl:if test="ancestor::cc:f-component[@status='optional' or @status='objective'] and not(ancestor::cc:f-component//@id=$prev-id)">
#       <div class="uc_inc_fcomp">
#       Include <xsl:apply-templates select="ancestor::cc:f-component" mode="make_xref"/> in ST.</div>
#     </xsl:if>
#     <!-- If the ancestor is an f-element and the previous one doesn't have the same f-element -->
#     <xsl:if test="ancestor::cc:f-element and not(ancestor::cc:f-element//@id=$prev-id)">
#       <div class="uc_from_fel">
#       From <xsl:apply-templates select="ancestor::cc:f-element" mode="make_xref"/>:</div>
#     </xsl:if>
#     <xsl:if test="ancestor::cc:management-function and not(ancestor::cc:management-function//@id=$prev-id)">
#       <xsl:choose>
#         <xsl:when test="ancestor::cc:management-function/cc:M">
#           <div class="uc_mf">From <xsl:apply-templates select="ancestor::cc:management-function" mode="make_xref"/>:</div>
#         </xsl:when>
#         <xsl:otherwise>
#           <div class="uc_mf">Include <xsl:apply-templates select="ancestor::cc:management-function" mode="make_xref"/>
#           in the ST and :</div>
#         </xsl:otherwise>
#       </xsl:choose>
#     </xsl:if>
#     <xsl:choose>
#       <xsl:when test="$not='1'">
#          <xsl:for-each select="ancestor::cc:selectable">
#           <xsl:if test="not(.//@id=$prev-id)">
#             <div class="{$sclass}">* select <xsl:apply-templates select="." mode="make_xref"/></div>
#           </xsl:if>
#         </xsl:for-each>
#       </xsl:when>
#       <xsl:otherwise>
#         <xsl:for-each select="ancestor-or-self::cc:selectable">
#           <xsl:if test="not(.//@id=$prev-id)">
#             <div class="{$sclass}">* select <xsl:apply-templates select="." mode="make_xref"/></div>
#           </xsl:if>
#         </xsl:for-each>
#       </xsl:otherwise>
#     </xsl:choose>
#   </xsl:template>

# ####################
# #
# ###################  <xsl:template name="get-prev-id">
#     <xsl:if test="not(parent::cc:or or preceding-sibling::cc:*[1][self::cc:or])">
#       <xsl:value-of select="preceding-sibling::cc:*[1]/descendant-or-self::cc:ref-id"/>
#     </xsl:if>
#   </xsl:template>
  
# ####################
# #
# ###################  <xsl:template match="cc:guidance|cc:restrict" mode="use-case">
#     <xsl:variable name="ref-id" select="cc:ref-id[1]/text()"/>
#     <xsl:variable name="sclass">uc_guide<xsl:if test="//cc:management-function//@id=$ref-id"> uc_mf</xsl:if></xsl:variable>

#     <xsl:choose>
#       <xsl:when test="//cc:assignable/@id=$ref-id">
#         <xsl:apply-templates select="//cc:*[@id=$ref-id]" mode="handle-ancestors">
#           <xsl:with-param name="prev-id"><xsl:call-template name="get-prev-id"/></xsl:with-param>
#         </xsl:apply-templates>
#  	<div class="{$sclass}">* for the <xsl:apply-templates select="//cc:assignable[@id=$ref-id]" mode="make_xref"/>, 
# 	<xsl:apply-templates/></div>
#       </xsl:when>
#       <xsl:otherwise>
# 	<xsl:message>Can't find assignable with ID of  <xsl:value-of select="$ref-id"/></xsl:message>
#       </xsl:otherwise>
#     </xsl:choose>
#   </xsl:template>

#    <!-- ############### --> 
#   <!--                 -->
#   <!-- ############### -->
#   <xsl:template match="cc:not[cc:ref-id/text()=//cc:threat/@id]" mode="use-case">
#     <xsl:for-each select="cc:ref-id[text() = //cc:threat/@id]">
#       <xsl:variable name="theid" select="text()"/>
#       <xsl:apply-templates mode="make_xref" select="//cc:*[@id=$theid]"/> does not apply in this use case.
#     </xsl:for-each>
#   </xsl:template>
  

# ####################
# #
# ###################  <xsl:template match="cc:not" mode="use-case">
#     <xsl:variable name="ref-id" select="cc:ref-id[1]/text()"/>
#     <xsl:apply-templates select="//cc:*[@id=$ref-id]" mode="handle-ancestors">
#        <xsl:with-param name="prev-id"><xsl:call-template name="get-prev-id"/></xsl:with-param>
#        <xsl:with-param name="not" select="'1'"/>
#     </xsl:apply-templates>
#     <xsl:if test="$ref-id=//cc:module/@id">
#       <div class="uc,not,module">Exclude the 
#       <xsl:apply-templates select="//cc:module[@id=$ref-id]" mode="make_xref"/> module from the ST
#       </div>
#     </xsl:if>
#     <xsl:if test="cc:ref-id/text()=//cc:selectable/@id">
#       <div class="uc_not">Do not choose:
#       <xsl:for-each select="cc:ref-id[text()=//cc:selectable/@id]">
# 	<!-- Not sure why this is a for -->
#         <xsl:variable name="ref" select="text()"/>
#         <div class="uc_not_sel">* <xsl:apply-templates select="//cc:selectable[@id=$ref]" mode="make_xref"/></div>
#       </xsl:for-each>
#       </div>
#     </xsl:if>
#   </xsl:template>


# ####################
# #
# ###################  <xsl:template match="cc:doc" mode="use-case">
#     <xsl:variable name="docpath"><xsl:value-of select="concat($work-dir,'/',@ref)"/>.xml</xsl:variable>
#     <xsl:variable name="docurl"><xsl:value-of select="//cc:*[@id=current()/@ref]/cc:url/text()"/></xsl:variable>
#     <xsl:variable name="name"><xsl:value-of select="document($docpath)//cc:PPTitle"/><xsl:if test="not(document($docpath)//cc:PPTitle)">PP-Module for <xsl:value-of select="document($docpath)/cc:Module/@name"/></xsl:if></xsl:variable>


#     <div class="uc_inc_pkg"> From the <a href="{$docurl}"><xsl:value-of select="$name"/></a>: </div>
#     <xsl:for-each select="cc:ref-id">
#       <xsl:call-template name="handle-ref-ext"> 
#         <xsl:with-param name="ref-id" select="text()"/>
#         <xsl:with-param name="root" select="document($docpath)/cc:*"/>
#       </xsl:call-template>
#     </xsl:for-each>
#   </xsl:template>

# ####################
# #
# ###################  <xsl:template name="handle-ref-ext">
#     <xsl:param name="ref-id"/>
#     <xsl:param name="root"/>

#     <xsl:choose>
#       <xsl:when test="$root//cc:selectable[@id=$ref-id]">
#         <xsl:apply-templates select="$root//cc:*[@id=$ref-id]" mode="handle-ancestors">
#           <xsl:with-param name="prev-id"><xsl:call-template name="get-prev-id"/></xsl:with-param>
#         </xsl:apply-templates>
#       </xsl:when>
#       <xsl:when test="$root//cc:f-component[@id=$ref-id]">
#         <div class="uc_inc_fcomp">Include <xsl:apply-templates select="$root//cc:*[@id=$ref-id]" mode="make_xref"/> in the ST </div>
#       </xsl:when>
#       <xsl:when test="$root//cc:management-function//@id=$ref-id">
#         <xsl:apply-templates select="$root//cc:*[@id=$ref-id]" mode="handle-ancestors">
#           <xsl:with-param name="prev-id"><xsl:call-template name="get-prev-id"/></xsl:with-param>
#         </xsl:apply-templates>
#         <div class="uc_mf">Include
#         <xsl:apply-templates select="$root//cc:management-function[@id=$ref-id]" mode="make_xref"/>
#         in the ST</div>
#       </xsl:when>
#       <xsl:otherwise>
#         <xsl:message> Failed to find <xsl:value-of select="$ref-id"/> in <xsl:call-template name="genPath"/></xsl:message>
#       </xsl:otherwise>
#     </xsl:choose>
#   </xsl:template> 
  
# ####################
# #
# ###################<!--  <xsl:template match="cc:ref-id" mode="use-case">
#     <xsl:call-template name="handle-ref">
#       <xsl:with-param name="ref-id" select="text()"/>
#     </xsl:call-template>
#   </xsl:template>  -->

  
#  <xsl:template match="cc:ref-id" mode="use-case">
#    <xsl:variable name="ref-id-txt" select="text()"/>
#    <xsl:choose>
#       <xsl:when test="//cc:module[@id=$ref-id-txt]">
# 	<div class="uc,module"> Include the <xsl:apply-templates select="//cc:*[@id=$ref-id-txt]" mode="make_xref"/> module in the ST </div>
#       </xsl:when>
#       <xsl:when test="//cc:selectable[@id=$ref-id-txt]">
#         <xsl:apply-templates select="//cc:*[@id=$ref-id-txt]" mode="handle-ancestors">
#           <xsl:with-param name="prev-id"><xsl:call-template name="get-prev-id"/></xsl:with-param>
#         </xsl:apply-templates>
#       </xsl:when>
#       <xsl:when test="//cc:f-component[@id=$ref-id-txt]">
#         <div class="uc_inc_fcomp">Include <xsl:apply-templates select="//cc:*[@id=$ref-id-txt]" mode="make_xref"/> in the ST </div>
#       </xsl:when>
#       <xsl:when test="//cc:management-function//@id=$ref-id-txt">
#         <xsl:apply-templates select="//cc:*[@id=$ref-id-txt]" mode="handle-ancestors">
#           <xsl:with-param name="prev-id"><xsl:call-template name="get-prev-id"/></xsl:with-param>
#         </xsl:apply-templates>
#         <div class="uc_mf">Include
#         <xsl:apply-templates select="//cc:management-function[@id=$ref-id-txt]" mode="make_xref"/>
#         in the ST</div>
#       </xsl:when>
#       <xsl:otherwise>
#         <xsl:message> Failed to find <xsl:value-of select="$ref-id-txt"/> in <xsl:call-template name="genPath"/> (use case or rule)</xsl:message>
#         <xsl:if test="./@alt">
#           <b><i><xsl:value-of select="./@alt"/></i></b>
#         </xsl:if>
#       </xsl:otherwise>
#     </xsl:choose>
#   </xsl:template>
 
  
  
# ####################
# #
# ###################
#   <xsl:template name="handle-ref">
#     <xsl:param name="ref-id" select="text()"/>
#     <xsl:choose>
#       <xsl:when test="//cc:selectable[@id=$ref-id]">
#         <xsl:apply-templates select="//cc:*[@id=$ref-id]" mode="handle-ancestors">
#           <xsl:with-param name="prev-id"><xsl:call-template name="get-prev-id"/></xsl:with-param>
#         </xsl:apply-templates>
#       </xsl:when>
#       <xsl:when test="//cc:f-component[@id=$ref-id]">
#         <div class="uc_inc_fcomp">Include <xsl:apply-templates select="//cc:*[@id=$ref-id]" mode="make_xref"/> in the ST </div>
#       </xsl:when>
#       <xsl:when test="//cc:management-function//@id=$ref-id">
#         <xsl:apply-templates select="//cc:*[@id=$ref-id]" mode="handle-ancestors">
#           <xsl:with-param name="prev-id"><xsl:call-template name="get-prev-id"/></xsl:with-param>
#         </xsl:apply-templates>
#         <div class="uc_mf">Include
#         <xsl:apply-templates select="//cc:management-function[@id=$ref-id]" mode="make_xref"/>
#         in the ST</div>
#       </xsl:when>
#       <xsl:otherwise>
#         <xsl:message> Failed to find <xsl:value-of select="$ref-id"/> in <xsl:call-template name="genPath"/></xsl:message>
#       </xsl:otherwise>
#     </xsl:choose>
#   </xsl:template> 


        

    def handle_aelements(self, els, formal, par):
        agroups = self.sort_aelements(els)
        for title in "Developer action", "Content and presentation", "Evaluator action":
            tipe=title[0:1]
            if len(agroups[tipe])>0:
                par.append(HTM_E.h4(title+" elements:"))
                for el in agroups[tipe]:
                    self.handle_felement(el, par)

    def sort_aelements(self, els):
        ret={"D":[], "C":[], "E":[]}
        for el in els:
            if self.add_based_on_attr(el, ret):
                continue
            title=el.find("cc:title",NS).text
            if title.startswith("The developer shall"):
                ret["D"].append(el)
                print("Adding to developer")
            elif title.startswith("The evaluator shall"):
                ret["E"].append(el)
            else:
                ret["C"].append(el)
        return ret
            

            
    def add_based_on_attr(self, el, theset):
        if "type" in el.attrib:
            theset[el.attrib["type"]].append(el)
            return True
        return False


    def make_aactivity_pane(self):
        return HTM_E.div(attrs("activity_pane hide"),
                                  HTM_E.div(attrs("activity_pane_header"),
                                            HTM_E.a({"onclick":"toggle(this);return false;","href":"#"},
                                                    HTM_E.span(attrs("activity_pane_label"),"Evaluation Activities"),
                                                    HTM_E.span(attrs("toggler"))
                                                    )
                                            )
                                  )

        
    def handle_fcomp_activities(self, fcomp, formal, out):
        div = self.make_aactivity_pane()
        div_out = adopt(div, HTM_E.div(attrs("activity_pane_body")))
        if self.write_fcomp_activities_out(fcomp, formal, div_out):
            out.append(div)
            
            
    def write_fcomp_activities_out(self,  fcomp, formal, out):
        comp_acts = fcomp.xpath(".//cc:aactivity[not(cc:elev)]", namespaces=NS)
        should_add=self.handle_grouped_activities(formal, comp_acts, out)
        for fel in fcomp.xpath(".//cc:*[cc:aactivity/cc:elev]", namespaces=NS):
            # out.append(HTM_E.div(attrs("element-activity-header"), ))
            fel_id = self.fel_cc_id(fel)
            self.handle_grouped_activities(fel_id, fel.findall("cc:aactivity[cc:elev]", NS), out, "element")
            should_add=True
        return should_add

            
    def handle_grouped_activities(self, formal, aacts, out, level="fcomp"):
        if len(aacts)==0:
            return False
        general_div=adopt(out, HTM_E.div(HTM_E.div(attrs(level+"-activity-header"),formal)))
        acts={"TSS":None, "Guidance":None,"Tests":None,"KMD":None,"no-tests":None}
        for aact in aacts:
            self.apply_templates_single(aact, general_div)
            for act in acts:
                act_div=HTM_E.div()
                acts[act]=act_div
                act_el = aact.find("cc:"+act,NS)
                if self.handle_content(act_el, act_div):
                    out.append(act_div)
                
        for act in acts:
            if not is_empty(acts[act]):
                if act != "no-tests":
                    out.append(HTM_E.div(attrs("eacategory"),act))
                out.append(acts[act])
        return True


    def find_first_section_with_title(self, title):
        sections = self.find_sections_with_title(title)
        if len(sections)==0:
            return None
        else:
            return sections[0]
    
    def find_sections_with_title(self, title):
        underscored_title = title.replace(" ", "_")
        xpath="//*[@title='"+title+"']|sec:"+underscored_title+"[not(@title)]"        
        return self.rx(xpath)

    
    def handle_sparse_sfrs(self, sfrs, par, sfr_category, is_sd=False):
        """
        Converts a group of SFRs to HTML equivalent. Putting section
        headers in and grouping the SFRs appropriately underthem.

        :param sfrs An iterable group of f-component XML elements
        :param par The XML output parent
        :param sfr_category A string reflecting the type of sfrs (e.g. optional, sel-based)
        :param is_sd Boolean whether it's being called to write to a SD
        """

        titles={}
        for sfr in sfrs:
            sec = sfr.find("..")
            title = self.get_section_title(sec)
            id = self.derive_id(sec)+"__" + sfr_category
            if title not in titles:
                if len(titles)>0:
                    self.end_section()
                titles[title]=1
                par.append(self.sec({"id":id}, title))
                if not is_sd:
                    self.handle_content(sec,par)
            if is_sd:
                self.sd_handle_component(sfr, par)
            else:
                self.handle_component(sfr, par)
        if len(titles)>0:
            self.end_section()
# WE HAVE TO CLOSE THESE SECTIONS            
        
    def apply_templates_single(self, node, parent):
        # Returns None if 
        if node is None or not isinstance(node.tag,str):
            return False
        self.apply_template_to_element(node, parent)
        return True

    
    def apply_template_to_element(self, node, parent):
        tag = node.tag
        print("Applying: " + tag)
        if tag.startswith("{https://niap-ccevs.org/cc/v1/section}"):
            self.template_newsection(node, parent)
        elif tag == CC+"section":
            self.template_oldsection(node, parent)
        elif tag == CC+"appendix":
            self.template_oldsection(node, parent)
        elif tag.startswith("{http://www.w3.org/1999/xhtml}"):
            self.template_html(node, parent)
        elif tag == CC+"xref":
            self.template_xref(node, parent)
        elif tag == CC+"tech-terms":
            self.template_tech_terms(node, parent)
        elif tag==CC+"usecases":
            self.template_usecases(node, parent)
        elif tag==CC+"assumptions"\
             or tag==CC+"cclaims"\
             or tag==CC+"threats"\
             or tag==CC+"OSPs"\
             or tag==CC+"SOs"\
             or tag==CC+"SOEs":
            self.template_assumptions_cclaims_threats_OSPs_SOs_SOEs(node, parent)
        elif tag==CC+"sfrs":
            self.template_sfrs(node, parent)
        elif tag in DONT_PROCESS:
            return
        elif tag in TRANSPARENT:
            self.handle_content(node, parent)
        elif tag==CC+"management-function-set":
            self.template_management_function_set(node, parent)
        elif tag==CC+"ctr":
            self.template_ctr(node, parent)
        elif tag==CC+"no-link":
            span=adopt(parent, HTM_E.span({"class":"no-link"}))
            self.handle_content(node, parent, span)
        elif tag==CC+"manager":
            td = adopt(parent, HTM_E.td())
            self.handle_content(node, td)
        elif tag==CC+"figure":
            self.handle_figure(node, parent)
        elif tag==CC+"audit-table":
            self.template_audit_table(node, parent)
        elif tag==CC+"selectables":
            self.template_selectables(node, parent)
        elif tag==CC+"assignable":
            self.template_assignable(node, parent)
        elif tag==CC+"int":
            self.template_int(node, parent)
        elif tag==CC+"_":
            self.make_xref(self.shortcut, parent)
        elif tag==CC+"refinement":
            span = adopt(parent, HTM_E.span({"class":"refinement"}))
            self.handle_content(node, span)
        elif tag==CC+"testlist":
            self.handle_testlist(node, parent)
        elif tag == CC+"consistency_rationale":
            print("Not doing a-compoents")
        elif tag == CC+"equation":
            self.handle_equation(node, parent)
        elif tag == CC+"Objective" or tag == CC+"Evidence":
            localtag = pp_util.localtag(node.tag)
            obj_out = adopt(parent, HTM_E.div({"class":"test_"+localtag}))
            obj_out.append(HTM_E.b(localtag+": "))
            self.handle_content(node, obj_out)
        else:
            raise Exception("Can't handle: " + pp_util.debug_node(node))

    def handle_equation(self, node, out):
        id=self.derive_id(node)
        eq_out = HTM_E.td("$$")
        self.handle_content(node, eq_out)
        self.add_text(eq_out, "$$")
        ctr_out = HTM_E.td("(")
        self.create_ctr("equation", id, ctr_out, "", sep="")
        self.add_text(ctr_out,")")
        out.append(HTM_E.table({"class":"equation_"},
            HTM_E.tr(eq_out, ctr_out)
            ))
        

    def get_test_title(self, testnode):
        if testnode in self.test_titles:
            return self.test_titles[testnode]
        
        aa_el = testnode.xpath("ancestor::cc:aactivity", namespaces=NS)[0]
        if aa_el.find("cc:elev", NS) is None:
            ance =testnode.xpath("ancestor::cc:f-component", namespaces=NS)[0]
            cc_id=self.fcomp_cc_id(ance)
        else:
            ance =testnode.xpath("ancestor::cc:f-element", namespaces=NS)[0]
            cc_id=self.fel_cc_id(ance)
        ctr=1
        self.derive_test_title_recur(aa_el, cc_id+"#", stack=[0])
        return self.test_titles[testnode]

    def derive_test_title_recur(self, node, prefix, stack):
        if node.tag==CC+"test":
            new_num=stack.pop() + 1
            stack.append(new_num)
            test_label = prefix +".".join(map(str, stack))
            self.test_titles[node] = test_label
            stack.append(0)
        for kid in node:
            self.derive_test_title_recur(kid, prefix, stack)
        if node.tag==CC+"test":
            stack.pop()
        
    
    def handle_testlist(self, testlist, out):
        ul = adopt(out, HTM_E.ul(attrs("testlist-")))
        for test in testlist.findall("cc:test", NS):
            li = adopt(ul, HTM_E.li(attrs("test-")))
            test_id=self.derive_id(test)
            title = self.get_test_title(test)
            # self.register_keyterm( title, test_id)
            atts=attrs("test- def_", test_id)
            adopt(li, HTM_E.a(atts, "Test "+title))
            dependses = test.findall("cc:depends", NS)
            if len(dependses)>0:
                self.add_text(li, "[conditional,aaaa]")
            self.add_text(li, ":")
            self.handle_content(test, li)

    def get_title_n_sfrs(self, thistable):
        if thistable=="mandatory":
            return ("Mandatory", self.man_sfrs)
        elif thistable=="optional":
            return ("Strictly Optional", self.opt_sfrs)
        elif thistable=="objective":
            return ("Objective",self.obj_sfrs)
        elif thistable=="feat-based":
            return ("Implementation-based",self.impl_sfrs)
        elif thistable=="sel-based":
            return ("Selection-based", self.sel_sfrs)
        else:
            raise Exception("Can't handle audit table for: " + thistable)
        
  
    def template_audit_table(self, node, par, thistable=None):
        if thistable is None and "table" in node.attrib:
            thistable=node.attrib["table"]
        explainer="The auditable events in the table below are included in a Security Target if both the associated requirement is included and the incorporating PP or PP-Module supports audit event reporting through FAU_GEN.1 and any other criteria in the incorporating PP or PP-Module are met."

        if thistable=="mandatory":
            explainer = "The auditable events in the table below must be included in a Security Target."
        title_sfrs = self.get_title_n_sfrs(thistable)
        title = title_sfrs[0]
        sfrs  = title_sfrs[1]
        
        sfrs_event_map = self.get_sfrs_with_audit_events(sfrs, thistable)

        if len(sfrs_event_map)==0:
            return
        if node is None:
            myid="at-"+thistable+"-"
        else:
            myid = self.derive_id(node)            
        
        div=HTM_E.div()
        div.append(HTM_E.p(explainer))
        title="Auditable Events for "+ title + " Requirements"
        table=adopt(div, HTM_E.table({"border":"1"}))
        caption = adopt(table, HTM_E.caption())
        self.create_ctr("Table", myid, caption, "Table ")
        pp_util.append_text(caption, title)
        tr = HTM_E.tr(HTM_E.th("Requirement"),HTM_E.th("Auditable Events"),HTM_E.th("Additional Audit Record Contents"))
        table.append(tr)
        # This is not going to handle no SFRs well
        for fcomp in sfrs_event_map:
            events = sfrs_event_map[fcomp]
            add_grouping_row(table, self.fcomp_cc_id(fcomp), len(events))
            for event in events:
                self.make_audit_row_from_event(event, table)
        par.append(div)

    # This assumes the group never changes
    def get_sfrs_with_audit_events(self, sfrs, table):
        if not table in self.group_audit_map:
            entry={}
            for sfr in sfrs:
                events = sfr.xpath(".//cc:audit-event[not(@table) or @table='"+table+"']", namespaces=NS)
                if len(events)>0:
                    entry[sfr]=events
            self.group_audit_map[table]=entry
        return self.group_audit_map[table]

            
    def make_audit_row_from_event(self, event, table):
        row = adopt(table, HTM_E.tr())
        desc_in = event.find("cc:audit-event-descr",NS)
        if desc_in is None:
            row.append(HTM_E.td("No events specified"))
            row.append(HTM_E.td("N/A"))
            return
        desc = adopt(row, HTM_E.td())
        self.template_maybe_optional_audit(desc_in, desc, decider=event)
        extra= adopt(row, HTM_E.td())
        info_in = event.findall("cc:audit-event-info",NS)
        if len(info_in)==1:
            self.template_maybe_optional_audit(info_in[0], extra, nowords="No additional information")
        elif len(info_in)>1:
            ul=adopt(extra, HTM_E.ul())
            for single_info in info_in:
                self.template_maybe_optional_audit(single_info, adopt(ul, HTM_E.li()), nowords="No additional information")

        
    def template_maybe_optional_audit(self, nodein, out, decider=None, nowords="None"):
        if decider==None:
            decider=nodein
        if is_optional(decider):
            out.append(HTM_E.b("[selection"))
            self.add_text(out, ": ")
            self.handle_content(nodein, out)
            self.add_text(out, ", "+nowords)
            out.append(HTM_E.b("]"))
        else:
            self.handle_content(nodein, out)
            
            
        # for fcomp in self.rx("//cc:f-component[cc:audit-event]|//cc:f-component[@id=//cc:audit-event[not(parent::cc:external-doc)]/@affects]"):
  #       <xsl:variable name="fcompstatus"><xsl:apply-templates select="." mode="compute-fcomp-status"/></xsl:variable>
  #       <xsl:if test="cc:audit-event[(@table=$thistable) or (not(@table) and ($fcompstatus=$thistable))]">
  #         <xsl:variable name="rowspan"
  #       		select="1+count(cc:audit-event[(@table=$thistable) or (not(@table) and ($fcompstatus=$thistable))])"/>
  #         <xsl:variable name="myid"><xsl:apply-templates select="." mode="getId"/></xsl:variable>
  #         <tr data-sortkey="{$myid}">
  #           <td rowspan="{$rowspan}">
  #             <xsl:value-of select="$myid"/>
  #           </td>      <!-- SFR name -->
  #           <td style="display:none"></td>
  #           <!-- <td>fake</td> -->
  #         </tr>
  #         <!-- Fake row so that the CSS color alternator doesn't get thrown off-->
  #         <!-- The audit event is included in this table only if
  #                - The audit event's expressed table attribute matches this table
  #                - Or the table attribute is not expressed and the audit event's default audit attribute matches this table.
  #                - The default table for an audit event is the same as the status attribute of the enclosing f-component.  -->
  #           <!-- <xsl:if test="(@table=$thistable) or (not(@table) and ($fcompstatus=$thistable))"> -->
  # 	    <xsl:apply-templates select="cc:audit-event[(@table=$thistable) or (not(@table) and ($fcompstatus=$thistable))]" mode="kg-intable">
  #             <xsl:with-param name="sortkey" select="$myid"/>
  #           </xsl:apply-templates>
  #       </xsl:if>
  #     </xsl:for-each>

  #  NOT DOING THIS THIS
  #     <!-- Goes through each external document -->
  #     <xsl:for-each select="//cc:*[@id=//cc:external-doc[//cc:audit-event/@table=$thistable]/@ref]">
  #       <tr><td colspan="3">
  #         From <xsl:apply-templates select="." mode="make_xref"/>
  #       </td></tr>

  #       <xsl:variable name="listy"><xsl:for-each select="//cc:audit-event[@table=$thistable and parent::cc:external-doc/@ref=current()/@id]/@ref-cc-id"><xsl:value-of select="."/>,</xsl:for-each>
  #       </xsl:variable>
  #       <xsl:call-template name="external-gatherer">
  #         <xsl:with-param name="listy" select="$listy"/>
  #         <xsl:with-param name="table" select="$thistable"/>
  #         <xsl:with-param name="ext_id" select="@id"/>
  #       </xsl:call-template>
  #     </xsl:for-each>
      
  #   </table>
  # </xsl:template>


        
    def get_pre(self, el):
        if "pre" in el.attrib:
            return el.attrib["pre"]
        if el.tag == CC+"figure":
            return "Figure "
        return pp_util.get_attr_or(el, "ctr-type", default="Table ")
    
    def template_ctr(self, node, par):
        ctrtype = node.attrib["ctr-type"]
        prefix=ctrtype+" "
        if "pre" in node.attrib:
            prefix=node.attrib["pre"]
        id = self.derive_id(node)
        self.create_ctr(ctrtype, id, par, prefix, child=node)

        # count = str(self.get_next_counter(ctrtype))
        # span = adopt(par, HTM_E.span({"class":"ctr","data-counter-type":"ct-"+ctrtype,
        #                               "id":id}, ))
        # self.add_text(span,self.get_pre(node))
        # span.append(HTM_E.span({"class":"counter"}, id))
        # self.handle_content(node, span)

        
    def template_int(self, node):
        if not pp_util.is_attr(node, "hide", "no"):
            return ""
        if "lte" in node.attrib:
            lte = node.attrib["lte"]
            if "gte" in node.attrib:
                gte = node.attrib["gte"]
                ret+=" between "+ gte + " and " + lte + ", inclusive "
                return ret
            ret+=" less than or equal to " + lte
            return ret
        elif "gte" in node.attrib:
            ret+=" greater than or equal to " + node.attrib["gte"]
        return ret

    def template_assignable(self, node, par):
        id=self.derive_id(node)
        self.add_text(par,"[")
        par.append(HTM_E.b("assignment"))
        self.add_text(par,": ")
        span=adopt(par, HTM_E.span({"class":"assignable-content","id":id}))
        self.handle_content(node, span)
        self.add_text(par,"]")

    # def template_appendix(self, node, parent):
    #     id=self.derive_id(node)
    #     title=node.attrib["title"]
    #     parent.append(HTM_E.h1({"id":id},title))
    #     if "boilerplate" in node.attrib and node.attrib["boilerplate"]=="no":
    #         return
    #     self.handle_section_hook_base(title, node, parent)
    #     self.handle_content(node, parent)

    def template_selectables(self, node, par):
        if not is_in_choice(node):
            self.add_text(par,"[")
            par.append(HTM_E.b("selection"))
            if node.find("cc:onlyone", NS) is not None:
                par.append(HTM_E.b(", choose one of"))
            self.add_text(par, ": ")
            
        sep=", "
        extraclass=""
        if node.find("cc:bulletize", NS) is not None \
           or node.find(".//cc:selectables", NS) is not None:
            sep=None
            extraclass=" linebreak-sel"

        # Add the comma thing
        lagsep=None
        sels = node.findall("./cc:selectable",NS)
        sels_left = len(sels)
        for selectable in sels:
            sels_left = sels_left-1
            if is_in_choice(node) and sels_left==0 and sep==", ":
                lagsep=lagsep+"or "
            id = self.derive_id(selectable)
            self.add_text(par,lagsep)
            lagsep=sep
                
            span = adopt(par,HTM_E.span({"class":"selectable-content"+extraclass, "id":id}))
            self.handle_content(selectable, span)
        if not is_in_choice(node):
            self.add_text(par,"]")
 #                   <li style="{@style}"><xsl:apply-templates select="." mode="handle_sel"/></li>
 #                   </xsl:for-each></ul>
 #    </xsl:when>
 #    <xsl:otherwise>
 #      <xsl:for-each select="cc:selectable|cc:not-selectable">
 #        <xsl:apply-templates mode="handle_sel" select="."/><xsl:call-template name="commaifnotlast"/>
 #        <xsl:text> </xsl:text>
 #      </xsl:for-each>
 #    </xsl:otherwise>
 # </xsl:choose>]</xsl:template>

 # <xsl:template mode="handle_sel" match="cc:selectable|cc:not-selectable">
 #    <xsl:variable name="id"><xsl:apply-templates mode="getId" select="."/></xsl:variable>
 #    <span class="{local-name()}-content" id="{$id}"><xsl:apply-templates/></span>
 # </xsl:template>
        
            
    def template_management_function_set(self, node, par):
        table = adopt(par, HTM_E.table({"class":"mfs","style":"width: 100%;"}))
        tr = adopt(table, HTM_E.tr({"class":"header"}))
        tr.append(HTM_E.td("#"))
        tr.append(HTM_E.td("Management Function"))
        managers = node.findall("./cc:manager", NS)
        self.apply_templates(managers,tr)
        ctr=0
        prefix = pp_util.get_attr_or(node, "ctr-prefix")
        deffy  = node.attrib["default"]
        for mf in node.findall("./cc:management-function", NS):
            ctr+=1
            self.make_mf_row(mf, prefix+str(ctr), managers, deffy, table)

    # def get_mf_id(self, node):
    #     if "id" in node.attrib:
    #         return node.attrib["id"]
    #     return "_mf_"+str(self.get_global_index(node))

    def make_mf_val(self, tag, node, par):
        attrs = {"class":"tooltiptext"}
        if tag == "O":
            par.append(HTM_E.div("O",HTM_E.span(attrs,"Optional")))
        elif tag =="M":
            par.append(HTM_E.div("M",HTM_E.span(attrs,"Mandatory")))
        elif tag == "NA":
            par.append(HTM_E.div("-",HTM_E.span(attrs,"N/A")))
        else:
            self.handle_content(node, par)

            
    def make_mf_row(self, mf, prefix, managers, defval, par):
        mf_num = str(self.get_global_index(mf))
        mf_id = self.derive_id(mf)
        tr = adopt(par, HTM_E.tr())
        tr.append(HTM_E.td(HTM_E.a(def_attr(mf_id),prefix)))
        td=adopt(tr, HTM_E.td({"style":"text-align:left"}))
        self.apply_templates_single(mf.find("cc:text",NS), td)
        for manager in managers:
            cid=manager.attrib["cid"]
            tagnode=mf.find("*[@ref='"+cid+"']")
            if tagnode == None:
                val=defval
            else:
                val= pp_util.localtag(tagnode.tag)
            td=adopt(tr, HTM_E.td())
            self.make_mf_val(val, tagnode,td)

    def get_first_section_with_title(self, title):
        possibles=self.root.xpath("//*[@title='"+title+"']|//sec:"+title.replace(' ','_'), namespaces=NS)
        if possibles is None or len(possibles)==0:
            return None
        return possibles[0]
            
    def set_shortcut(self, node):
        self.shortcut = node

    def make_xref_mf(self, id, parent):
        parent.append(HTM_E.a({"href":"#"+id,"class":"dynref"}))

    def make_xref_generic(self, target, parent, ref, deftext=""):
        a_el=adopt(parent, HTM_E.a({"href":"#"+target.attrib["id"],"class":"dynref"}))
        if not self.handle_content(ref, a_el):
            self.add_text(a_el, deftext)

    # def make_xref_section(self, id, parent):
    #     parent.append(HTM_E.a({"href":"#"+id,"class":"dynref"},"section "))

    def make_xref_bibentry(self, node, parent):
        txt = "["+node.find("./cc:tag", NS).text+"]"
        anchor="#"+node.attrib["id"]
        parent.append(E.a(txt, href=anchor))

    def make_xref_feature(self, target, out, ref=None):
        refid = self.derive_id(target)
        a_out = adopt(out, HTM_E.a({"href":"#"+refid}, target.attrib["title"]))

        
    def make_xref_selectable(self, target, out, ref):
        refid = self.derive_id(target)
        a_out = adopt(out, HTM_E.a({"href":"#"+refid}))
        readable = target.find("cc:readable", NS)
        snip = target.find("cc:snip", NS)
        if readable is not None:
            self.handle_content(readable, a_out)
        elif snip is not None:
            self.handle_content(snip, a_out)
        else:
            self.handle_content(target, a_out)


    
    # M
    def make_xref(self, target, parent, ref=None):
        if not hasattr(target, "tag"):
            self.broken_refs.add( (target, adopt(parent, HTM_E.a()), ref) )
        elif target.tag == CC+"entry":
            self.make_xref_bibentry(target, parent)
        elif target.tag == CC+"base-pp" or target.tag == CC+"include-pkg":
            theid= target.attrib["id"]
            self.pkgs[theid].make_xref_edoc(parent)
        elif target.tag == CC+"f-element":
            ccid=self.get_ccid_for_ccel(target)
            id=self.derive_id(target)
            parent.append(HTM_E.a({"href":"#"+id}, ccid))
        elif target.tag == CC+"selectable":
            self.make_xref_selectable(target, parent, ref)
        elif target.tag == CC+"feature":
            self.make_xref_feature(target, parent, ref)
        else:
            self.broken_refs.add( (self.derive_id(target), adopt(parent, HTM_E.a()), ref) )
        # if target.tag.startswith("{https://niap-ccevs.org/cc/v1/section}"):
        #     self.make_xref_section(pp_util.localtag(target.tag), parent)
        # elif target.tag == CC+"section":
        #     self.make_xref_section(target.attrib["id"], parent)
        # elif target.tag == CC+"management-function":
        #     self.make_xref_mf(self.derive_id(target), parent)
        # elif target.tag == CC+"test":
        #     self.make_xref_generic(target, parent, ref, "")
        # elif target.tag == CC+"figure":
        #     self.make_xref_generic(target, parent, ref, "figure")
        # elif target.tag == CC+"ctr":
        #     self.make_xref_generic(target, parent, ref, "")
        # elif target.tag == CC+"appendix":
        #     self.make_xref_generic(target, parent, ref, "Appendix")
        # elif target.tag == CC+"equation":
        #     self.make_xref_generic(target, parent, ref, "equation")
        # else:
        #     raise Exception("Cannot reference: " + target.tag + " " + target.text)

    def is_base(self, attr):
        b_el = self.rf("//cc:base-pp[@id='"+attr+"']")
        if b_el is not None:
            raise Exception("Should not have a base")
        return False
        
    # def show_package(self, node):
    #     ret+="<a href=\""+node.attrib["url"]+"\">"
    #     if "name" in node.attrib:
    #         ret+=node.attrib["name"]
    #         ret+=pp_util.get_attr_or(node, "short", post=lambda x:"("+x+")")
    #         version = node.attrib["version"]            
    #     else:
    #         proot = self.pkgs[node.attrib["id"]]
    #         ret+=proot.find(".//cc:PPTitle",NS).text
    #         version=proot.find(".//cc:PPVersion",NS).text
    #     ret+="Package, version "
    #     ret+=version
    #     ret+="</a> Conformant"

        
    def handle_rules_appendix(self, out):
        rules = self.rfa("//cc:rule")
        if len(rules)==0:
            return
        out.append(HTM_E.p("This appendix contains \"rules\" specified "+
                            "by the PP Authors that indicate whether certain selections "+
	                    "require the making of other selections in order for a "+
                            "Security Target to be valid. For example, selecting "+
                            "\"HMAC-SHA-3-384\" as a supported keyed-hash "+
                            "algorithm would require that \"SHA-3-384\" be selected "+
                            "as a hash algorithm."))
        out.append(HTM_E.p("This appendix contains only such \"rules\" as have been "+
                            "defined by the PP Authors, and does not necessarily "+
	                    "represent all such dependencies in the document."))
        ctr=1
        for rule in rules:
            ruleid = self.derive_id(rule)
            out.append(HTM_E.h2({"id":ruleid}, "Rule #"+str(ctr)))
            ctr+=1
            desc_out = adopt(out, HTM_E.div())
            self.handle_content(rule.find("cc:description", NS), desc_out)
            self.apply_use_case_templates(rule, out)

    def apply_use_case_templates(self,nodes, out):
        for node in nodes:
            if is_comment(node):
                pass
            elif node.tag == CC+"and" or node.tag == CC+"config" or node.tag == CC+"not":
                print("WUZHERE: " + node.tag)
                self.and_use_case(node, out)
            elif node.tag == CC+"if":
                pass
            elif node.tag == CC+"then":
                self.then_usecase(node, out)
            elif node.tag==CC+"description":
                pass
            elif node.tag==CC+"ref-id":
                print("WUZHERE: " + node.tag)
                self.refid_use_case(node, out)
            elif node.tag==CC+"doc":
                self.doc_use_case(node, out)
            else:
                print("can't handle: "+node.tag + " in use-case.")


            
    def and_use_case(self, and_el, out):
        for child in and_el:
            print("Anding :"+ child.tag)
            self.apply_use_case_templates(child, out)
            
            # <xsl:template match="cc:and" mode="use-case" name="use-case-and">
            #   <xsl:apply-templates mode="use-case"/>
            # </xsl:template>
            

    def or_use_case(self, or_el, out):
        table_attrs = {"class":"uc_table_or", "style":"border: 1px solid black"}
        table_out = adopt(out, HTM_E.table(table_attrs,
                                           HTM_E.tr(
                                               HTM_E.td({"class":"or_cell", "rowspan":len(or_el)}, "OR"),
                                               blank_cell()
                                           )
                                           ))



    def doc_use_case(self, doc_el, out):
        doc_id = doc_el.attrib["ref"]
        print("Get_product: " + doc_id)
        print("Doc is a "+doc_el.tag)
        target = self.rf("//cc:*[@id='"+doc_id+"']")
        if target is None:
            print("Could not find an external document: "+target)
        div=adopt(out, HTM_E.div({"class":"uc pkg"}, "From the "))
        edoc=None
        if target.tag == CC+"include-pkg":
            target_edoc = self.pkgs[doc_id]
        elif target.tag == CC+"module":
            target_edoc= self.modules[doc_id]
        else:
            print("Target is " + target.tag)
        target_edoc.make_xref_edoc(out)
        self.add_text(out, " include ")
        for sub in doc_el:
            target_edoc.make_xref_sub(sub.text, out)
        self.add_text(out, " in the ST. ")
            



        # doc = self.pkgs[doc_id]
        # out.append(HTM_E.div("From " + doc.derive_title()))
          
  # <xsl:template match="cc:doc" mode="use-case">
  #   <xsl:variable name="docpath"><xsl:value-of select="concat($work-dir,'/',@ref)"/>.xml</xsl:variable>
  #   <xsl:variable name="docurl"><xsl:value-of select="//cc:*[@id=current()/@ref]/cc:url/text()"/></xsl:variable>
  #   <xsl:variable name="name"><xsl:value-of select="document($docpath)//cc:PPTitle"/><xsl:if test="not(document($docpath)//cc:PPTitle)">PP-Module for <xsl:value-of select="document($docpath)/cc:Module/@name"/></xsl:if></xsl:variable>


  #   <div class="uc_inc_pkg"> From the <a href="{$docurl}"><xsl:value-of select="$name"/></a>: </div>
  #   <xsl:for-each select="cc:ref-id">
  #     <xsl:call-template name="handle-ref-ext"> 
  #       <xsl:with-param name="ref-id" select="text()"/>
  #       <xsl:with-param name="root" select="document($docpath)/cc:*"/>
  #     </xsl:call-template>
  #   </xsl:for-each>
  # </xsl:template>


      

    def refid_use_case(self, refid_el, out):
        refid=refid_el.text
        target = self.rf("//cc:*[@id='"+refid+"']")
        start="I"
        print("BLAHBLAHBLAH: ")
        el_ancestors = refid_el.xpath("ancestor::cc:*", namespaces=NS)
        for ans in el_ancestors:
            print("BBB " + ans.tag)
        if len(refid_el.xpath("ancestor::cc:not", namespaces=NS))==1:
            start="Do NOT i"
        if target==None:
            print("Failed to find "+refid+" in a use case or rule")
            return 
        if target.tag == CC+"module":
            out_div = adopt(out,HTM_E.div({"class":"uc module"},start+"nclude the "))
            self.make_xref(target, out)
            self.add_text(out_div, " module in the ST ")
        elif target.tag == CC+"selectable":
            out_div = adopt(out,HTM_E.div({"class":"uc selectable"},start+"nclude "))
            self.make_xref(target, out_div)
            print("HANDLING ANCESTORS")
            self.add_text(out_div, " selectable in the ST ")
        elif target.tag == CC+"f-component":
            out_div = adopt(out,HTM_E.div({"class":"uc fcomp"},start+"nclude "))
            self.make_xref(target, out_div)
            self.add_text(out_div, " in the ST ")
        elif target.tag == CC+"management-function":
            print("HANDLING ANCESTORS")
            out_div = adopt(out,HTM_E.div({"class":"uc mf"},start+"nclude "))
            self.make_xref(target, out_div)
            self.add_text(out_div, " in the ST ")
        else:
            raise Exception("Can't handle: " +target.tag + " : " + refid)
  #           <xsl:template match="cc:ref-id" mode="use-case">
  #  <xsl:variable name="ref-id-txt" select="text()"/>
  #  <xsl:choose>
  #     <xsl:when test="//cc:module[@id=$ref-id-txt]">
  #       <div class="uc,module"> Include the <xsl:apply-templates select="//cc:*[@id=$ref-id-txt]" mode="make_xref"/> module in the ST </div>
  #     </xsl:when>
  #     <xsl:when test="//cc:selectable[@id=$ref-id-txt]">
  #       <xsl:apply-templates select="//cc:*[@id=$ref-id-txt]" mode="handle-ancestors">
  #         <xsl:with-param name="prev-id"><xsl:call-template name="get-prev-id"/></xsl:with-param>
  #       </xsl:apply-templates>
  #     </xsl:when>
  #     <xsl:when test="//cc:f-component[@id=$ref-id-txt]">
  #       <div class="uc_inc_fcomp">Include <xsl:apply-templates select="//cc:*[@id=$ref-id-txt]" mode="make_xref"/> in the ST </div>
  #     </xsl:when>
  #     <xsl:when test="//cc:management-function//@id=$ref-id-txt">
  #       <xsl:apply-templates select="//cc:*[@id=$ref-id-txt]" mode="handle-ancestors">
  #         <xsl:with-param name="prev-id"><xsl:call-template name="get-prev-id"/></xsl:with-param>
  #       </xsl:apply-templates>
  #       <div class="uc_mf">Include
  #       <xsl:apply-templates select="//cc:management-function[@id=$ref-id-txt]" mode="make_xref"/>
  #       in the ST</div>
  #     </xsl:when>
  #     <xsl:otherwise>
  #       <xsl:message> Failed to find <xsl:value-of select="$ref-id-txt"/> in <xsl:call-template name="genPath"/> (use case or rule)</xsl:message>
  #       <xsl:if test="./@alt">
  #         <b><i><xsl:value-of select="./@alt"/></i></b>
  #       </xsl:if>
  #     </xsl:otherwise>
  #   </xsl:choose>
  # </xsl:template>

      
      # <!--  <xsl:template match="cc:or" mode="rule"> -->
      # <!--   <table class="uc_table_or" style="border: 1px solid black"> -->
      # <!--     <tr> <td class="or_cell" rowspan="{count(cc:*)+1}">OR</td><td style="display:none"></td></tr> -->
      # <!--     <xsl:for-each select="cc:*"> -->
      # <!--       <tr><td style="width: 99%"><xsl:apply-templates select="." mode="use-case"/></td></tr> -->
      # <!--     </xsl:for-each> -->
      # <!--   </table> -->
      # <!-- </xsl:template> -->


    def then_usecase(self, then_el, out):
        table_attrs = {"class":"uc_table_or", "style":"border: 1px solid black"}
        if_el = then_el.xpath("preceding-sibling::cc:if[1]", namespaces=NS)
        if if_el is None:
            print("Found 'then' without a preceding 'if'")
            return

        attrs={"style":"width: 99%"}
        if_out = HTM_E.td(attrs)
        for if_kid in if_el:
            self.apply_use_case_templates(if_kid, if_out)
        then_td = HTM_E.td(attrs)
        self.apply_use_case_templates(then_el, then_td)
        table_out = adopt(out, HTM_E.table(table_attrs,
                                           HTM_E.tr(
                                               HTM_E.td({"class":"or_cell", "rowspan":"1"}, "IF"),
                                               if_out
                                           ),
                                           HTM_E.tr(
                                               HTM_E.td({"class":"or_cell", "rowspan":"1"}, "THEN"),
                                               then_td
                                        )))
         
  # <xsl:template match="cc:if" mode="use-case">
  #   <table class="uc_table_or" style="border: 1px solid black">
  #     <tr> <td class="or_cell" rowspan="{count(cc:*)+1}">IF</td><td style="display:none"></td></tr>
  #     <xsl:for-each select="cc:*">
  #       <tr><td style="width: 99%"><xsl:apply-templates select="." mode="use-case"/></td></tr>
  #     </xsl:for-each>
  #   </table>
  # </xsl:template>
	
  # <xsl:template match="cc:then" mode="use-case">
  #   <table class="uc_table_or" style="border: 1px solid black">
  #     <tr> <td class="or_cell" rowspan="{count(cc:*)+1}">THEN</td><td style="display:none"></td></tr>
  #     <xsl:for-each select="cc:*">
  #       <tr><td style="width: 99%"><xsl:apply-templates select="." mode="use-case"/></td></tr>
  #     </xsl:for-each>
  #   </table>
  # </xsl:template>
    