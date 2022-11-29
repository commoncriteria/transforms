import lxml.etree as ET
from lxml.builder import E
from lxml.builder import ElementMaker
import css_content
import pp_util
from pp_util import log
import math
import edoc
NS = {'cc': "https://niap-ccevs.org/cc/v1",
      'sec': "https://niap-ccevs.org/cc/v1/section",
      'htm': "http://www.w3.org/1999/xhtml"}

# SVG_NS="http://www.w3.org/2000/svg"
# SVG="{%s}"%SVG_NS
# OUT_NSMAP={None: SVG_NS}
SVG_E=ElementMaker(namespace="http://www.w3.org/2000/svg")
HTM_E=pp_util.get_HTM_E()
adopt=pp_util.adopt

apptxt=pp_util.append_text

def strnull(thing):
    if thing is None:
        return ""
    else:
        return thing

def make_sort_key_stringnum(s):
    spl=s.split(".")
    return spl[0]+"."+spl[1].rjust(3)

    
# def stringify(root):
#     return ET.tostring(root, pretty_print=True, encoding='UTF-8').decode('utf-8')

defargs={'fill':'black',
         'font-size':'15'}
boxargs={'height':'16','fill':'none','stroke':'black'}


def drawbox(parent, ybase,boxtext,ymid, xbase=0):
    if xbase==0:
        width=150
    else:
        width=len(boxtext)*12

    txt_el = SVG_E.text(boxtext, **defargs, x=str(xbase+4),y=str(ybase+24))
    parent.append(txt_el)
    rec_el = SVG_E.rect(**boxargs, x=str(xbase+2),y=str(ybase+11),width=str(width))
    parent.append(rec_el)
    if xbase>0:
        ln_el=SVG_E.line(x1='152',y1=str(ymid+17),x2=str(xbase+1),y2=str(ybase+17), stroke='black')
        parent.append(ln_el)


