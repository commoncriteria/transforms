import lxml.etree as ET
import css_content
import pp_util
import edoc
NS = {'cc': "https://niap-ccevs.org/cc/v1",
      'sec': "https://niap-ccevs.org/cc/v1/section",
      'htm': "http://www.w3.org/1999/xhtml"}



        
class generic_pp_doc(object):
    def __init__(self, root, workdir, output, boilerplate):
        self.root = root
        self.out = open(output, "w+")
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
        self.man_sfrs = self.rx("//cc:f-component[not(cc:depends)]")

        for man_sfr in self.man_sfrs:
            pp_util.log("Man SFR: " + man_sfr.attrib["cc-id"])
        
        dep_sfrs = self.rx("//cc:f-component[cc:depends]")
        for sfr in dep_sfrs:
            # We're just looking at the first one
            for depends in sfr.findall("cc:depends[1]", NS):
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
                            self.handle_unknown_depends(sfr, depends.attrib[attr])

    def handle_unknown_depends(self, sfr, attr):
        raise Exception("Can't handle this dependent sfr:"+sfr.attrib["cc-id"])

            
    def to_html(self):
        self.start()
        pp_util.log("And now I'm done")
        self.out.close()

    def ol(self, str):
        if str is not None:
            self.out.write(str)
            self.out.write("\n")

    def o(self, str):
        if str is not None:
            self.out.write(str)

    def rf(self, findexp):
        return self.root.find( "."+findexp, NS)
    
    def rfa(self, findexp):
        return self.root.findall( "."+findexp, NS)

    def rx(self, xpath):
        return self.root.xpath(xpath , namespaces=NS)
    
    def fx_init_js(self):
        self.ol("""// <![CDATA[
        // Called on page load to parse URL parameters and perform actions on them.
        function init(){
            if(getQueryVariable("expand") == "on"){
              expand();
            }
            var aa;
            var brk_els = document.getElementsByClassName("dyn-abbr");
            //
            for(aa=0; aa!=brk_els.length; aa++){
                var abbr = brk_els[aa].firstElementChild.getAttribute("href").substring(1);
                var el = document.getElementById("long_"+abbr)
                if (el==null) {
                     console.log("Could not find 'long_abbr_'"+abbr);
                     continue;
                }
                var abbr_def = el.textContent;
                brk_els[aa].setAttribute("title", abbr_def);
            }
        }
        // ]]>""")


    def fx_pp_js(self):
        self.ol("""<script 
 src='https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.1/MathJax.js?config=TeX-AMS-MML_HTMLorMML'
 type="text/javascript"></script>
                <script type="text/x-mathjax-config">
                    MathJax.Hub.Config({
                    extensions: ["tex2jax.js"],
                    jax: ["input/TeX", "output/HTML-CSS"],
                    showMathMenu: false,
                    tex2jax: {
                      inlineMath: [ ['$','$'], ["\\(","\\)"] ],
                      displayMath: [ ['$$','$$'], ["\\[","\\]"] ],
                      processEscapes: true
                    },
                    styles: {
        
                        ".MathJax_Display": {
                        "text-align": "left !important",
                        margin:       "0em 0em !important"
                    }}
                    });
                </script>
                <script type="text/javascript">
""")
        self.fx_init_js()
        self.ol("""// <![CDATA[
        const AMPERSAND=String.fromCharCode(38);
        
        // Pass a URL variable to this function and it will return its value
        function getQueryVariable(variable)
        {
            var query = window.location.search.substring(1);
            var vars = query.split(AMPERSAND);
            for (var i=0;i!=vars.length;i++) {
                var pair = vars[i].split("=");
                if(pair[0] == variable){return pair[1];}
            }
            return(false);
        }
        
        
        //    Expands all evaluation activities
        function expand(){
            var ap = document.getElementsByClassName('activity_pane');
            for (var ii = 0; ii!=ap.length; ii++) {
                ap[ii].classList.remove('hide');
            }
        }
        
        // Function to expand and contract a given div
        function toggle(descendent) {
            var cl = descendent.parentNode.parentNode.classList;
            if (cl.contains('hide')){
              cl.remove('hide');
            }
            else{
              cl.add('hide');
            }
        }
        
        // Expands targets if they are hidden
        function showTarget(id){
            var element = document.getElementById(id);
            while (element != document.body.rootNode ){
        	element.classList.remove("hide");
        	element = element.parentElement;
            }
        }
        // ]]>
                </script>
""")


    def start(self):
        self.ol("<!DOCTYPE html>")
        self.ol("<html xmlns=\"http://www.w3.org/1999/xhtml\">")
        self.ol("    <head>")
        self.ol("      <meta content=\"text/html;charset=utf-8\" http-equiv=\"Content-Type\"></meta>")
        self.ol("	<meta content=\"utf-8\" http-equiv=\"encoding\"></meta>")
        self.ol("	<title>"+self.title()+"</title>")
        self.fx_pp_js()
        self.ol("        <style type=\"text/css\">")
        css_content.fx_pp_css(self)
        extra_css = self.rf("//cc:extra-css")
        if extra_css is not None:
            self.ol(extra_css.text)
        
        self.ol("	</style>")
        self.ol("      </head>")
        self.ol("<body onload=\"init()\">")
        self.fx_body_begin()
        self.apply_templates([self.root])
        self.ol("      </body>")
        self.ol("    </html>")

    def title(self):
        return self.root.attrib["name"]
    
    def fx_body_begin(self):
        comments_els = self.rfa("//cc:comment")
        if comments_els:
            ctr=0
            self.ol("     <div id=\"commmentbox-\">")
            for comment_el in comment_els:
                id=self.derive_id(comment_el)
                self.ol("         <a href=\"#"+id+"\">Comment: "+id+"</a><br/>")
            self.ol("     </div>")
        self.o("   <h1 class=\"title\" style=\"page-break-before:auto;\">")
        self.o(self.title())
        self.o("</h1>")
        self.ol("   <noscript>")
        self.ol("     <h1 style=\"text-align:center; border-style: dashed; border-width: medium; border-color: red;\"")
        self.ol("         >This page is best viewed with JavaScript enabled!</h1>")
        self.ol("   </noscript>")
        self.ol("   <div class=\"center\">")
        self.ol("     <img src=\"images/niaplogo.png\" alt=\"NIAP Logo\"/> <br/>")
