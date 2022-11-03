import lxml.etree as ET
import css_content
import pp_util
from pp_util import log
import math
import edoc
NS = {'cc': "https://niap-ccevs.org/cc/v1",
      'sec': "https://niap-ccevs.org/cc/v1/section",
      'htm': "http://www.w3.org/1999/xhtml"}

def strnull(thing):
    if thing is None:
        return ""
    else:
        return thing

def make_sort_key_stringnum(s):
    spl=s.split(".")
    return spl[0]+"."+spl[1].rjust(3)



def drawbox(ybase,boxtext,ymid, xbase=0):
    if xbase==0:
        width=150
    else:
        width=len(boxtext)*12
    ret="<text x='"+str(xbase+4)+"' fill='black' font-size='15' y='"+str(ybase+24)+"'>"
    ret+=boxtext
    ret+="</text>\n<rect x='"+str(xbase+2)+"' y='"+str(ybase+11)+"' width='"+str(width)+"' height='16' fill='none' stroke='black'/>"
    if xbase>0:
        ret+="<line x1='152' y1='"+str(ymid+17)+"' x2='"+str(xbase+1)+"' y2='"+str(ybase+17)+"' stroke='black'/>"
    

        
    return ret


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
        ret="<!DOCTYPE html>\n"
        ret=""
        ret+="<html xmlns=\"http://www.w3.org/1999/xhtml\">\n"
        ret+="    <head>\n"
        ret+="      <meta content=\"text/html;charset=utf-8\" http-equiv=\"Content-Type\"></meta>\n"
        ret+="	<meta content=\"utf-8\" http-equiv=\"encoding\"></meta>\n"
        ret+="	<title>"+self.title()+"</title>\n"
        ret+=pp_util.get_js()
        ret+="        <style type=\"text/css\">\n"
        ret+=css_content.fx_pp_css(self)
        extra_css = self.rf("//cc:extra-css")
        if extra_css is not None:
            ret+=extra_css.text+"\n"
        
        ret+="	</style>\n"
        ret+="      </head>\n"
        ret+="<body onload=\"init()\">\n"
        ret += self.fx_body_begin()
        ret += self.apply_templates([self.root])
        ret+="      </body>\n"
        ret+="    </html>\n"
        return ret

    def title(self):
        return self.root.attrib["name"]
    
    def fx_body_begin(self):
        ret=""
        comments_els = self.rfa("//cc:comment")
        if comments_els:
            ctr=0
            ret+="     <div id=\"commmentbox-\">\n"
            for comment_el in comment_els:
                id=self.derive_id(comment_el)
                ret+="         <a href=\"#"+id+"\">Comment: "+id+"</a><br/>\n"
            ret+="     </div>\n"
        ret+="   <h1 class=\"title\" style=\"page-break-before:auto;\">"
        ret+=self.title()
        ret+="</h1>"
        ret+="   <noscript>\n"
        ret+="     <h1 style=\"text-align:center; border-style: dashed; border-width: medium; border-color: red;\"\n"
        ret+="         >This page is best viewed with JavaScript enabled!</h1>\n"
        ret+="   </noscript>\n"
        ret+="   <div class=\"center\">\n"
        ret+="     <img src=\"images/niaplogo.png\" alt=\"NIAP Logo\"/> <br/>\n"