class generic_pp_doc(object):
    def __init__(self, root, workdir, boilerplate):
        self.root = root
        self.globaltags = {}
        self.ids = {}
        self.boilerplate = boilerplate
        self.edocs = {}
        for external in root.findall(".//cc:*[cc:git]", NS):
            self.edocs[external.attrib["id"]] = edoc.Edoc(external, workdir)
        self.sel_sfrs = {}
        self.opt_sfrs = {}
        self.obj_sfrs = {}
        self.impl_sfrs = {}
        self.fams_to_sfrs = {}
        self.man_sfrs = self.rx("//cc:f-component[not(cc:depends)]")
        for sfr in self.man_sfrs:
            self.maybe_register_sfr_with_fam(sfr)
            
        dep_sfrs = self.rx("//cc:f-component[cc:depends]")
        for sfr in dep_sfrs:
            should_register = True
            # We're just looking at the first one
            depends=sfr.find("cc:depends[1]", NS)
            if depends.find("cc:optional", NS) is not None:
                self.opt_sfrs[sfr]=1
            elif depends.find("cc:objective", NS) is not None:
                self.obj_sfrs[sfr]=1
            elif depends.find("cc:external-doc", NS) is not None:
                self.sel_sfrs[sfr]=1
            else:
                for attr in depends.attrib:
                    el = self.rf("//*[@id=\""+depends.attrib[attr]+"\"]")
                    if el is None:
                        raise Exception("Cannot find dependee for " + depends.attrib[attr])
                    elif el.tag == "{https://niap-ccevs.org/cc/v1}selectable":
                        self.sel_sfrs[sfr]=1
                    elif el.tag == "{https://niap-ccevs.org/cc/v1}feature":
                        self.impl_sfrs[sfr]=1
                    else:
                        # This really only handles modified.
                        self.handle_unknown_depends(sfr, depends.attrib[attr])
                        should_register=False
                    break
            if should_register:
                self.maybe_register_sfr_with_fam(sfr)
                        

    def handle_unknown_depends(self, sfr, attr):
        raise Exception("Can't handle this dependent sfr:"+sfr.attrib["cc-id"])
            
    def to_html(self):
        return self.start()

    def rf(self, findexp):
        return self.root.find( "."+findexp, NS)
    
    def rfa(self, findexp):
        return self.root.findall( "."+findexp, NS)

    def rx(self, xpath):
        return self.root.xpath(xpath , namespaces=NS)

    def maybe_register_sfr_with_fam(self, sfr):
        if sfr.find("cc:comp-lev",NS) is None:
            return
        if sfr.find("cc:notnew", NS) is not None:
            return
        fam = sfr.attrib["cc-id"].split(".")[0]
        if fam not in self.fams_to_sfrs:
            self.fams_to_sfrs[fam]=[]
        self.fams_to_sfrs[fam].append(sfr)
    
    def start(self):
        head = HTM_E.head(
                HTM_E.meta({"content":"text/html;charset=utf-8", "http-equiv":"Content-Type"}),
                HTM_E.meta({"content":"utf-8","http-equiv":"encoding"}),
                HTM_E.title(self.title())
        )
        ret = HTM_E.html(head)
        pp_util.add_js(head)
        css_text = css_content.fx_pp_css(self)
        extra_css = self.rf("//cc:extra-css")
        if extra_css is not None:
            css_text=extra_css.text+"\n"
        style=HTM_E.style({"type":"text/css"},css_text)
        head.append(style)
        body=HTM_E.body({"onload":"init()"})
        ret.append(body)
        self.fx_body_begin(body)
        self.apply_templates([self.root], body)
        return ret

    def title(self):
        return self.root.attrib["name"]

    def handle_comments(self, body):
        comments_els = self.rfa("//cc:comment")
        if not comments_els:
            return
        div=HTM_E.div({"id":"commentbox-"})
        ctr=0
        for comment_el in comment_els:
            id=self.derive_id(comment_el)
            div.append(HTM_E.a({"href":"#"+id},"Comment: " + id))
            div.append(HTM_E.br())
        return ret
    
    def fx_body_begin(self, body):
        self.handle_comments(body)
        body.append(HTM_E.h1({"class":"title", "style":"page-break-before:auto;"}, self.title()))
        body.append(HTM_E.noscript(HTM_E.h1, {"style":"text-align:center; border-style: dashed; border-width: medium; border-color: red;"},"This page is best viewed with JavaScript enabled!"))
        body.append(HTM_E.div({"class":"center"},
                              HTM_E.img({"src":"images/niaplogo.png","alt":"NIAP Logo"}),
                              "Version: "+self.rf("//cc:ReferenceTable/cc:PPVersion").text,
                              HTM_E.br(),
                              "     "+self.rf("//cc:ReferenceTable/cc:PPPubDate").text,
                              HTM_E.br(),
                              HTM_E.b(self.rf("//cc:PPAuthor").text),
                              HTM_E.br()))
        self.apply_templates(self.rfa("//cc:foreword"), body)
        rev_his = HTM_E.h2({"style":"page-break-before:always;"},"Revision History")
        body.append(rev_his)
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
        body.append(HTM_E.h2("Contents"))
        body.append(HTM_E.div({"class":"toc","id":"toc"}))
        return 

        
    def fcomp_cc_id(self, node, suffix=""):
        ret = node.attrib["cc-id"].upper() + suffix
        if "iteration" in node.attrib:
            ret += "/"+node.attrib["iteration"]
        return ret
        
        
    # def element_cc_id(self, node):
    #     fcomp = node.find("..")
    #     indexstr = str(fcomp.index(node))
    #     return self.fcomp_cc_id(fcomp, suffix="."+indexstr)

                
    def handle_content(self, node, parent,defcon=""):
        if node is None:
            apptxt(parent, defcon)
            return
        apptxt(parent, node.text)
        for child in node:
            self.apply_templates_single(child,parent)
            apptxt(parent,child.tail)
            
    def handle_section(self, node, title, id, parent):
        title_el = HTM_E.h2({"id":id}, title)
        parent.append(title_el)
        self.handle_section_hook(title, node, parent)
        print("Handling "+title)
        self.handle_content(node, parent)

    def handle_section_hook(self, title, node, parent):
        if "boilerplate" in node.attrib and node.attrib["boilerplate"]=="no":
            return 
        self.handle_section_hook_base(title, node, parent)

    def handle_section_hook_base(self, title, node, parent):
        if title=="Conformance Claims":
            self.handle_conformance_claims(node, parent)
        elif title=="Implicity Satisfied Requirements":
            self.handle_implicitly_satisfied_requirements(parent)
        elif title=="Security Objectives Rationale":
            self.handle_security_objectives_rationale(node, parent)
        elif title=="Security Objectives for the Operational Environment":
            self.handle_security_objectives_operational_environment(parent)
    
    def doctype(self):
        return "PP"
    
            
    def handle_ext_comp_defs(self ,par):
        if self.rf("//cc:ext-comp-def") is None:
            return ""
        par.append(HTM_E.h1({"id":"ext-comp-defs","class":"indexable","data-level":"A"},"Extended Component Definitions"))
        apptxt(par, "This appendix contains the definitions for all extended requirements specified in the " + self.doctype()+".\n")
        par.append(HTM_E.h2({"id":"ext-comp-defs-bg-","class":"indexable","data-level":"2"},"Extended Components Table"))
        apptxt(par,"All extended components specified in the "+self.doctype()+" are listed in this table:")
        par.append(HTM_E.br())
        table = adopt(par, HTM_E.table({"class":"sort_kids_"}))
        caption = adopt(table, HTM_E.captions({"data-sortkey":"#0"}))
        b_el = adopt(caption, HTM_E.b())
        self.create_ctr("Table","t-ext-comp_map", b_el)
        apptxt(b_el, ": Extended Component Definitions")
        table.append(HTM_E.tr({"data-sortkey":"#1"},
                              HTM_E.th("Functional Class"),
                              HTM_E.th("Functional Components")))
        
        # <!-- section is compatible with the new section styles b/c the new section style is not allowed to 
        #      for sections that directly contain f-components and a-components -->
        ecdsecs = self.rx("//*[cc:ext-comp-def]")
        ecdsecs.sort(key=lambda sec: sec.attrib["title"])
        defsec = HTM_E.div()
        for sec in ecdsecs:
            ecds=sec.findall("cc:ext-comp-def", NS)
            table.append(HTM_E.tr(HTM_E.td({"rowspan":str(len(ecds)+1)}, sec.attrib["title"]), HTM_E.td({"style":"display:none;"})))
            # ret+="<tr><td rowspan='"+str(len(ecds)+1)+"'>" + sec.attrib["title"] + "</td><td style='display:none;'/></tr>\n"
            for ecd in ecds:
                table.append(HTM_E.tr( HTM_E.td(ecd.attrib["fam-id"]+ " - " + ecd.attrib["title"])))
                # ret+="<tr><td>"+ecd.attrib["fam-id"] + " - " + ecd.attrib["title"]+"</td></tr>\n"
                self.handle_ecd(ecd, sec.attrib["title"], defsec)
        par.append(HTM_E.h2({"id":"ext-comp-defs-bg","class":"indexable","data-level":"2"}, "Extended Component Definitions"))
        par.append(HTM_E.span({"class":"sort_kids_"}))
        par.append(defsec)

        #         <xsl:call-template name="RecursiveGrouping"><xsl:with-param name="list" select="//*[cc:ext-comp-def]"/></xsl:call-template>
        #         ret+="</table>\n"

        #         <xsl:call-template name="RecursiveGrouping">
        #       <xsl:with-param name="list" select="//*[cc:ext-comp-def]"/>
        #       <xsl:with-param name="fake_mode" select="'sections'"/>
        #     </xsl:call-template>
        # <!--
        #     <xsl:variable name="alltitles"><xsl:for-each select="//*[./cc:ext-comp-def]/@title"><xsl:sort/><xsl:value-of select="."/>@@</xsl:for-each></xsl:variable>

        #     <xsl:call-template name="extcompdef_no_repeats">
        #       <xsl:with-param name="titles" select="$alltitles"/>
        #     </xsl:call-template> -->

    def handle_ecd(self, famnode, title, par):
        famId = famnode.attrib["fam-id"].lower()
        classid = title.split(")")[0].split("(")[1]
        span=adopt(par, HTM_E.span({"data-sortkey":title}))
        span.append(HTM_E.h3({"id":"ext-comp-"+classid,"class":"indexable","data-level":"3"},title))
        desc = famnode.find("cc:class-description",NS)
        self.handle_content(desc, span, defcon="This "+self.doctype() +\
                            " defines the following extended components as part of the "+\
                            classid + " class originally defined by CC Part 2:" )
        div = adopt(span, HTM_E.div({"style":"margin-left: 1em;"}))
        famBi = famnode.find("cc:fam-behavior",NS)
        if famBi is not None:
            div.append(HTM_E.h4("Family Behavior"))
            div_fam = adopt(div, HTM_E.div())
            self.handle_content(famBi, div_fam)
            sfrs = self.fams_to_sfrs[famId]
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