# Might think about getting rid of this and just making it part of the foreword
        self.ol("     Version: "+self.rf("//cc:ReferenceTable/cc:PPVersion").text+"<br/>")
        self.ol("     "+self.rf("//cc:ReferenceTable/cc:PPPubDate").text+"<br/>")
        self.ol("     <b>"+self.rf("//cc:PPAuthor").text+"</b><br/>")
        self.ol("   </div>")
        self.apply_templates(self.rfa("//cc:foreword"))
        self.ol("<h2 style=\"page-break-before:always;\">Revision History</h2>")
        self.ol("<table>")
        self.ol("<tr class=\"header\">")
        self.ol("<th>Version</th>")
        self.ol("<th>Date</th>")
        self.ol("<th>Comment</th>")
        self.ol("</tr>")
        for entry in self.rfa("//cc:RevisionHistory/cc:entry"):
            self.ol("<tr>")
            self.o("<td>")
            self.handle_content(entry.find("cc:version",NS))
            self.o("</td>")
            self.o("<td>")
            self.handle_content(entry.find("cc:date",NS))
            self.o("</td>")
            self.o("<td>")
            self.handle_content(entry.find("cc:subject",NS))
            self.o("</td>")
            self.ol("</tr>")
        self.ol("</table>")
        self.ol("<h2>Contents</h2>")
        self.ol("<div class=\"toc\" id=\"toc\"/>")
            


        
    def fcomp_cc_id(self, node, suffix=""):
        ret = node.attrib["cc-id"].upper() + suffix
        if "iteration" in node.attrib:
            ret += "/"+node.attrib["iteration"]
        return ret
        
        
    # def element_cc_id(self, node):
    #     fcomp = node.find("..")
    #     indexstr = str(fcomp.index(node))
    #     return self.fcomp_cc_id(fcomp, suffix="."+indexstr)
        

    def handle_content(self, node):
        if node is None:
            return
        self.o(node.text)
        for child in node:
            self.apply_templates_single(child)
            self.o(child.tail)

            
    def handle_section(self, node, title, id):
        self.o("<h5 id=\""+id+"\">")
        self.o(title)
        self.ol("</h5>")
        self.handle_section_hook(title, node)
        self.handle_content(node)

    def handle_section_hook(self, title, node):
        if "boilerplate" in node.attrib and node.attrib["boilerplate"]=="no":
            return
        self.handle_section_hook_base(title, node)

    def handle_section_hook_base(self, title, node):
        if title=="Conformance Claims":
            self.handle_conformance_claims(node)
        elif title=="Implicity Satisfied Requirements":
            self.handle_implicitly_satisfied_requirements()
        elif title=="Security Objectives Rationale":
            self.handle_security_objectives_rationale(node)
        elif title=="Security Objectives for the Operational Environment":
            self.handle_security_objectives_operational_environment()
        elif title=="Optional Requirements":
            self.handle_optional_requirements()
        elif title=="Selection-based Requirements":
            self.handle_selection_based_requirements(node)

    def opt_app(self,level,word,sfrs):
        self.ol("<h"+level+" id='"+word.replace(" ","-")+"-' class='indexable' data-level='"+level+"'>"+word+"</h"+level+">")
        if len(sfrs)==0:
            self.ol("This PP-Module does not define any "+word+" SFRs.")
        else:
            self.handle_sparse_sfrs(sfrs)

    def handle_optional_requirements(self):
        self.opt_app("2", "Strictly Optional", self.opt_sfrs)
        self.opt_app("2", "Objective", self.opt_sfrs)
        self.opt_app("2", "Strictly Optional", self.opt_sfrs)

    def handle_selection_based_requirements(self, node):
        self.opt_app("1", "Selection-based", self.sel_sfrs)

            
    def handle_security_objectives_operational_environment(self):
        soes=self.rfa("cc:SOEs")
        if len(soes)>0:
            self.ol("Something")
            self.ol("""The OE of the TOE implements technical and procedural measures 
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
            self.ol("This PP-Module does not define any objectives for the OE.")
        
    def create_ctr(self, ctrtype, id):
        self.ol("<span class=\"ctr\" data-myid=\""+id+"\" data-counter-type=\"ct-"+ctrtype+"\" id=\""+id+"\">")
        self.o(ctrtype + " ")
        self.ol("<span  class=\"counter\">"+id+"</span>")
        self.ol("</span>")
        
    def create_bibliography(self):
        self.ol("        <h1 id=\"appendix-bibliography\" class=\"indexable\" data-level=\"A\">Bibliography</h1>")
        self.ol("<table>")
        self.ol("<tr class=\"header\"> <th>Identifier</th> <th>Title</th> </tr>")
        # <xsl:apply-templates mode="hook" select="."/>
        entries = (self.rfa("//cc:bibliography/cc:entry") +
                   self.boilerplate.xpath("//*[@id='cc-docs']/cc:entry",namespaces=NS))
        entries.sort(key=lambda x: pp_util.flatten(x.find("cc:description", NS)))
        for entry in entries:
            pp_util.log("Entry : "+pp_util.flatten(entry.find("cc:description", NS)))
            self.ol("<tr>")
            self.o("<td><span id=\""+self.derive_id(entry)+"\">["+entry.find("cc:tag", NS).text+"]</span></td>\n<td>")
            self.handle_content(entry.find("cc:description",NS))
            self.ol("</td>")
            self.ol("</tr>")
        self.ol("</table>")
        
    def create_acronym_listing(self):
        self.ol("<h1 id=\"acronyms\" class=\"indexable\" data-level=\"A\">Acronyms</h1>")
        self.ol("<table>")
        self.ol("<tr class=\"header\"><th>Acronym</th><th>Meaning</th></tr>")
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
            self.ol("<tr>")
            self.o("<td><span class=\"term\" id=\"abbr_"+abbr+"\"")
            self.o(pp_util.get_attr_or(term_el, "plural", post=lambda x:" plural=\""+x+"\""))
            self.o(pp_util.get_attr_or(term_el, "lower",  post=lambda x:" lower=\""+x+"\""))
            self.o(">")
            self.o(abbr)
            self.ol("</span></td>")
            self.o("<td><span id=\"long_abbr_")
            self.o(abbr)
            self.ol("\">"+full+"</span></td></tr>\n")
        self.ol("</table>")

            
            
    def handle_security_objectives_rationale(self, node):
        self.o("""<h2 class="indexable,h2" data-level="2">Security Objectives Rationale</h2>   
This section describes how the assumptions, threats, and organizational 
security policies map to the security objectives.
<table>
<caption>""")
        self.create_ctr("Table","t-sec-obj-rat");
        self.ol(": Security Objectives Rationale</caption>")
        self.ol("""<tr class="header">
        <td>Threat, Assumption, or OSP</td>
        <td>Security Objectives</td>
        <td>Rationale</td>
      </tr>""")
        objrefers=self.rx("//cc:threat/cc:objective-refer | //cc:OSP/cc:objective-refer | //cc:assumption/cc:objective-refer")
        firstcol=""
        for objrefer in objrefers:
            parent = objrefer.find("..")
            pname = parent.attrib["name"]
            self.o("<tr")
            if pname != firstcol:
                firstcol=pname
                numkids = len(parent.findall("cc:objective-refer", NS))
                self.o(" class=\"major-row\">")
                pname_wrap = pp_util.make_wrappable(pname)
                self.o("<td rowspan=\""+str(numkids)+"\">")
                self.o(pname_wrap)
                self.o("</td")
            self.o("><td>")
            self.o(pp_util.make_wrappable(objrefer.attrib["ref"]))
            self.o("</td><td>")
            self.handle_content(objrefer.find("cc:rationale",NS))
            self.ol("</td></tr>")
        self.ol("</table>")
    #         <xsl:if test="not(name(preceding-sibling::cc:*[1])='objective-refer')">
    #         <xsl:attribute name="class">major-row</xsl:attribute>
    #         <xsl:variable name="rowspan" select="count(../cc:objective-refer)"/>
    #         <td rowspan="{$rowspan}">
    #           <xsl:call-template name="underscore_breaker">
    #     	<xsl:with-param name="valu"><xsl:apply-templates select=".." mode="get-representation"/></xsl:with-param></xsl:call-template>
    #         </td>
    #       </xsl:if>
    #       <td>
    #         <xsl:call-template name="underscore_breaker">
    #           <xsl:with-param name="valu" select="@ref"/>
    #         </xsl:call-template>
    #     </td>
    #       <td><xsl:apply-templates select="cc:rationale"/></td>
    #     </tr>
    #   </xsl:for-each>
    # </table>

        
    def handle_implicitly_satisfied_requirements(self):
       self.ol("<p>This appendix lists requirements that should be considered satisfied by products")
       self.ol("successfully evaluated against this "+self.doctype_short()+". These requirements are not featured")
       self.ol("explicitly as SFRs and should not be included in the ST. They are not included as ")
       self.ol("standalone SFRs because it would increase the time, cost, and complexity of evaluation.")
       self.ol("This approach is permitted by <a href=\"#bibCC\">[CC]</a> Part 1, 8.2 Dependencies between components.</p>")
       self.ol("<p>This information benefits systems engineering activities which call for inclusion of particular")
       self.ol("security controls. Evaluation against the "+self.doctype_short()+" provides evidence that these controls are present ")
       self.ol("and have been evaluated.</p>")
       
        
    def template_assumptions_cclaims_threats_OSPs_SOs_SOEs(self, node):
        defs = node.findall("cc:*[cc:description]", NS)
        if len(defs)>0:
            self.ol("<dl>")
            for defined in defs:
                classtype=pp_util.localtag(defined.tag)
                name= defined.attrib["name"]
                self.o("<dt class=\""+classtype+",defined\" id=\""+name+"\">")
                self.o(name)
                self.ol("</dt>")
                self.o("<dd>")
                self.apply_templates(defined.findall("./cc:description",NS))
                self.apply_templates(defined.findall("./cc:appnote",NS))
                self.ol("</dd>")
            self.ol("</dl>")
        else:
            self.ol("This document does not define any additional " + pp_util.localtag(node.tag))
        
    def template_xref(self, node):
        if "to" in node.attrib:
            to=node.attrib["to"]
        else:
            to=node.attrib["g"]
        refs = self.rx(".//cc:*[@id='"+to+"']|.//sec:*[local-name()='"+to+"']")
        if len(refs)==0:
            pp_util.log("Failed to find a reference to "+to)
            self.ol("<a href=\"#{@to}\" class=\"dynref\" data-post=\"{@format}\"></a>")
            return
        elif len(refs)>1:
            pp_util.log("Found multipled targets for "+ to)
        self.make_xref(refs[0])

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
        self.handle_section(node,node.attrib["title"],id)
        
    def template_newsection(self, node):
        id = pp_util.localtag(node.tag)
        if "title" in node.attrib:
            title=node.attrib["title"]
        else:
            title=id.replace("_", " ")
        self.handle_section(node, title, id)

    def make_term_table(self, term_els, ignores=""):
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
            self.template_glossary_entry(termdic[term])

        
    def template_tech_terms(self, node):
        self.ol("    <div class=\"no-link\">")
        self.ol("    <h2 id='glossary' class='indexable' data-level='2'>Terms</h2>")
        self.ol("The following sections list Common Criteria and technology terms used in this document.")
        self.ol("    <h3 id=\"cc-terms\" class=\"indexable\" data-level=\"3\">Common Criteria Terms</h3>")
        self.ol("    <table>")
        igs=""
        suppress_el = self.rf("//cc:suppress")
        if suppress_el is not None:
            igs = ","+suppress_el.text+","
        fromdoc = self.rx(".//cc:cc-terms/cc:term[text()]")
        builtin=self.boilerplate.xpath(".//cc:cc-terms/cc:term[text()]", namespaces=NS)
        self.make_term_table(fromdoc+builtin, ignores=igs)
        self.ol("    </table>")
        self.ol("    <h3 id=\"tech-terms\" class=\"indexable\" data-level=\"3\">Technical Terms</h3>")
        self.ol("    <table style=\"width: 100%\">")
        self.make_term_table(node.xpath(".//cc:term[text()]", namespaces=NS))
        self.ol("    </table>")
        self.ol("    </div>")
        
    def template_glossary_entry(self, node):
        full = node.attrib["full"]
        self.ol("        <tr>")
        id=full.replace(" ", "_")
        self.o("        <td><div id=\""+id+"\">"+full)
        
        if "abbr" in node.attrib:
            self.o(" ("+node.attrib["abbr"]+")")
        self.ol("</div></td>")
        self.ol("        <td>")
        self.handle_content(node)
        self.ol("</td>      </tr>\n")
      
    def template_html(self, node):
        lt = pp_util.localtag(node.tag)
        self.o("<"+lt)
        for att in node.attrib:
            self.o(" "+att+"=\""+ pp_util.make_attr_safe(node.attrib[att])+"\"")
        self.o(">")
        self.handle_content(node)
        self.o("</"+lt+">")
        
        
    def apply_templates(self, nodelist):
        if nodelist is None:
            return
        for node in nodelist:
            self.apply_templates_single(node)



    def template_usecases(self, node):
        self.ol("    <dl>")
        ctr = 1
        for usecase in node.findall("cc:usecase", NS):
            id = usecase.attrib["id"]
            self.o("        <dt id=\""+id+"\"> [USE CASE "+str(ctr)+"] ")
            self.o(usecase.attrib["title"])
            self.o("</dt>\n        <dd>")
            self.apply_templates(usecase.findall("./cc:description",NS))
            config = node.find("./cc:config", NS)
            if config is not None:
                self.ol("          <p> For changes to included SFRs, selections, and assignments required for this use case, see <a href=\"#appendix-"+id+"\" class=\"dynref\"></a>.")
                self.ol("          </p>")

            self.ol("        \"</dd>")
            ctr += 1
        self.ol("    </dl>")

    # def get_plural(self, node):
    #     if "target-products" in node.attrib:
    #         return node.attrib["target-products"]
    #     return node.attrib["target-product"]+"s"

    # def get_short(self, node):
    #     if "short" in node.attrib:
    #         return node.attrib["short"]
    #     return self.get_plural(node)




    def handle_felement(self, node, reqid):
        self.ol("<div class=\"element\">")
        
        # reqid = self.element_cc_id(node)
#       <xsl:variable name="reqid"><xsl:apply-templates select="." mode="getId"/></xsl:variable>
        self.ol("<div class=\"reqid\" id=\""+reqid+"\">")
        self.ol("  <a href=\"#"+reqid+"\" class=\"abbr\">" + reqid +"</a>")
        self.ol("</div>")
        self.ol("<div class=\"reqdesc\">")
        title=node.find("cc:title", NS)
        self.handle_content(title)
        # apply_templates_single(title)
        rulez = self.rx("//cc:rule[.//cc:ref-id/text()=current()//@id]")
        notes = node.findall("cc:note" , NS)
        if len(rulez)+len(notes) > 0:
            self.ol("<br/><span class=\"note-header\">Application Note: </span>")
            for note in notes:
                self.handle_content(note)
#         <xsl:if test="//cc:rule[.//cc:ref-id/text()=current()//@id]">
# 	  <xsl:if test="not(cc:note)">
# 	  </xsl:if>
#           <div class="validationguidelines_label">Validation Guidelines:</div>
# <!--          <p/>Selections in this requirement involve the following rule(s):<br/> -->
#           <xsl:apply-templates select="//cc:rule[.//cc:ref-id/text()=current()//@id]" mode="use-case"/>
# 	</xsl:if>
        self.ol("  </div>")
        self.ol("</div>")
        
    


    def get_meaningful_ancestor(self, refid):
        ret = self.rx("//cc:f-element[.//@id='"+refid+"']|//cc:choice[.//@id='"+refid+"']|//cc:feature[.//@id='"+refid+"']")
        pp_util.log("Got: "+str(len(ret)) + " for " + refid)
        if len(ret) != 1:
            raise Exception("Should only be one thing")
        return ret[0]

    def handle_fcomponent(self, node):
        formal = self.fcomp_cc_id(node)
        self.ol("<div class=\"comp\" id=\""+formal+"\">")
        self.ol("<h4>"+ formal + " "+ node.attrib["name"]+"</h4>")
        status=""
        objective = False
        optional = False
        # Meaningful ancestor is the key
        selecteds = {}

        if node.find("cc:depends/cc:objective", NS):
            objective = True
        else:
            for dep in node.findall("cc:depends", NS):
                if dep.find("cc:optional", NS):
                    optional = True
                    pass
                edoc = dep.find("cc:external-doc", NS)
                if edoc is not None:
                    self.rf("//cc:*[@id='"+edoc.attrib["ref"]+"']")
                    raise Exception("Can't handle yet")
                else:
                    buckets={"f-element":{},"feature":{},"choice":{} }
                    for attrname in dep.attrib:
                        attr = dep.attrib[attrname]
                        if self.is_base(attr):
                            continue
                        meananc = self.get_meaningful_ancestor(attr)
                        ltag = pp_util.localtag(meananc.tag)
                        log("stroign off something")
                        # if meananc in selecteds:
                        #     selecteds[meananc].append(attr)
                        # else:
                        #     selecteds[meananc] = [].append(attr)
            for meananc in selecteds:
                pp_util.log("Doing something: "+ meananc.tag)
            if optional:
                status += "<p>This component may also be included in the ST as if optional.</p>"
        if len(status) > 0:
            self.ol("<div class=\"statustag\"><i><b>"+status+"</b></i></div>")



   #     <xsl:if test="@status='sel-based'">
  #       <div class="statustag">
  #         <b><i>This is a selection-based component. Its inclusion depends upon selection from
  #         <xsl:call-template name="handle_thing_with_depends"/>
  #         </i></b>
  #       </div>
  #     </xsl:if>
  #     <xsl:if test="@status='feat-based'">
  #       <div class="statustag">
  #         <i><b>This is an implementation-based component.
  #               Its inclusion in depends on whether the TOE implements one or more of the following features:
  #               <ul>
  #                 <xsl:for-each select="cc:depends/@*">
  #                   <xsl:variable name="ref-id" select="."/>
  #                     <li><a href="#{$ref-id}"><xsl:value-of select="//cc:feature[@id=$ref-id]/@title"/></a></li>
  #                 </xsl:for-each>
  #               </ul>
  #               as described in Appendix A: Implementation-based Requirements.
  #              <xsl:if test="cc:depends/cc:optional"><p>This component may also be included in the ST as if optional.</p></xsl:if>
  #       </b></i>
  #       </div>
  #     </xsl:if>
  #    <xsl:apply-templates/>
  #       <xsl:call-template name="f-comp-activities"/>
  #   </div>
  # </xsl:template>
        ctr=0
        for f_el in node.findall(".//cc:f-element", NS):
            ctr+=1
            reqid=self.fcomp_cc_id(node, "."+str(ctr))
            self.handle_felement(f_el, reqid)
        self.ol("</div>")
    
    def handle_sparse_sfrs(self, sfrs):
        titles={}
        for sfr in sfrs:
            sec = sfr.find("..")
            title = self.get_section_title(sec)
            id = self.get_section_base_id(sec)
            if title not in titles:
                titles[title]=1
                self.ol("<h4 id='"+id+"'>"+title+"</h4>")
            self.handle_fcomponent(sfr)

                
        
    def apply_templates_single(self, node):
        if node is None or not isinstance(node.tag,str):
            return False
        return self.apply_template_to_element(node)

    def apply_template_to_element(self, node):
        tag = node.tag
        # pp_util.log("Starting: " + str(node))
        if tag.startswith("{https://niap-ccevs.org/cc/v1/section}"):
            self.template_newsection(node)
        elif tag == "{https://niap-ccevs.org/cc/v1}section":
            self.template_oldsection(node)
        elif tag == "{https://niap-ccevs.org/cc/v1}appendix":
            self.template_appendix(node)
        elif tag.startswith("{http://www.w3.org/1999/xhtml}"):
            self.template_html(node)
        elif tag == "{https://niap-ccevs.org/cc/v1}xref":
            self.template_xref(node)
        elif tag == "{https://niap-ccevs.org/cc/v1}tech-terms":
            self.template_tech_terms(node)
        elif tag=="{https://niap-ccevs.org/cc/v1}usecases":
            self.template_usecases(node)
        elif tag=="{https://niap-ccevs.org/cc/v1}assumptions"\
             or tag=="{https://niap-ccevs.org/cc/v1}cclaims"\
             or tag=="{https://niap-ccevs.org/cc/v1}threats"\
             or tag=="{https://niap-ccevs.org/cc/v1}OSPs"\
             or tag=="{https://niap-ccevs.org/cc/v1}SOs"\
             or tag=="{https://niap-ccevs.org/cc/v1}SOEs":
            self.template_assumptions_cclaims_threats_OSPs_SOs_SOEs(node)
        elif tag=="{https://niap-ccevs.org/cc/v1}sfrs":
            self.template_sfrs(node)
        elif tag=="{https://niap-ccevs.org/cc/v1}f-component" or\
             tag=="{https://niap-ccevs.org/cc/v1}ext-comp-def" or\
             tag=="{https://niap-ccevs.org/cc/v1}base-pp":

            pass
        elif tag=="{https://niap-ccevs.org/cc/v1}f-element":
            self.template_felement(node)
        elif tag=="{https://niap-ccevs.org/cc/v1}title":
            self.apply_templates(node)
        elif tag=="{https://niap-ccevs.org/cc/v1}management-function-set":
            self.template_management_function_set(node)
        elif tag=="{https://niap-ccevs.org/cc/v1}ctr":
            self.template_ctr(node)
        elif tag=="{https://niap-ccevs.org/cc/v1}no-link":
            self.ol("<span class=\"no-link\">")
            self.handle_content(node)
            self.ol("</span>")
        elif tag=="{https://niap-ccevs.org/cc/v1}manager":
            self.o("<td>")
            self.handle_content(node)
            self.ol("</td>")
        elif tag=="{https://niap-ccevs.org/cc/v1}text" or\
             tag=="{https://niap-ccevs.org/cc/v1}description":
            self.handle_content(node)
        elif tag=="{https://niap-ccevs.org/cc/v1}selectables":
            self.template_selectables(node)
        elif tag=="{https://niap-ccevs.org/cc/v1}assignable":
            self.template_assignable(node)
        elif tag=="{https://niap-ccevs.org/cc/v1}int":
            self.template_int(node)
        elif tag=="{https://niap-ccevs.org/cc/v1}_":
            self.o(self.shortcut)
        else:
            raise Exception("Can't handle: " + node.tag)
        # pp_util.log("Ending: "+str(node))
        return True


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

        self.ol("<span class=\"ctr\" data-myid=\""+id+"\" data-counter-type=\"ct-"+ctrtype+"\" id=\""+id+"\">")
        self.ol(self.get_pre(node))
        self.ol("      <span class=\"counter\">"+id+"</span>")
        self.handle_content(node)
        self.ol("    </span>")


        
    def template_int(self, node):
        if not pp_util.is_attr(node, "hide", "no"):
            return
        if "lte" in node.attrib:
            lte = node.attrib["lte"]
            if "gte" in node.attrib:
                gte = node.attrib["gte"]
                self.o(" between "+ gte + " and " + lte + ", inclusive ")
                return
            self.o(" less than or equal to " + lte)
            return
        elif "gte" in node.attrib:
            self.o(" greater than or equal to " + node.attrib["gte"])




        
    def template_assignable(self, node):
        id=self.derive_id(node)
        self.o("[<b>assignment</b>: <span class=\"assignable-content\" id=\""+id+"\">")
        self.handle_content(node)
        self.o("</span>]")

    def template_appendix(self, node):
        id=self.derive_id(node)
        title=node.attrib["title"]
        self.ol("        <h1 id=\""+id+"\" class=\"indexable\" data-level=\"A\">"+title+"</h1>")
        if "boilerplate" in node.attrib and node.attrib["boilerplate"]=="no":
            return
        self.handle_section_hook_base(title, node)
        self.handle_content(node)


    
    def template_selectables(self, node):
        self.o("[<b>selection</b>")
        if pp_util.is_attr(node, "onlyone", "yes"):
            self.o("<b>, choose one of</b>")
        self.o(": ")
        sli=""
        eli=""
        eul=""
        sep=","
        lagsep=""

        if pp_util.is_attr(node, "linebreak", "yes") or node.find(".//cc:selectables", NS) is not None:
            self.ol("<ul>")
            sep=""
            eul="</ul>"            
            sli="<li"+pp_util.get_attr_or(node, "style", post=lambda a:" style=\""+a+"\"")+">"
            eli="</li>"

        # Add the comma thing
        for selectable in node.findall("./cc:selectable",NS):
            self.o(lagsep)
            self.o(sli)
            id = self.derive_id(selectable)
            self.o("<span class=\"selectable-content\" id=\""+id+"\">")
            self.handle_content(selectable)
            self.o("</span>")
            self.ol(eli)
            lagsep=sep
        self.o("]")
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
        self.ol("<table class=\"mfs\" style=\"width: 100%;\">")
        self.ol("<tr class=\"header\">")
        self.ol("<td>#</td><td>Management Function</td>")
        managers = node.findall("./cc:manager", NS)
        self.apply_templates(managers)
        self.ol("</tr>")
        ctr=0
        prefix = pp_util.get_attr_or(node, "ctr-prefix")
        deffy  = node.attrib["default"]
        for mf in node.findall("./cc:management-function", NS):
            ctr+=1
            self.make_mf_row(mf, prefix+str(ctr), managers, deffy)
        self.ol("</table>")

    def get_mf_id(self, node):
        if "id" in node.attrib:
            return node.attrib["id"]
        return "_mf_"+str(self.get_global_index(node))

    def make_mf_val(self, tag, node):
        if tag == "O":
            self.o("<div>O<span class=\"tooltiptext\">Optional</span></div>")
        elif tag =="M":
            self.o("<div>M<span class=\"tooltiptext\">Mandatory</span></div>")
        elif tag == "NA":
            self.o("<div>-<span class=\"tooltiptext\">N/A</span></div>")
        else:
            self.handle_content(node)

    
    def make_mf_row(self, mf, prefix, managers, defval):
        mf_num = str(self.get_global_index(mf))
        mf_id = self.get_mf_id(mf)
        self.ol("   <tr id=\"{$mf_id}\">")
        self.o("     <td>"+prefix+"</td>")
        self.ol("<td style=\"text-align:left\">")
        self.apply_templates_single(mf.find("cc:text",NS))
        self.ol("</td>")
        for manager in managers:
            cid=manager.attrib["cid"]
            tagnode=mf.find("*[@ref='"+cid+"']")
            if tagnode == None:
                val=defval
            else:
                val= pp_util.localtag(tagnode.tag)
            self.ol("         <td>")
            self.make_mf_val(val, tagnode)
            self.ol("         </td>")
        self.ol("   </tr>")

    def set_underscore(self, val):
        self.shortcut = val
        
    def make_xref_section(self, node, id):
        self.ol("<a href=\"#{"+id+"}\" class=\"dynref\">Section </a>")

    def make_xref_bibentry(self, node):
        id =  node.attrib["id"]
        self.o("<a href=\"#"+id+"\">[")
        self.o(node.find("./cc:tag", NS).text)
        self.ol("]</a>")

        
    def make_xref(self, node):
        if node.tag.startswith("{https://niap-ccevs.org/cc/v1/section}"):
            self.make_xref_section(node, pp_util.localtag(node.tag))
        elif node.tag == "{https://niap-ccevs.org/cc/v1}base-pp":
            self.o(self.edocs[node.attrib["id"]].make_xref_edoc())
        elif node.tag == "{https://niap-ccevs.org/cc/v1}entry":
            self.make_xref_bibentry(node)
        else:
            raise Exception("Cannot handle: " + node.tag)

    def is_base(self, attr):
        b_el = self.rf("//cc:base-pp[@id='"+attr+"']")
        if b_el is not None:
            raise Exception("Should not have a base")
        return False
        
    # def show_package(self, node):
    #     self.o("<a href=\""+node.attrib["url"]+"\">")
    #     if "name" in node.attrib:
    #         self.o(node.attrib["name"])
    #         self.o(pp_util.get_attr_or(node, "short", post=lambda x:"("+x+")"))
    #         version = node.attrib["version"]            
    #     else:
    #         proot = self.edocs[node.attrib["id"]]
    #         self.o(proot.find(".//cc:PPTitle",NS).text)
    #         version=proot.find(".//cc:PPVersion",NS).text
    #     self.o("Package, version ")
    #     self.o(version)
    #     self.o("</a> Conformant")

        