# Might think about getting rid of this and just making it part of the foreword
        ret+="     Version: "+self.rf("//cc:ReferenceTable/cc:PPVersion").text+"<br/>\n"
        ret+="     "+self.rf("//cc:ReferenceTable/cc:PPPubDate").text+"<br/>\n"
        ret+="     <b>"+self.rf("//cc:PPAuthor").text+"</b><br/>\n"
        ret+="   </div>\n"
        self.apply_templates(self.rfa("//cc:foreword"))
        ret+="<h2 style=\"page-break-before:always;\">Revision History</h2>\n"
        ret+="<table>\n"
        ret+="<tr class=\"header\"><th>Version</th><th>Date</th><th>Comment</th></tr>"
        for entry in self.rfa("//cc:RevisionHistory/cc:entry"):
            ret+="<tr><td>"
            ret+=self.handle_content(entry.find("cc:version",NS))
            ret+="</td><td>"
            ret+=self.handle_content(entry.find("cc:date",NS))
            ret+="</td><td>"
            ret+=self.handle_content(entry.find("cc:subject",NS))
            ret+="</td></tr>\n"
        ret+="</table>\n"
        ret+="<h2>Contents</h2>\n"
        ret+="<div class=\"toc\" id=\"toc\"/>\n"
        return ret


        
    def fcomp_cc_id(self, node, suffix=""):
        ret = node.attrib["cc-id"].upper() + suffix
        if "iteration" in node.attrib:
            ret += "/"+node.attrib["iteration"]
        return ret
        
        
    # def element_cc_id(self, node):
    #     fcomp = node.find("..")
    #     indexstr = str(fcomp.index(node))
    #     return self.fcomp_cc_id(fcomp, suffix="."+indexstr)
    

    def handle_content(self, node, defcon=""):
        if node is None:
            return defcon
        ret=strnull(node.text)
        for child in node:
            ret+=self.apply_templates_single(child)
            ret+=strnull(child.tail)
        return ret
            
    def handle_section(self, node, title, id):
        ret="<h5 id=\""+id+"\">"
        ret+=title
        ret+="</h5>\n"
        ret+=self.handle_section_hook(title, node)
        ret+=self.handle_content(node)
        return ret

    def handle_section_hook(self, title, node):
        if "boilerplate" in node.attrib and node.attrib["boilerplate"]=="no":
            return ""
        return self.handle_section_hook_base(title, node)

    def handle_section_hook_base(self, title, node):
        if title=="Conformance Claims":
            return self.handle_conformance_claims(node)
        elif title=="Implicity Satisfied Requirements":
            return self.handle_implicitly_satisfied_requirements()
        elif title=="Security Objectives Rationale":
            return self.handle_security_objectives_rationale(node)
        elif title=="Security Objectives for the Operational Environment":
            return self.handle_security_objectives_operational_environment()
        return ""
    
    def doctype(self):
        return "PP"
    
            
    def handle_ext_comp_defs(self):
        if self.rf("//cc:ext-comp-def") is None:
            return ""
        
        ret= "<h1 id=\"ext-comp-defs\" class=\"indexable\" data-level=\"A\">Extended Component Definitions</h1>\n"
        ret+="This appendix contains the definitions for all extended requirements specified in the " + self.doctype()+".\n"
        ret+="<h2 id=\"ext-comp-defs-bg-\" class=\"indexable\" data-level=\"2\">Extended Components Table</h2>\n"
        ret+="All extended components specified in the "+self.doctype()+" are listed in this table:<br/>\n"
        ret+="<table class=\"sort_kids_\">\n"
        ret+="<caption data-sortkey=\"#0\"><b>"
        ret+=self.create_ctr("Table","t-ext-comp_map")
        ret+=": Extended Component Definitions</b></caption>\n"
        ret+="<tr data-sortkey=\"#1\">\n"
        ret+="<th>Functional Class</th><th>Functional Components</th> </tr>\n"
        # <!-- section is compatible with the new section styles b/c the new section style is not allowed to 
        #      for sections that directly contain f-components and a-components -->
        ecdsecs = self.rx("//*[cc:ext-comp-def]")
        ecdsecs.sort(key=lambda sec: sec.attrib["title"])
        defsec = ""
        
        for sec in ecdsecs:
            ecds=sec.findall("cc:ext-comp-def", NS)
            ret+="<tr><td rowspan='"+str(len(ecds)+1)+"'>" + sec.attrib["title"] + "</td><td style='display:none;'/></tr>\n"
            for ecd in ecds:
                ret+="<tr><td>"+ecd.attrib["fam-id"] + " - " + ecd.attrib["title"]+"</td></tr>\n"
                defsec += self.handle_ecd(ecd, sec.attrib["title"])

                
        ret+="</table>\n"
        ret+="<h2 id=\"ext-comp-defs-bg\" class=\"indexable\" data-level=\"2\">Extended Component Definitions</h2>\n"
        ret+="<span class=\"sort_kids_\">\n"
        ret+="</span>\n"
        ret+=defsec
        return ret

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

    def handle_ecd(self, famnode, title):
        famId = famnode.attrib["fam-id"].lower()
        ret=""
        classid = title.split(")")[0].split("(")[1]
        ret+="<span data-sortkey='"+title+"'>"
        ret+="<h3 id=\"ext-comp-"+classid+"\" class=\"indexable\" data-level=\"3\">"
        ret+=title
        ret+="</h3>"
        desc = famnode.find("cc:class-description",NS)
        ret += self.handle_content(desc, defcon="This "+self.doctype() +\
                                   " defines the following extended components as part of the "+\
                                   classid + " class originally defined by CC Part 2:" )
        ret +="<div style=\"margin-left: 1em;\">"
        famBi = famnode.find("cc:fam-behavior",NS)
        if famBi is not None:
            ret +="<h4>Family Behavior</h4>"
            ret +="<div>"+self.handle_content(famBi)
            sfrs = self.fams_to_sfrs[famId]
            sfrs.sort(key=lambda fcom: make_sort_key_stringnum(fcom.attrib["cc-id"]))
            ret+="<h4>Component Leveling</h4>"
            ret+="<svg xmlns='http://www.w3.org/2000/svg' style='max-height: "+str(20*len(sfrs)+10)+"px;'>"
            ret+= drawbox(20*math.floor(len(sfrs)/2), famId, 0)
            ctr=0
            complevel_text=""
            sfr_mng_aud_text=""
            for sfr in sfrs:
                cc_id = self.fcomp_cc_id(sfr)
                text = cc_id.split(".")[1]
                ret+=drawbox(ctr*20, text, 20*math.floor(len(sfrs)/2), xbase=230 )
                ctr+=1
                complevel_text+="<p>"+cc_id+", " + sfr.attrib["name"]+", "+self.handle_content(sfr.find("cc:comp-lev",NS))+"</p>\n"
                sfr_mng_aud_text+=self.get_mng_aud(sfr, cc_id)
            ret+="</svg>"
            ret+=complevel_text
            ret+=sfr_mng_aud_text
            ret+="</div>"
        else:
            ret+=self.handle_content(famnode.find("cc:mod-def",NS))


        ret+="</div>"
        ret+="</span>"
        return ret


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
    def get_mng_aud(self, sfr, cc_id):
        ret="<h4>Management: "+cc_id+"</h4>\n<p>"
        ret+=self.handle_content(sfr.find("cc:management",NS),
                                 defcon="There are no management functions foreseen.")
        ret+="</p>\n<h4>Audit: "+cc_id+"</h4>\n<p>"
        ret+=self.handle_content(sfr.find("cc:audit",NS),
                                 defcon="There are no audit events foreseen.")
        ret+="</p><h4>"+cc_id+" "+sfr.attrib["name"]+"</h4>\n"
        ret+="<div style=\"margin-left: 1em;\">"
        ret+="<p>Hierarchical to: "+self.handle_content(sfr.find("cc:heirarchical-to",NS), defcon="No other components.")
        ret+="</p>\n<p>Dependencies to: "+self.handle_content(sfr.find("cc:dependencies",NS), defcon="No dependencies.")
        ret+="</p>"
        ret+="</div>"
        ctr=1
        for fel in sfr.findall("cc:f-element", NS):
            fel_id = self.fcomp_cc_id(sfr, suffix="."+str(ctr))
            ret+="<h4 id='ext-comp-"+fel_id+"-'>"+fel_id+"</h4>"
            ecd_title = fel.find("cc:ext-comp-def-title",NS)
            if ecd_title is not None:
                ret+=self.apply_templates(ecd_title)
            else:
                title=fel.find("cc:title",NS)
                if title is None:
                    raise Exception("Can't find title")
                words=self.handle_content(title)
                ret+=words
            ctr+=1
        return ret

            
    def opt_app(self,level,word,sfrs,suffix=""):
        ret="<h"+level+" id='"+word.replace(" ","-")+"-' class='indexable' data-level='"+level+"'>"+word+" Requirements</h"+level+">\n"
        if len(sfrs)==0:
            ret+="This PP-Module does not define any "+word+" SFRs.\n"
        else:
            ret+=self.handle_sparse_sfrs(sfrs)
        return ret

    def handle_optional_requirements(self):
        ret="<h1 id='optional-appendix-' class='indexable' data-level='1'>Optional SFRs</h1>\n"
        ret+=self.opt_app("2", "Strictly Optional", self.opt_sfrs)
        ret+=self.opt_app("2", "Objective", self.obj_sfrs)
        ret+=self.opt_app("2", "Implementation-based", self.impl_sfrs)
        return ret

    def handle_selection_based_requirements(self, node):
        return self.opt_app("1", "Selection-based", self.sel_sfrs)

            
    def handle_security_objectives_operational_environment(self):
        soes=self.rfa("cc:SOEs")
        if len(soes)>0:
            return """The OE of the TOE implements technical and procedural measure
to assist the TOE in correctly providing its security functionality
(which is defined by the security objectives for the TOE).
The security objectives for the OE consist of a set of statements
describing the goals that the OE should achieve.
This section defines the security objectives that are to be
addressed by the IT domain or by non-technical or procedural means.
The assumptions identified in Section 3 are incorporated as
security objectives for the environment.
"""
        else:
            return "This PP-Module does not define any objectives for the OE.\n"

        
    def create_ctr(self, ctrtype, id):
        ret="<span class=\"ctr\" data-myid=\""+id+"\" data-counter-type=\"ct-"+ctrtype+"\" id=\""+id+"\">\n"
        ret+=ctrtype + " "
        ret+="<span  class=\"counter\">"+id+"</span>\n"
        ret+="</span>\n"
        return ret
        
    def create_bibliography(self):
        ret="        <h1 id=\"appendix-bibliography\" class=\"indexable\" data-level=\"A\">Bibliography</h1>\n"
        ret+="<table>\n"
        ret+="<tr class=\"header\"> <th>Identifier</th> <th>Title</th> </tr>\n"
        # <xsl:apply-templates mode="hook" select="."/>
        entries = (self.rfa("//cc:bibliography/cc:entry") +
                   self.boilerplate.xpath("//*[@id='cc-docs']/cc:entry",namespaces=NS))
        entries.sort(key=lambda x: pp_util.flatten(x.find("cc:description", NS)))
        for entry in entries:
            pp_util.log("Entry : "+pp_util.flatten(entry.find("cc:description", NS)))
            ret+="<tr>\n"
            ret+="<td><span id=\""+self.derive_id(entry)+"\">["+entry.find("cc:tag", NS).text+"]</span></td>\n<td>"
            ret+=self.handle_content(entry.find("cc:description",NS))
            ret+="</td>\n"
            ret+="</tr>\n"
        ret+="</table>\n"
        return ret
        
    def create_acronym_listing(self):
        ret="<h1 id=\"acronyms\" class=\"indexable\" data-level=\"A\">Acronyms</h1>\n"
        ret+="<table>\n"
        ret+="<tr class=\"header\"><th>Acronym</th><th>Meaning</th></tr>\n"
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
            ret+="<tr>\n"
            ret+="<td><span class=\"term\" id=\"abbr_"+abbr+"\""
            ret+=pp_util.get_attr_or(term_el, "plural", post=lambda x:" plural=\""+x+"\"")
            ret+=pp_util.get_attr_or(term_el, "lower",  post=lambda x:" lower=\""+x+"\"")
            ret+=">"
            ret+=abbr
            ret+="</span></td>\n"
            ret+="<td><span id=\"long_abbr_"
            ret+=abbr
            ret+="\">"+full+"</span></td></tr>\n"
        ret+="</table>\n"
        return ret
            
            
    def handle_security_objectives_rationale(self, node):
        ret="""<h2 class="indexable h2" data-level="2">Security Objectives Rationale</h2>  
This section describes how the assumptions, threats, and organizational 
security policies map to the security objectives.
<table>
<caption>"""
        ret+=self.create_ctr("Table","t-sec-obj-rat");
        ret+=": Security Objectives Rationale</caption>\n"
        ret+="""<tr class="header">
        <td>Threat, Assumption, or OSP</td>
        <td>Security Objectives</td>
        <td>Rationale</td>
      </tr>"""
        objrefers=self.rx("//cc:threat/cc:objective-refer | //cc:OSP/cc:objective-refer | //cc:assumption/cc:objective-refer")
        firstcol=""
        for objrefer in objrefers:
            parent = objrefer.find("..")
            pname = parent.attrib["name"]
            ret+="<tr"
            if pname != firstcol:
                firstcol=pname
                numkids = len(parent.findall("cc:objective-refer", NS))
                ret+=" class=\"major-row\">"
                pname_wrap = pp_util.make_wrappable(pname)
                ret+="<td rowspan=\""+str(numkids)+"\">"
                ret+=pname_wrap
                ret+="</td"
            ret+="><td>"
            ret+=pp_util.make_wrappable(objrefer.attrib["ref"])
            ret+="</td><td>"
            ret+=self.handle_content(objrefer.find("cc:rationale",NS))
            ret+="</td></tr>\n"
        ret+="</table>\n"
        return ret

        
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
       
        
    def template_assumptions_cclaims_threats_OSPs_SOs_SOEs(self, node):
        ret=""
        defs = node.findall("cc:*[cc:description]", NS)
        if len(defs)>0:
            ret+="<dl>\n"
            for defined in defs:
                classtype=pp_util.localtag(defined.tag)
                name= defined.attrib["name"]
                ret+="<dt class=\""+classtype+" defined\" id=\""+name+"\">"
                ret+=name
                ret+="</dt>\n"
                ret+="<dd>"
                ret+=self.apply_templates(defined.findall("./cc:description",NS))
                ret+=self.apply_templates(defined.findall("./cc:appnote",NS))
                ret+="</dd>\n"
            ret+="</dl>\n"
        else:
            ret+="This document does not define any additional " + pp_util.localtag(node.tag)
        return ret
            
        
    def template_xref(self, node):
        ret=""
        if "to" in node.attrib:
            to=node.attrib["to"]
        else:
            to=node.attrib["g"]
        refs = self.rx(".//cc:*[@id='"+to+"']|.//sec:*[local-name()='"+to+"']")
        if len(refs)==0:
            pp_util.log("Failed to find a reference to "+to)
            ret+="<a href=\"#{@to}\" class=\"dynref\" data-post=\"{@format}\"></a>\n"
            return ret
        elif len(refs)>1:
            pp_util.log("Found multipled targets for "+ to)
        return self.make_xref(refs[0])

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
    
    def template_oldsection(self, node):
        if "id" in node.attrib:
            id=node.attrib["id"]
        else:
            id="sec_"+str(get_global_index(node))+"-"
        return self.handle_section(node,node.attrib["title"],id)
        
    def template_newsection(self, node):
        id = pp_util.localtag(node.tag)
        title = pp_util.get_attr_or(node, "title", id.replace("_", " "))
        return self.handle_section(node, title, id)

    def make_term_table(self, term_els, ignores=""):
        ret=""
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
            ret += self.template_glossary_entry(termdic[term])
        return ret
        
    def template_tech_terms(self, node):
        
        ret ="    <div class=\"no-link\">\n"
        ret+="    <h2 id='glossary' class='indexable' data-level='2'>Terms</h2>\n"
        ret+="The following sections list Common Criteria and technology terms used in this document.\n"
        ret+="    <h3 id=\"cc-terms\" class=\"indexable\" data-level=\"3\">Common Criteria Terms</h3>\n"
        ret+="    <table>\n"
        igs=""
        suppress_el = self.rf("//cc:suppress")
        if suppress_el is not None:
            igs = ","+suppress_el.text+","
        fromdoc = self.rx(".//cc:cc-terms/cc:term[text()]")
        builtin=self.boilerplate.xpath(".//cc:cc-terms/cc:term[text()]", namespaces=NS)
        ret+=self.make_term_table(fromdoc+builtin, ignores=igs)
        ret+="    </table>\n"
        ret+="    <h3 id=\"tech-terms\" class=\"indexable\" data-level=\"3\">Technical Terms</h3>\n"
        ret+="    <table style=\"width: 100%\">\n"
        ret+=self.make_term_table(node.xpath(".//cc:term[text()]", namespaces=NS))
        ret+="    </table>\n"
        ret+="    </div>\n"
        return ret
        
    def template_glossary_entry(self, node):
        full = node.attrib["full"]
        ret="        <tr>\n"
        id=full.replace(" ", "_")
        ret+="        <td><div id=\""+id+"\">"+full
        
        if "abbr" in node.attrib:
            ret+=" ("+node.attrib["abbr"]+")"
        ret+="</div></td>\n"
        ret+="        <td>\n"
        ret+=self.handle_content(node)
        ret+="</td>      </tr>\n\n"
        return ret
      
    def template_html(self, node):
        lt = pp_util.localtag(node.tag)
        ret="<"+lt
        for att in node.attrib:
            ret+=" "+att+"=\""+ pp_util.make_attr_safe(node.attrib[att])+"\""
        ret+=">"
        ret+=self.handle_content(node)
        ret+="</"+lt+">"
        return ret
        
        
    def apply_templates(self, nodelist):
        ret=""
        if nodelist is None:
            return ""
        for node in nodelist:
            ret += self.apply_templates_single(node)
        return ret


    def template_usecases(self, node):
        ret="    <dl>\n"
        ctr = 1
        for usecase in node.findall("cc:usecase", NS):
            id = usecase.attrib["id"]
            ret+="        <dt id=\""+id+"\"> [USE CASE "+str(ctr)+"] "
            ret+=usecase.attrib["title"]
            ret+="</dt>\n        <dd>"
            ret+= self.apply_templates(usecase.findall("./cc:description",NS))
            config = node.find("./cc:config", NS)
            if config is not None:
                ret+="          <p> For changes to included SFRs, selections, and assignments required for this use case, see <a href=\"#appendix-"+id+"\" class=\"dynref\"></a>.\n"
                ret+="          </p>\n"

            ret+="        \"</dd>\n"
            ctr += 1
        ret+="    </dl>\n"
        return ret
    # def get_plural(self, node):
    #     if "target-products" in node.attrib:
    #         return node.attrib["target-products"]
    #     return node.attrib["target-product"]+"s"

    # def get_short(self, node):
    #     if "short" in node.attrib:
    #         return node.attrib["short"]
    #     return self.get_plural(node)




    def handle_felement(self, node, reqid):
        ret="<div class=\"element\">\n"
        # reqid = self.element_cc_id(node)