#           <xsl:variable name="dcount"
#             select="count(//cc:f-component[starts-with(@cc-id, $famId) and not(@notnew)][not(ancestor::cc:modified-sfrs) and (cc:comp-lev)])"/>
#           <svg xmlns="http://www.w3.org/2000/svg" style="{concat('max-height: ', 20*$dcount+10, 'px;')}">
#               <xsl:call-template name="drawbox">
#                 <xsl:with-param name="ybase" select="20*floor($dcount div 2)"/>
#                 <xsl:with-param name="boxtext" select="@fam-id"/>
#               </xsl:call-template>
#               <xsl:for-each select="//cc:f-component[starts-with(@cc-id, $famId)and not(@notnew)][not(ancestor::cc:modified-sfrs) and (cc:comp-lev)]">
#                 <xsl:variable name="box_text"><!--
#                   --><xsl:value-of select="substring-after(@cc-id, '.')"/><!--
#                   --><xsl:if test="@iteration">/<xsl:value-of select="@iteration"/></xsl:if></xsl:variable>
#                 <xsl:call-template name="drawbox">
#                   <xsl:with-param name="ybase" select="( position() - 1)* 20"/>
#                   <xsl:with-param name="boxtext" select="$box_text"/>
#                   <xsl:with-param name="xbase" select="230"/>
#                   <xsl:with-param name="ymid" select="20*floor($dcount div 2)"/>
#                 </xsl:call-template>
#               </xsl:for-each>
#           </svg>
# <!--          </xsl:element> -->
#         </xsl:when>
#         <xsl:otherwise>
#           <xsl:apply-templates select="cc:mod-def"/>
#         </xsl:otherwise>
#       </xsl:choose>

