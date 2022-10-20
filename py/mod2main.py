#!/usr/bin/env python3
import sys
import pathlib
#import xml.etree.ElementTree as ET
import lxml.etree as ET
import argparse
import css_content

NS = {'cc': "https://niap-ccevs.org/cc/v1",
      'sec': "https://niap-ccevs.org/cc/v1/section",
      'htm': "http://www.w3.org/1999/xhtml"}

def log(msg):
    sys.stderr.write(msg)
    sys.stderr.write("\n")

def make_attr_safe(attr):
    ret = attr.replace('&', '&amp;')
    return ret.replace('"', '&quot;')

def localtag(tag):
    return  tag.split("}")[1]
    
class PP:
    def __init__(self, root, workdir, output, boilerplate):
        self.root = root
        self.edocs = {}
        self.out = open(output, "w+")
        self.globaltags = {}
        self.ids = {}
        self.boilerplate = ET.parse(boilerplate).getroot()
        for external in root.findall(".//cc:*[cc:git]", NS):
            id = external.attrib["id"]
            self.edocs[id]=ET.parse(workdir+"/"+external.attrib["id"]+".xml").getroot()
            
    def to_html(self):
        self.start()
        log("And now I'm done")
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


        
    def title(self):
        node = self.rf("//cc:PPTitle")
        if node is not None:
            return node.text()
        if "target-products" in self.root.attrib:
            return "PP-Module for " + self.root.attrib["target-products"]
        else:
            ret = "PP-Module for " +  self.root.attrib["target-product"] + "s"
            return ret

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

    def fx_body_begin(self):
        comments_els = self.rfa("//cc:comment")
        if not comments_els:
            return
        ctr=0
        self.ol("     <div id=\"commmentbox-\">")
        for comment_el in comment_els:
            id=self.getId(comment_el)
            self.ol("         <a href=\"#"+id+"\">Comment: "+id+"</a><br/>")
        self.ol("     </div>")

    def fcomp_cc_id(self, node, suffix=""):
        ret = node.attrib["cc-id"].upper() + suffix
        if "iteration" in node.attrib:
            ret += "/"+node.attrib["iteration"]
        return ret
        
        
    def element_cc_id(self, node):
        fcomp = node.find("..")
        indexstr = str(fcomp.index(node))
        return self.fcomp_cc_id(fcomp, suffix="."+indexstr)
        
    def getId(self, node):
        if "id" in node.attrib:
            return node.attrib["id"]

    def template_module(self, node):
        self.apply_templates(self.rx("//*[@title='Introduction']|sec:Introduction"))
        self.apply_templates(self.rx("//*[@title='Conformance Claims']|sec:Conformance_Claims"))
        self.apply_templates(self.rx("//*[@title='Security Problem Description']|sec:Security_Problem_Description"))
        self.apply_templates(self.rx("//*[@title='Security Objectives']|sec:Security_Objectives"))
        self.apply_templates(self.rx("//*[@title='Security Requirements']|sec:Security_Requirements"))
        # <xsl:call-template name="mod-obj-req-map"/>
        # <xsl:call-template name="mod-sars"/>
        # <xsl:call-template name="consistency-rationale"/>
        # <xsl:call-template name="opt-sfrs"/>
        # <xsl:call-template name="sel-sfrs"/>
        # <xsl:call-template name="ext-comp-defs"/>
        # self.apply-templates select="//cc:appendix"/>
        # <xsl:call-template name="acronyms"/>
        # <xsl:call-template name="bibliography"/>

    def handle_content(self, node):
        self.o(node.text)
        for child in node:
            self.apply_templates_single(child)
            self.o(child.tail)

            
    def handle_section(self, node, title, id, is_recur = True):
        self.o("<h5 id=\""+id+"\">")
        self.o(title)
        self.ol("</h5>")
        if is_recur:
            self.handle_content(node)

    def template_assumptions_cclaims_threats_OSPs_SOs_SOEs(self, node):
        defs = node.findall("cc:*[cc:description]", NS)
        if defs is not None:
            self.ol("<dl>")
            for defined in defs:
                classtype=localtag(defined.tag)
                name= defined.attrib["name"]
                self.o("<dt class=\""+classtype+",defined\" id=\""+name+"\">")
                self.o(name)
                self.ol("</dt>")
                self.o("<dd>")
                self.apply_templates(defined.find("./cc:description",NS))
                self.apply_templates(defined.find("./cc:appnote",NS))
                self.ol("</dd>")
            self.ol("</dl>")
        else:
            self.ol("This document does not define any additional " + localtag(node.tag))
        
    def template_xref(self, node):
        if "to" in node.attrib:
            to=node.attrib["to"]
        else:
            to=node.attrib["g"]
        refs = self.rx(".//cc:*[@id='"+to+"']|.//sec:*[local-name()='"+to+"']")
        if len(refs)==0:
            log("Failed to find a reference to "+to)
            self.ol("<a href=\"#{@to}\" class=\"dynref\" data-format=\"{@format}\"></a>")
            return
        elif len(refs)>1:
            log("Found multipled targets for "+ to)
        self.make_xref(refs[0])

    def get_list_of(self, fulltag):
        if fulltag in self.globaltags:
            return self.globaltags[fulltag]
        nodes = self.root.findall(".//"+fulltag)
        self.globaltags[fulltag] = nodes
        return nodes
    
    def get_section_base_id(self, node):
        if node.tag == "{https://niap-ccevs.org/cc/v1}section":
            if "id" in node.attrib:
                return node.attrib["id"]
            osecs = self.get_list_of(node.tag)
            id="sec_"+str(osces.index(node))+"-"
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
            osecs = self.get_list_of(node.tag)
            id="sec_"+str(osces.index(node))+"-"
        self.handle_section(node,node.attrib["title"],id)
        
    def template_newsection(self, node):
        id = localtag(node.tag)
        if "title" in node.attrib:
            title=node.attrib["title"]
        else:
            title=id.replace("_", " ")
        self.handle_section(node, title, id)

    def template_tech_terms(self, node):
        self.ol("    <div class=\"no-link\">")
        self.ol("    <h2 id='glossary' class='indexable' data-level='2'>Terms</h2>")
        self.ol("The following sections list Common Criteria and technology terms used in this document.")
        self.ol("    <h3 id=\"cc-terms\" class=\"indexable\" data-level=\"3\">Common Criteria Terms</h3>")
        self.ol("    <table>")
        ignores=""
        suppress_el = self.rf("//cc:suppress")
        
        if suppress_el is not None:
            ignores = ","+suppress_el.text+","
        terms=[]
        termdic={}
        for termdef in self.rx(".//cc:cc-terms/cc:term[text()]")+self.boilerplate.xpath(".//cc:cc-terms/cc:term[text()]", namespaces=NS):
            term = termdef.attrib["full"]
            if (","+ term +",") in ignores:
                continue
            uppered = term.upper()
            terms.append(uppered)
            termdic[uppered]=termdef
        terms.sort()
        for term in terms:
            self.template_glossary_entry(termdic[term])

            # self.ol("          terms.append(uppered)\"")
        
          # <xsl:for-each select="|">
          #   <xsl:sort select="translate(@full, $upper, $lower)"/>
          #   <xsl:if test="not(contains($ignore_list, concat(',',@full,',')))">
          #     <xsl:call-template name="glossary-entry"/>
          #   </xsl:if>
          # </xsl:for-each>
      # self.ol("    </table>")
      # self.ol("    <h3 id=\"tech-terms\" class=\"indexable\" data-level=\"3\">Technical Terms</h3>")
      # self.ol("    <table style=\"width: 100%\">")
      # # <xsl:for-each select="cc:term[text()]">
      # #   <xsl:sort select="@full"/>
      # #   <xsl:call-template name="glossary-entry"/>
      # # </xsl:for-each>
      # self.ol("    </table>")
      # self.ol("    </div>")
      # self.ol("  </xsl:template>")
        
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
        lt = localtag(node.tag)
        self.o("<"+lt)
        for att in node.attrib:
            self.o(" "+att+"=\""+ make_attr_safe(node.attrib[att])+"\"")
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
            self.apply_templates(node.findall("./cc:description",NS))
            config = node.find("./cc:config", NS)
            if config is not None:
                self.ol("          <p> For changes to included SFRs, selections, and assignments required for this use case, see <a href=\"#appendix-"+id+"\" class=\"dynref\"></a>.")
                self.ol("          </p>")

            self.ol("        \"</dd>")
            ctr += 1
        self.ol("    </dl>")

    def get_plural(self, node):
        if "target-products" in node.attrib:
            return node.attrib["target-products"]
        return node.attrib["target-product"]+"s"

    def get_short(self, node):
        if "short" in node.attrib:
            return node.attrib["short"]
        return self.get_plural(node)

    def get_product(self, node):
        return node.attrib["target-product"]

    def is_modified(self, sfr, declared, broot):
        cc_id = sfr.attrib["cc-id"]
        xp_iter=""
        if "iteration" in sfr.attrib:
            iteration=sfr.attrib["iteration"]
            if (cc_id+"/"+iteration) in declared:
                return True
            xp_iter = " and @iteration='"+iteration+"'"
        else:
            if cc_id in declared:
                return True
        if broot is not None:
            xpath = "//cc:f-component[@cc-id='"+cc_id+"'"+xp_iter + "]"
            orig = broot.xpath(xpath, namespaces=NS)
            ret = len(orig) > 0
            return ret
        return False


    def get_declared_modified_sfrs(self, base):
        modsfrs =  base.find(".//mod-sfrs")
        if not modsfrs:
            return []
        return modsfrs.text.split(" ")


    def template_felement(self, node):
        self.ol("<div class=\"element\">")
        reqid = self.element_cc_id(node)
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
        
    
    def template_basepp(self, node):
        id = node.attrib["id"]
        if id in self.edocs:
            broot = self.edocs[id]
            short = self.get_short(broot)
        else:
            raise Exception("Can't do this basepp")
        log("Looking at: "+broot.xpath("//cc:PPTitle",namespaces=NS)[0].text)
        self.ol("<h2 id=\""+"secreq-"+id+" class=\"indexable\" data-level=\"2\">")
        self.o(short)
        self.ol(" Security Functional Requirements Direction")
        self.ol("</h2>")
        if not self.apply_templates_single(node.find("cc:sec-func-req-dir", NS)):
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


    def get_meaningful_ancestor(self, refid):
        ret = self.rx("//cc:f-element[.//@id='"+refid+"']")
        if len(ret) == 1:
            return ret
        ret = self.rf("//cc:feature[@id='"+refid+"']")
        if ret is not None:
            return ret
        ret = self.rx("//cc:choice[.//@id='"+refid+"']")
        if len(ret) == 1:
            return ret
        raise Exception("Could not find meaningful ancestor for: '" + refid+"'")
                

    def handle_fcomponent(self, node):
        formal = self.fcomp_cc_id(node)
        self.ol("<div class=\"comp\" id=\""+formal+"\">")
        self.ol("<h4>"+ formal + " "+ node.attrib["name"]+"</h4>")
        status=""
        objective = False
        optional = False
        # Meaningful ancestor is the key
        selecteds = []

        if node.find("cc:depends/cc:objective", NS):
            objective = True
        else:
            if node.find("cc:depends/cc:optional", NS):
                optional = True
            for dep in node.findall("cc:depends", NS):
                edoc = dep.find("cc:external-doc", NS)
                if edoc is not None:
                    self.rf("//cc:*[@id='"+edoc.attrib["ref"]+"']")
                    raise Exception("Can't handle yet")
                else:
                    for attr in dep.attrib:
                        if self.rf("//cc:base[@id='"+dep.attrib[attr]+"']") is None:
                            continue
                        meananc = self.get_meaningful_ancestor(dep.attrib[attr])
                        selecteds[meananc] = dep.attrib[attr]
                    
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
  #     <xsl:if test="@status='optional'">
  #       <div class="statustag">
  #         <i><b>This is an optional component. However, applied modules or packages might redefine it as mandatory.</b></i>
  #       </div>
  #     </xsl:if>
  #    <xsl:apply-templates/>
  #       <xsl:call-template name="f-comp-activities"/>
  #   </div>
  # </xsl:template>
        self.apply_templates(node.findall(".//cc:f-element", NS))
        self.ol("</div>")
    
    def handle_sparse_sfrs(self, sfrs):
        titles={}
        for sfr in sfrs:
            sec = sfr.find("..")
            title = self.get_section_title(sec)
            id = self.get_section_base_id(sec)
            if title not in titles:
                titles[title]=1
                log("Title is |"+title+"|")
                self.ol("<h4 id='"+id+"'>"+title+"</h4>")
            else:
                log("Not in")
            log("!!!!! "+ title)
            self.handle_fcomponent(sfr)

                
        
    def apply_templates_single(self, node):
        if node is None:
            return False
        tag = node.tag
        if not isinstance(tag,str):
            log("Handingling something weird")
            return False
        # log("Starting: " + str(node))
        if tag == "{https://niap-ccevs.org/cc/v1}Module":
            self.template_module(node)
        elif tag.startswith("{https://niap-ccevs.org/cc/v1/section}"):
            self.template_newsection(node)
        elif tag == "{https://niap-ccevs.org/cc/v1}section":
            self.template_oldsection(node)
        elif tag.startswith("{http://www.w3.org/1999/xhtml}"):
            self.template_html(node)
        elif tag == "{https://niap-ccevs.org/cc/v1}xref":
            log(str(node))
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
        elif tag=="{https://niap-ccevs.org/cc/v1}base-pp":
            self.template_basepp(node)
        elif tag=="{https://niap-ccevs.org/cc/v1}sfrs":
            pass
        elif tag=="{https://niap-ccevs.org/cc/v1}f-component":
            pass
        elif tag=="{https://niap-ccevs.org/cc/v1}f-element":
            self.template_felement(node)
        elif tag=="{https://niap-ccevs.org/cc/v1}title":
            self.apply_templates(node)
        elif tag=="{https://niap-ccevs.org/cc/v1}management-function-set":
            log("Skipping:" + tag)
        else:
            raise Exception("Can't handle: " + node.tag)
        # log("Ending: "+str(node))
        return True

    def make_xref_section(self, node, id):
        self.ol("<a href=\"#{"+id+"}\" class=\"dynref\">Section </a>")
        

    def make_xref_edoc(self, node):
        url=node.find("cc:url", NS).text
        self.o("<a href=\""+make_attr_safe(url)+"\">")        
        if "name" in node.attrib:
            self.o(node.attrib["name"])
            self.o(" version ")
            self.o(node.attrib["version"])
        else:
            root = self.edocs[node.attrib["id"]]
            modrot = root.find(".//cc:Module", NS)
            if modrot is not None:
                name = modrot.attrib["name"]
                if not name.startswith("PP-Module for"):
                    name = "PP-Module for " + name
            else:
                modrot = root.find(".//cc:PPTitle", NS)
                if modrot is not None:
                    name = modrot.text
                else:
                    raise Exception("Somethign else " + str(node)   )
            self.o(name)
            self.o(", version ")
            self.o(root.find(".//cc:PPVersion", NS).text)
        self.ol("</a>")

    def make_xref_bibentry(self, node):
        id =  node.attrib["id"]
        self.o("<a href=\"#"+id+"\">[")
        self.o(node.find("./cc:tag", NS).text)
        self.ol("]</a>")

        
    def make_xref(self, node):
        if node.tag.startswith("{https://niap-ccevs.org/cc/v1/section}"):
            self.make_xref_section(node, localtag(node.tag))
        elif node.tag == "{https://niap-ccevs.org/cc/v1}base-pp":
            self.make_xref_edoc(node)
        elif node.tag == "{https://niap-ccevs.org/cc/v1}entry":
            self.make_xref_bibentry(node)
        else:
            raise Exception("Cannot handle: " + node.tag)

            
        
  #   <h1 class="title" style="page-break-before:auto;"><xsl:value-of select="$title"/></h1>
  #   <noscript>
  #     <h1 style="text-align:center; border-style: dashed; border-width: medium; border-color: red;"
  #         >This page is best viewed with JavaScript enabled!</h1>
  #   </noscript>
  #   <div class="center">
  #     <img src="images/niaplogo.png" alt="NIAP Logo"/> <br/>
  #       <!-- Might think about getting rid of this and just making it part of the foreword -->
  #     Version: <xsl:value-of select="//cc:ReferenceTable/cc:PPVersion"/><br/>
  #     <xsl:value-of select="//cc:ReferenceTable/cc:PPPubDate"/><br/>
  #     <b><xsl:value-of select="//cc:PPAuthor"/></b><br/>
  #   </div>
  #   self.apply-templates select="//cc:foreword"/>

  #   <h2 style="page-break-before:always;">Revision History</h2>
  #   <table>
  #    <tr class="header">
  #      <th>Version</th>
  #      <th>Date</th>
  #      <th>Comment</th>
  #    </tr>
  #    <xsl:for-each select="//cc:RevisionHistory/cc:entry">
  #      <tr>
  #        <td> <xsl:value-of select="cc:version"/> </td>
  #        <td> <xsl:value-of select="cc:date"/> </td>
  #        <td> self.apply-templates select="cc:subject"/> </td>
  #      </tr><xsl:text>&#xa;</xsl:text>
  #    </xsl:for-each>
  #   </table>
  #   <h2>Contents</h2>
  #   <div class="toc" id="toc"/>
  # </xsl:template>
  #       print("Yes")
            
    
def make_mod(path):
    print("Making mod: "+path)
    doc = ET.parse(path)
    pp = PP( doc.getroot(), "../../output", "/tmp/abc.html", "/home/kevin/commoncriteria/bluetooth/transforms/xsl/boilerplates.xml" )
    pp.to_html()
    
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert an XML Protection Profile Definition to a readable HTML document')
    # parser.add_argument('integers', metavar='N', type=int, nargs='+',
    #                     help='an integer for the accumulator')
    # parser.add_argument('--sum', dest='accumulate', action='store_const',
    #                     const=sum, default=max,
    #                     help='sum the integers (default: find the max)')
    parser.add_argument('-w', nargs="?")
    parser.add_argument('output-file', nargs="?", help="Path to output file")
    parser.add_argument('input-file' , help="Path to the XML definition")
    args = parser.parse_args()
    make_mod(vars(args)["input-file"])
    print(str(args))

    # print(args.accumulate(args.integers))