#       <xsl:variable name="reqid"><xsl:apply-templates select="." mode="getId"/></xsl:variable>
        ret+="<div class=\"reqid\" id=\""+reqid+"\">\n"
        ret+="  <a href=\"#"+reqid+"\" class=\"abbr\">" + reqid +"</a>\n"
        ret+="</div>\n"
        ret+="<div class=\"reqdesc\">\n"
        title=node.find("cc:title", NS)
        ret+=self.handle_content(title)
        # apply_templates_single(title)
        rulez = self.rx("//cc:rule[.//cc:ref-id/text()=current()//@id]")
        notes = node.findall("cc:note" , NS)
        if len(rulez)+len(notes) > 0:
            ret+="<br/><span class=\"note-header\">Application Note: </span>\n"
            for note in notes:
                ret+=self.handle_content(note)
#         <xsl:if test="//cc:rule[.//cc:ref-id/text()=current()//@id]">
# 	  <xsl:if test="not(cc:note)">
# 	  </xsl:if>
#           <div class="validationguidelines_label">Validation Guidelines:</div>
# <!--          <p/>Selections in this requirement involve the following rule(s):<br/> -->
#           <xsl:apply-templates select="//cc:rule[.//cc:ref-id/text()=current()//@id]" mode="use-case"/>
# 	</xsl:if>
        ret+="  </div>\n"
        ret+="</div>\n"
        return ret
    
    def get_meaningful_ancestor(self, refid):
        ret = self.rx("//cc:f-element[.//@id='"+refid+"']|//cc:choice[.//@id='"+refid+"']|//cc:feature[.//@id='"+refid+"']")
        if len(ret) != 1:
            raise Exception("Should only be one thing")
        return ret[0]

    def handle_fcomponent(self, node):
        formal = self.fcomp_cc_id(node)
        ret="<div class=\"comp\" id=\""+formal+"\">\n"
        ret+="<h4>"+ formal + " "+ node.attrib["name"]+"</h4>\n"
        status=""
        objective = False
        optional = False
        # Meaningful ancestor is the key
        selecteds = {}
        ctr=0
        for f_el in node.findall(".//cc:f-element", NS):
            ctr+=1
            reqid=self.fcomp_cc_id(node, "."+str(ctr))
            ret+=self.handle_felement(f_el, reqid)
        ret+="</div>\n"
        return ret
        
    def handle_sparse_sfrs(self, sfrs):
        titles={}
        ret=""
        for sfr in sfrs:
            sec = sfr.find("..")
            title = self.get_section_title(sec)
            id = self.get_section_base_id(sec)
            if title not in titles:
                titles[title]=1
                ret+="<h4 id='"+id+"'>"+title+"</h4>\n"
            ret+=self.handle_fcomponent(sfr)
        return ret
                
        
    def apply_templates_single(self, node):
        if node is None or not isinstance(node.tag,str):
            return ""
        return self.apply_template_to_element(node)

    def apply_template_to_element(self, node):
        tag = node.tag
        if tag.startswith("{https://niap-ccevs.org/cc/v1/section}"):
            return self.template_newsection(node)
        elif tag == "{https://niap-ccevs.org/cc/v1}section":
            return self.template_oldsection(node)
        elif tag == "{https://niap-ccevs.org/cc/v1}appendix":
            return self.template_appendix(node)
        elif tag.startswith("{http://www.w3.org/1999/xhtml}"):
            return self.template_html(node)
        elif tag == "{https://niap-ccevs.org/cc/v1}xref":
            return self.template_xref(node)
        elif tag == "{https://niap-ccevs.org/cc/v1}tech-terms":
            return self.template_tech_terms(node)
        elif tag=="{https://niap-ccevs.org/cc/v1}usecases":
            return self.template_usecases(node)
        elif tag=="{https://niap-ccevs.org/cc/v1}assumptions"\
             or tag=="{https://niap-ccevs.org/cc/v1}cclaims"\
             or tag=="{https://niap-ccevs.org/cc/v1}threats"\
             or tag=="{https://niap-ccevs.org/cc/v1}OSPs"\
             or tag=="{https://niap-ccevs.org/cc/v1}SOs"\
             or tag=="{https://niap-ccevs.org/cc/v1}SOEs":
            return self.template_assumptions_cclaims_threats_OSPs_SOs_SOEs(node)
        elif tag=="{https://niap-ccevs.org/cc/v1}sfrs":
            return self.template_sfrs(node)
        elif tag=="{https://niap-ccevs.org/cc/v1}f-component" or\
             tag=="{https://niap-ccevs.org/cc/v1}ext-comp-def" or\
             tag=="{https://niap-ccevs.org/cc/v1}base-pp":
            return ""
        elif tag=="{https://niap-ccevs.org/cc/v1}f-element":
            return self.template_felement(node)
        elif tag=="{https://niap-ccevs.org/cc/v1}title": 
            return self.apply_templates(node)
        elif tag=="{https://niap-ccevs.org/cc/v1}management-function-set":
            return self.template_management_function_set(node)
        elif tag=="{https://niap-ccevs.org/cc/v1}ctr":
            return self.template_ctr(node)
        elif tag=="{https://niap-ccevs.org/cc/v1}no-link":
            ret="<span class=\"no-link\">\n"
            ret+=self.handle_content(node)
            ret+="</span>\n"
            return ret            
        elif tag=="{https://niap-ccevs.org/cc/v1}manager":
            ret="<td>"
            ret+=self.handle_content(node)
            ret+="</td>\n"
            return ret
        elif tag=="{https://niap-ccevs.org/cc/v1}text" or\
             tag=="{https://niap-ccevs.org/cc/v1}description":
            ret = self.handle_content(node)
            if ret is None:
                pp_util.log("Problem with description")
            return ret
        elif tag=="{https://niap-ccevs.org/cc/v1}selectables":
            return self.template_selectables(node)
        elif tag=="{https://niap-ccevs.org/cc/v1}assignable":
            return self.template_assignable(node)
        elif tag=="{https://niap-ccevs.org/cc/v1}int":
            return self.template_int(node)
        elif tag=="{https://niap-ccevs.org/cc/v1}_":
            return self.shortcut
        else:
            raise Exception("Can't handle: " + node.tag)


    def get_pre(self, el):
        if "pre" in el.attrib:
            return el.attrib["pre"]
        if el.tag == "{https://niap-ccevs.org/cc/v1}figure":
            return "Figure "
        return pp_util.get_attr_or(el, "ctr-type", default="Table ")
    
    def template_ctr(self, node):
        pre = pp_util.get_attr_or(node, "pre")
        ctrtype = pp_util.get_attr_or(node, "ctr-type", default=pre)
        id = self.derive_id(node)

        ret="<span class=\"ctr\" data-myid=\""+id+"\" data-counter-type=\"ct-"+ctrtype+"\" id=\""+id+"\">\n"
        ret+=self.get_pre(node)
        ret+="      <span class=\"counter\">"+id+"</span>\n"
        ret+=self.handle_content(node)
        ret+="    </span>\n"
        return ret
        
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

    def template_assignable(self, node):
        id=self.derive_id(node)
        ret="[<b>assignment</b>: <span class=\"assignable-content\" id=\""+id+"\">"
        ret+=self.handle_content(node)
        ret+="</span>]"
        return ret

    def template_appendix(self, node):
        id=self.derive_id(node)
        title=node.attrib["title"]
        ret="        <h1 id=\""+id+"\" class=\"indexable\" data-level=\"A\">"+title+"</h1>\n"
        if "boilerplate" in node.attrib and node.attrib["boilerplate"]=="no":
            return ret
        ret+=self.handle_section_hook_base(title, node)
        ret+=self.handle_content(node)
        return ret
    
    def template_selectables(self, node):
        ret="[<b>selection</b>"
        if pp_util.is_attr(node, "onlyone", "yes"):
            ret+="<b>, choose one of</b>"
        ret+=": "
        sli=""
        eli=""
        eul=""
        sep=","
        lagsep=""

        if pp_util.is_attr(node, "linebreak", "yes") \
           or node.find(".//cc:selectables", NS) is not None:
            ret+="<ul>\n"
            sep=""
            eul="</ul>"            
            sli="<li"+pp_util.get_attr_or(node, "style", post=lambda a:" style=\""+a+"\"")+">"
            eli="</li>"
        # Add the comma thing
        for selectable in node.findall("./cc:selectable",NS):
            ret+=lagsep
            ret+=sli
            id = self.derive_id(selectable)
            ret+="<span class=\"selectable-content\" id=\""+id+"\">"
            ret+=self.handle_content(selectable)
            ret+="</span>"
            ret+=eli
            lagsep=sep
        ret+="]"
        return ret
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
        
            
    def template_management_function_set(self, node):
        ret="<table class=\"mfs\" style=\"width: 100%;\">\n"
        ret+="<tr class=\"header\">\n"
        ret+="<td>#</td><td>Management Function</td>\n"
        managers = node.findall("./cc:manager", NS)
        ret+=self.apply_templates(managers)
        ret+="</tr>\n"
        ctr=0
        prefix = pp_util.get_attr_or(node, "ctr-prefix")
        deffy  = node.attrib["default"]
        for mf in node.findall("./cc:management-function", NS):
            ctr+=1
            ret+=self.make_mf_row(mf, prefix+str(ctr), managers, deffy)
        ret+="</table>\n"
        return ret

    def get_mf_id(self, node):
        if "id" in node.attrib:
            return node.attrib["id"]
        return "_mf_"+str(self.get_global_index(node))

    def make_mf_val(self, tag, node):
        if tag == "O":
            return "<div>O<span class=\"tooltiptext\">Optional</span></div>"
        elif tag =="M":
            return "<div>M<span class=\"tooltiptext\">Mandatory</span></div>"
        elif tag == "NA":
            return "<div>-<span class=\"tooltiptext\">N/A</span></div>"
        else:
            return self.handle_content(node)
    
    def make_mf_row(self, mf, prefix, managers, defval):
        mf_num = str(self.get_global_index(mf))
        mf_id = self.get_mf_id(mf)
        ret="   <tr id=\""+mf_id+"\">\n"
        ret+="     <td>"+prefix+"</td>"
        ret+="<td style=\"text-align:left\">\n"
        ret+=self.apply_templates_single(mf.find("cc:text",NS))
        ret+="</td>\n"
        for manager in managers:
            cid=manager.attrib["cid"]
            tagnode=mf.find("*[@ref='"+cid+"']")
            if tagnode == None:
                val=defval
            else:
                val= pp_util.localtag(tagnode.tag)
            ret+="         <td>\n"
            ret+=self.make_mf_val(val, tagnode)
            ret+="         </td>\n"
        ret+="   </tr>\n"
        return ret
    
    def set_underscore(self, val):
        self.shortcut = val
        
    def make_xref_section(self, node, id):
        return "<a href=\"#{"+id+"}\" class=\"dynref\">Section </a>\n"

    def make_xref_bibentry(self, node):
        id =  node.attrib["id"]
        ret="<a href=\"#"+id+"\">["
        ret+=node.find("./cc:tag", NS).text
        ret+="]</a>\n"
        return ret
        
    def make_xref(self, node):
        if node.tag.startswith("{https://niap-ccevs.org/cc/v1/section}"):
            return self.make_xref_section(node, pp_util.localtag(node.tag))
        elif node.tag == "{https://niap-ccevs.org/cc/v1}base-pp":
            return self.edocs[node.attrib["id"]].make_xref_edoc()
        elif node.tag == "{https://niap-ccevs.org/cc/v1}entry":
            return self.make_xref_bibentry(node)
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

        