# 	<!-- All Component descriptions --> 
#       <xsl:for-each select="//cc:f-component[starts-with(@cc-id, $famId) and not(@notnew)][not(ancestor::cc:modified-sfrs) and (cc:comp-lev)]">
#          <xsl:variable name="upId"><xsl:apply-templates select="." mode="getId"/></xsl:variable>
#          <p><xsl:value-of select="$upId"/>,
#              <xsl:value-of select="@name"/>,
#              <xsl:apply-templates select="cc:comp-lev" mode="reveal"/>
#          </p>
#       </xsl:for-each>
    def get_mng_aud(self, sfr, cc_id, par):
        par.append(HTM_E.h4("Management: "+cc_id))
        p_el = adopt(par, HTM_E.p())
        self.handle_content(sfr.find("cc:management",NS),p_el,
                            defcon="There are no management functions foreseen.")
        par.append(HTM_E.h4("Audit: "+cc_id))
        p_el = adopt(par, HTM_E.p())
        self.handle_content(sfr.find("cc:audit",NS),p_el,
                            defcon="There are no audit events foreseen.")
        par.append(HTM_E.h4(cc_id+" "+sfr.attrib["name"]+": "+cc_id))
        div = adopt(par, HTM_E.div({"style":"margin-left: 1em;"}))
        p_el = adopt(div, HTM_E.p("Hierarchical to: "))
        self.handle_content(sfr.find("cc:heirarchical-to",NS), p_el, defcon="No other components.")
        p_el = adopt(div, HTM_E.p("Dependencies to: "))
        self.handle_content(sfr.find("cc:dependencies",NS), p_el, defcon="No dependencies.")
        ctr=1
        for fel in sfr.findall("cc:f-element", NS):
            fel_id = self.fcomp_cc_id(sfr, suffix="."+str(ctr))
            par.append(HTM_E.h4({"id":"ext-comp-"+fel_id+"-"},fel_id))
            ecd_title = fel.find("cc:ext-comp-def-title",NS)
            if ecd_title is not None:
                self.apply_templates(ecd_title, par)
            else:
                title=fel.find("cc:title",NS)
                if title is None:
                    raise Exception("Can't find title")
                self.handle_content(title, par)
            ctr+=1
            
    def opt_app(self,level,word,sfrs, par, suffix=""):
        par.append(HTM_E.h4({"id":word.replace(" ","-")+"-","class":"indexable","data-level":"level"},word+" Requirements"))
        if len(sfrs)==0:
            apptxt(par, "This PP-Module does not define any "+word+" SFRs.\n")
        else:
            self.handle_sparse_sfrs(sfrs, par)


    def handle_optional_requirements(self, par):
        par.append(HTM_E.h1({"id":"optional-appendix-","class":"indexable", "data-level":"1"},"Optional SFRs"))
        self.opt_app("2", "Strictly Optional", self.opt_sfrs, par)
        self.opt_app("2", "Objective", self.obj_sfrs, par)
        self.opt_app("2", "Implementation-based", self.impl_sfrs, par)

    def handle_selection_based_requirements(self, node, par):
        return self.opt_app("1", "Selection-based", self.sel_sfrs, par)

            
    def handle_security_objectives_operational_environment(self, parent):
        soes=self.rfa("cc:SOEs")
        if len(soes)>0:
            apptxt(parent,"""The OE of the TOE implements technical and procedural measure
to assist the TOE in correctly providing its security functionality
(which is defined by the security objectives for the TOE).
The security objectives for the OE consist of a set of statements
describing the goals that the OE should achieve.
This section defines the security objectives that are to be
addressed by the IT domain or by non-technical or procedural means.
The assumptions identified in Section 3 are incorporated as
security objectives for the environment.
""")
        else:
            apptxt(parent, "This PP-Module does not define any objectives for the OE.")

        
    def create_ctr(self, ctrtype, id ,parent):
        span = adopt(parent, HTM_E.span({"class":"ctr",
                                         "data-myid":id,
                                         "data-counter-type":"ct-"+ctrtype,
                                         "id":id}, ctrtype,
                                        HTM_E.span({"class":"counter"},id)
                                        ))
        
    def create_bibliography(self, par):
        par.append(HTM_E.h1({"id":"appendix-bibliography","class":"indexable","data-level":"A"},"Bibliography"))
        table = adopt(par, HTM_E.table())
        table.append(HTM_E.tr(HTM_E.th("Identifier"),HTM_E.th("Title")))
        entries = (self.rfa("//cc:bibliography/cc:entry") +
                   self.boilerplate.xpath("//*[@id='cc-docs']/cc:entry",namespaces=NS))
        entries.sort(key=lambda x: pp_util.flatten(x.find("cc:description", NS)))
        for entry in entries:
            pp_util.log("Entry : "+pp_util.flatten(entry.find("cc:description", NS)))
            tr = adopt(table, HTM_E.tr())
            td = adopt(tr, HTM_E.td( HTM_E.span({"id":self.derive_id(entry)},"["+entry.find("cc:tag", NS).text+"]")))
            self.handle_content(entry.find("cc:description",NS), td)
        
    def create_acronym_listing(self, par):
        par.append(HTM_E.h1({"id":"acronyms","class":"indexable","data-level":"A"},"Acronyms"))
        table = adopt(par, HTM_E.table())
        table.append(HTM_E.tr(HTM_E.th("Acronym"), HTM_E.th("Meaning")))
        suppress_el=self.rf("//cc:suppress")
        if suppress_el is None:
            suppress_list=[]
        else:
            suppress_list=suppress.text.split(",")
        term_els=self.rfa("//cc:term[@abbr]")+self.boilerplate.findall("//cc:cc-terms/cc:term[@abbr]", NS)
        term_els.sort(key=lambda t_el:t_el.attrib["full"].upper())
        for term_el in term_els:
            full=term_el.attrib["full"]
            abbr=term_el.attrib["abbr"]            
            if full in suppress_list:
                continue
            tr = adopt(table, HTM_E.tr())

            attrs = {"class":"term", "id":"abbr_"+abbr}
            pp_util.maybe_add_attr(attrs, term_el, "plural")
            pp_util.maybe_add_attr(attrs, term_el, "lower")
            tr.append(HTM_E.td(HTM_E.span(attrs, abbr)))
            tr.append(HTM_E.td(HTM_E.span({"id":"long_abbr_abbr"}, full)))
            
            
    def handle_security_objectives_rationale(self, node, parent):
        parent.append(HTM_E.h2({"class":"indexable h2","data-level":"2"},
                               "Security Objectives Rationale"))
        apptxt(parent, """This section describes how the assumptions, threats, and organizational 
security policies map to the security objectives.""")
        table = adopt(parent, HTM_E.table())
        caption = adopt(table, HTM_E.caption())
        self.create_ctr("Table","t-sec-obj-rat", caption);
        apptxt(caption, ": Security Objectives Rationale")
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
            apptxt(parent, "This document does not define any additional " + pp_util.localtag(node.tag))
            
        
    def template_xref(self, node, parent):
        attrs = {}
        if "to" in node.attrib:
            to=node.attrib["to"]
        else:
            to=node.attrib["g"]
        if "format" in node.attrib:
            attrs["data-post"]=node.attrib["format"]
        refs = self.rx(".//cc:*[@id='"+to+"']|.//sec:*[local-name()='"+to+"']")
        if len(refs)==0:
            pp_util.log("Failed to find a reference to "+to)
            parent.append( HTM_E.a(attrs))
            return 
        elif len(refs)>1:
            pp_util.log("Found multipled targets for "+ to)
        self.make_xref(refs[0], parent)

    def get_list_of(self, fulltag):
        if fulltag in self.globaltags:
            return self.globaltags[fulltag]
        nodes = self.root.findall(".//"+fulltag)
        self.globaltags[fulltag] = nodes
        return nodes

    def get_global_index(self, node):
        allof = self.get_list_of(node.tag)
        return allof.index(node)

    def derive_id(self, node):
        if "id" in node.attrib:
            return node.attrib["id"]
        return pp_util.localtag(node.tag)+"_"+str(self.get_global_index(node))+"-"
    
    def get_section_base_id(self, node):
        if node.tag == "{https://niap-ccevs.org/cc/v1}section":
            if "id" in node.attrib:
                return node.attrib["id"]
            id="sec_"+str(get_global_index(node))+"-"
            return id
        else:
            return node.tag.split("}")[1]
        
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
        divy.append(HTM_E.h2({"id":"glossary", "class":"indexable", "data-level":"2"}, "Terms"))
        apptxt(divy,"The following sections list Common Criteria and technology terms used in this document.")
        divy.append(HTM_E.h3({"id":"cc-terms","class":"indexable","data-level":"3"},"Common Criteria Terms"))
        tabley = HTM_E.table()
        divy.append(tabley)
        igs=""
        suppress_el = self.rf("//cc:suppress")
        if suppress_el is not None:
            igs = ","+suppress_el.text+","
        fromdoc = self.rx(".//cc:cc-terms/cc:term[text()]")
        builtin=self.boilerplate.xpath(".//cc:cc-terms/cc:term[text()]", namespaces=NS)
        self.make_term_table(fromdoc+builtin, tabley, ignores=igs,)
        divy.append(HTM_E.h3({"id":"tech-terms","class":"indexable","data-level":"3"},"Technical Terms"))
        tabley = HTM_E.table({"style":"width: 100%"})
        divy.append(tabley)
        self.make_term_table(node.xpath(".//cc:term[text()]", namespaces=NS), tabley)
        
    def template_glossary_entry(self, node, parent):
        full = node.attrib["full"]
        tr = HTM_E.tr()
        parent.append(tr)
        id=full.replace(" ", "_")
        text = "        <td><div id=\""+id+"\">"+full
        
        if "abbr" in node.attrib:
            text+=" ("+node.attrib["abbr"]+")"
        tr.append(HTM_E.td(HTM_E.div({"id":id}, text)))
        deftd = HTM_E.td()
        self.handle_content(node, deftd)
        tr.append(deftd)

      
    def template_html(self, node ,parent):
        tag = pp_util.localtag(node.tag)
        html_el = ET.Element(tag, node.attrib)
        parent.append(html_el)
        self.handle_content(node, html_el)

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
                dd.append(HTM.p("For changes to included SFRs, selections, and assignments required for this use case, see", HTM.a({"href":"#appendix-"+id, "class":"dynref"}),"."))
            ctr += 1
    # def get_plural(self, node):
    #     if "target-products" in node.attrib:
    #         return node.attrib["target-products"]
    #     return node.attrib["target-product"]+"s"

    # def get_short(self, node):
    #     if "short" in node.attrib:
    #         return node.attrib["short"]
    #     return self.get_plural(node)




    def handle_felement(self, node, reqid, par):
        div_fel=adopt(par, HTM_E.div({"class":"element"}))
        div_fel.append(
            HTM_E.div({"class":"reqid","id":reqid},
                      HTM_E.a({"href":"#"+reqid,"class":"abbr"}, reqid))
        )
        div_reqdesc = adopt(div_fel, HTM_E.div({"class":"reqdesc"}))
        title=node.find("cc:title", NS)
        self.handle_content(title, div_reqdesc)
        # apply_templates_single(title)
        rulez = self.rx("//cc:rule[.//cc:ref-id/text()=current()//@id]")
        notes = node.findall("cc:note" , NS)
        if len(rulez)+len(notes) > 0:
            div_reqdesc.append(HTM_E.br())
            div_reqdesc.append(HTM_E.span({"class":"note-header"},"Application Note: "))
            for note in notes:
                self.handle_content(note, div_reqdesc)
#         <xsl:if test="//cc:rule[.//cc:ref-id/text()=current()//@id]">
# 	  <xsl:if test="not(cc:note)">
# 	  </xsl:if>
#           <div class="validationguidelines_label">Validation Guidelines:</div>
# <!--          <p/>Selections in this requirement involve the following rule(s):<br/> -->
#           <xsl:apply-templates select="//cc:rule[.//cc:ref-id/text()=current()//@id]" mode="use-case"/>
# 	</xsl:if>
    
    def get_meaningful_ancestor(self, refid):
        ret = self.rx("//cc:f-element[.//@id='"+refid+"']|//cc:choice[.//@id='"+refid+"']|//cc:feature[.//@id='"+refid+"']")
        if len(ret) != 1:
            raise Exception("Should only be one thing")
        return ret[0]

    def handle_fcomponent(self, node, par):
        formal = self.fcomp_cc_id(node)
        div = adopt(par, HTM_E.div({"class":"comp", "id":formal}))
        div.append(HTM_E.h4(formal + " "+ node.attrib["name"]))
        status=""
        objective = False
        optional = False
        # Meaningful ancestor is the key
        selecteds = {}
        ctr=0
        for f_el in node.findall(".//cc:f-element", NS):
            ctr+=1
            reqid=self.fcomp_cc_id(node, "."+str(ctr))
            self.handle_felement(f_el, reqid,div)
        
    def handle_sparse_sfrs(self, sfrs, par):
        titles={}
        for sfr in sfrs:
            sec = sfr.find("..")
            title = self.get_section_title(sec)
            id = self.get_section_base_id(sec)
            if title not in titles:
                titles[title]=1
                par.append(HTM_E.h4({"id":id}, title))
            self.handle_fcomponent(sfr, par)

                
        
    def apply_templates_single(self, node, parent):
        # Returns None if 
        if node is None or not isinstance(node.tag,str):
            return False
        self.apply_template_to_element(node, parent)
        return True

    def apply_template_to_element(self, node, parent):
        tag = node.tag
        if tag.startswith("{https://niap-ccevs.org/cc/v1/section}"):
            return self.template_newsection(node, parent)
        elif tag == "{https://niap-ccevs.org/cc/v1}section":
            return self.template_oldsection(node, parent)
        elif tag == "{https://niap-ccevs.org/cc/v1}appendix":
            return self.template_appendix(node, parent)
        elif tag.startswith("{http://www.w3.org/1999/xhtml}"):
            print("Handling " + tag)
            return self.template_html(node, parent)
        elif tag == "{https://niap-ccevs.org/cc/v1}xref":
            return self.template_xref(node, parent)
        elif tag == "{https://niap-ccevs.org/cc/v1}tech-terms":
            return self.template_tech_terms(node, parent)
        elif tag=="{https://niap-ccevs.org/cc/v1}usecases":
            return self.template_usecases(node, parent)
        elif tag=="{https://niap-ccevs.org/cc/v1}assumptions"\
             or tag=="{https://niap-ccevs.org/cc/v1}cclaims"\
             or tag=="{https://niap-ccevs.org/cc/v1}threats"\
             or tag=="{https://niap-ccevs.org/cc/v1}OSPs"\
             or tag=="{https://niap-ccevs.org/cc/v1}SOs"\
             or tag=="{https://niap-ccevs.org/cc/v1}SOEs":
            return self.template_assumptions_cclaims_threats_OSPs_SOs_SOEs(node, parent)
        elif tag=="{https://niap-ccevs.org/cc/v1}sfrs":
            return self.template_sfrs(node, parent)
        elif tag=="{https://niap-ccevs.org/cc/v1}f-component" or\
             tag=="{https://niap-ccevs.org/cc/v1}ext-comp-def" or\
             tag=="{https://niap-ccevs.org/cc/v1}base-pp":
            return ""
        elif tag=="{https://niap-ccevs.org/cc/v1}f-element":
            return self.template_felement(node, parent)
        elif tag=="{https://niap-ccevs.org/cc/v1}title": 
            return self.apply_templates(node, parent)
        elif tag=="{https://niap-ccevs.org/cc/v1}management-function-set":
            return self.template_management_function_set(node, parent)
        elif tag=="{https://niap-ccevs.org/cc/v1}ctr":
            self.template_ctr(node, parent)
        elif tag=="{https://niap-ccevs.org/cc/v1}no-link":
            span=adopt(parent, HTM_E.span({"class":"no-link"}))
            self.handle_content(node, parent, span)
        elif tag=="{https://niap-ccevs.org/cc/v1}manager":
            td = adopt(parent, HTM_E.td())
            self.handle_content(node, td)
            return
        elif tag=="{https://niap-ccevs.org/cc/v1}text" or\
             tag=="{https://niap-ccevs.org/cc/v1}description":
            if self.handle_content(node, parent) is None:
                pp_util.log("Problem with description")
        elif tag=="{https://niap-ccevs.org/cc/v1}selectables":
            self.template_selectables(node, parent)
        elif tag=="{https://niap-ccevs.org/cc/v1}assignable":
            self.template_assignable(node, parent)
        elif tag=="{https://niap-ccevs.org/cc/v1}int":
            self.template_int(node, parent)
        elif tag=="{https://niap-ccevs.org/cc/v1}_":
            self.shortcut
        else:
            raise Exception("Can't handle: " + node.tag)


    def get_pre(self, el):
        if "pre" in el.attrib:
            return el.attrib["pre"]
        if el.tag == "{https://niap-ccevs.org/cc/v1}figure":
            return "Figure "
        return pp_util.get_attr_or(el, "ctr-type", default="Table ")
    
    def template_ctr(self, node, par):
        pre = pp_util.get_attr_or(node, "pre")
        ctrtype = pp_util.get_attr_or(node, "ctr-type", default=pre)
        id = self.derive_id(node)

        span = adopt(par, HTM_E.span({"class":"ctr","data-myid":id,"data-counter-type":"ct-"+ctrtype,
                                      "id":id}))
        apptxt(span,self.get_pre(node))
        span.append(HTM_E.span({"class":"counter"}, id))
        self.handle_content(node, span)

        
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
        apptxt(par,"[")
        par.append(HTM_E.b("assignment"))
        apptxt(par,": ")
        span=adopt(par, HTM_E.span({"class":"assignable-content","id":id}))
        self.handle_content(node, span)
        apptxt(par,"]")

    def template_appendix(self, node, parent):
        id=self.derive_id(node)
        title=node.attrib["title"]
        parent.append(HTM_E.h1({"id":id, "class":"indexable", "data-level":"A"},title))
        if "boilerplate" in node.attrib and node.attrib["boilerplate"]=="no":
            return
        self.handle_section_hook_base(title, node, parent)
        self.handle_content(node, parent)

    
    def template_selectables(self, node, par):
        apptxt(par,"[")
        par.append(HTM_E.b("selection"))
        if pp_util.is_attr(node, "onlyone", "yes"):
            par.append(HTM_E.b(", choose one of"))
        apptxt(par, ": ")
        sep=", "
        extraclass=""
        if pp_util.is_attr(node, "linebreak", "yes") \
           or node.find(".//cc:selectables", NS) is not None:
            sep=None
            extraclass=" linebreak-sel"

        # Add the comma thing
        lagsep=None
        for selectable in node.findall("./cc:selectable",NS):
            id = self.derive_id(selectable)
            span = adopt(par,HTM_E.span({"class":"selectable-content"+extraclass, "id":id}))
            self.handle_content(selectable, span)
            apptxt(par,lagsep)
            lagsep=sep
        apptxt(par,"]")
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


    def get_mf_id(self, node):
        if "id" in node.attrib:
            return node.attrib["id"]
        return "_mf_"+str(self.get_global_index(node))

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
        mf_id = self.get_mf_id(mf)
        tr = adopt(par, HTM_E.tr({"id":mf_id}))
        tr.append(HTM_E.td(prefix))
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
    
    def set_underscore(self, val):
        self.shortcut = val
        
    def make_xref_section(self, node, id):
        return "<a href=\"#{"+id+"}\" class=\"dynref\">Section </a>\n"

    def make_xref_bibentry(self, node, parent):
        txt = "["+node.find("./cc:tag", NS).text+"]"
        anchor="#"+node.attrib["id"]
        parent.append(E.a(txt, href=anchor))
        
    def make_xref(self, node, parent):
        if node.tag.startswith("{https://niap-ccevs.org/cc/v1/section}"):
            self.make_xref_section(node, pp_util.localtag(node.tag), parent)
        elif node.tag == "{https://niap-ccevs.org/cc/v1}base-pp":
            self.edocs[node.attrib["id"]].make_xref_edoc(parent)
        elif node.tag == "{https://niap-ccevs.org/cc/v1}entry":
            self.make_xref_bibentry(node, parent)
            # self.handle_content(node,parent)
        else:
            raise Exception("Cannot handle: " + node.tag)

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
    #         proot = self.edocs[node.attrib["id"]]
    #         ret+=proot.find(".//cc:PPTitle",NS).text
    #         version=proot.find(".//cc:PPVersion",NS).text
    #     ret+="Package, version "
    #     ret+=version
    #     ret+="</a> Conformant"

        
