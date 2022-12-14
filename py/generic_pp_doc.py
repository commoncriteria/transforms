import lxml.etree as ET
from lxml.builder import E
from lxml.builder import ElementMaker
import css_content
import pp_util
from pp_util import log
import math
import edoc
import re

CC="{https://niap-ccevs.org/cc/v1}"
NS = {'cc': "https://niap-ccevs.org/cc/v1",
      'sec': "https://niap-ccevs.org/cc/v1/section",
      'htm': "http://www.w3.org/1999/xhtml"}

# SVG_NS="http://www.w3.org/2000/svg"
# SVG="{%s}"%SVG_NS
# OUT_NSMAP={None: SVG_NS}
#SVG_E=ElementMaker(namespace="http://www.w3.org/2000/svg")
NBSP=str(chr(0xA0))
SVG_E=ElementMaker()
HTM_E=pp_util.get_HTM_E()
adopt=pp_util.adopt


        


A_UPPERCASE = ord('A')
ALPHABET_SIZE = 26

def add_grouping_row(table, text, size):
    rowspan=size+2
    # Add two blank rows, so that it doesn't screw up the alternating coloring
    attrs={"rowspan":str(rowspan)}
    table.append(HTM_E.tr({"class":"major-row"}, HTM_E.td(attrs, text), blank_cell))
    table.append(HTM_E.tr(blank_cell))

def blank_cell():
    return HTM_E.td({"style":"display:none;"})

def add_to_map_to_map(mappy, key, attr):
    if key not in mappy:
        minor = {}
    else:
        minor=mappy[key]
    minor[attr]=1
    mappy[key]=minor

def _decompose(number):
    """Generate digits from `number` in base alphabet, least significants
    bits first.

    Since A is 1 rather than 0 in base alphabet, we are dealing with
    `number - 1` at each iteration to be able to extract the proper digits.
    """
    while number:
        number, remainder = divmod(number-1, ALPHABET_SIZE)
        yield remainder


def base_10_to_alphabet(number):
    """Convert a decimal number to its base alphabet representation"""
    return ''.join(
            chr(A_UPPERCASE + part)
            for part in _decompose(number+1)
    )[::-1]

def make_sort_key_stringnum(s):
    spl=s.split(".")
    return spl[0]+"."+spl[1].rjust(3)

def backslashify(phrase):
    return re.sub("([][_.^()-/])", r"\\\1", phrase)

def def_attr(id):
    return {"id":id, "class":"def_", "href":"#"+id}

defargs={'fill':'black',
         'font-size':'15'}
boxargs={'height':'17','fill':'none','stroke':'black'}


def drawbox(parent, ybase,boxtext,ymid, xbase=0):
    if xbase==0:
        width=150
    else:
        width=len(boxtext)*12

    txt_el = SVG_E.text(boxtext, **defargs, x=str(xbase+4),y=str(ybase+24))
    parent.append(txt_el)
    rec_el = SVG_E.rect(**boxargs, x=str(xbase+2),y=str(ybase+10),width=str(width))
    parent.append(rec_el)
    if xbase>0:
        ln_el=SVG_E.line(x1='152',y1=str(ymid+17),x2=str(xbase+1),y2=str(ybase+17), stroke='black')
        parent.append(ln_el)


def get_convention_explainer():
    return HTM_E.div(
    "The following conventions are used for the completion of operations:",
        HTM_E.ul(HTM_E.li(HTM_E.b("Refinement")," operation (denoted by ", HTM_E.b("bold text")," or ", HTM_E.strike("strikethrough text"), "): Is used to add details to a requirement (including replacing an assignment with a more restrictive selection) or to remove part of the requirement that is made irrelevant through the completion of another operation, and thus further restricts a requirement."),
             HTM_E.li(HTM_E.b("Selection"),"(denoted by ", HTM_E.i("italicized text"),"): Is used to select one or more options provided by the [CC] in stating a requirement."),
             HTM_E.li(HTM_E.b("Assignment")," operation (denoted by ", HTM_E.i("italicized text"),"): Is used to assign a specific value to an unspecified parameter, such as the length of a password. Showing the value in square brackets indicates assignment."),
             HTM_E.li(HTM_E.b("Iteration")," operation: Is indicated by appending the SFR name with a slash and unique identifier suggesting the purpose of the operation, e.g. \"/EXAMPLE1.\"")
     )
    )
        

class generic_pp_doc(object):
    def __init__(self, root, workdir, boilerplate):
        self.root = root
        self.globaltags = {}
        self.ids = {}
        self.boilerplate = boilerplate
        self.edocs = self.make_edocs(workdir)
        self.sel_sfrs = {}
        self.opt_sfrs = {}
        self.obj_sfrs = {}
        self.impl_sfrs = {}
        self.fams_to_sfrs = {}
        self.man_sfrs = self.rx("//cc:f-component[not(cc:depends)]")
        self.are_sfrs_mingled = False

        self.categorize_sfrs()
        self.outline = [0]
        self.is_appendix = False
        self.abbrs = {}                       # Full set of abbreviaiotns
        #        self.plural_to_abbr = {}              # Map from plural abbreviations to abbreviation
        #        self.used_abbrs = set()               # Set of abbreviations that we've seen
        #        self.full_abbrs = {}                  # Map from full in-text definition to abbreviation
        self.discoverables_to_ids = {}        # List of terms we're looking for
        #        self.test_number_stack = [0]
        self.register_threats_assumptions_objectives_policies()
        self.register_sfrs()
        self.register_abbrs()
        self.counters={}

    def get_next_counter(self, ctr_type):
        if ctr_type in self.counters:
            self.counters[ctr_type]+=1
            return self.counters[ctr_type]
        else:
            self.counters[ctr_type]=1
            return 1
        
    def register_sfrs(self):
        for fcomp in self.root.findall(".//cc:f-component", NS):
            id = self.fcomp_cc_id(fcomp)
            self.register_keyterm(id.upper(),id)
            for fel in fcomp.findall(".//cc:f-element", NS):
                felid=self.fel_cc_id(fel)
                self.register_keyterm(felid.upper(), felid)
                
    def get_all_abbr_els(self):
        return self.rfa("//cc:term[@abbr]")+\
            self.boilerplate.findall("//cc:cc-terms/cc:term[@abbr]", NS)

    def register_threats_assumptions_objectives_policies(self):
        for aa in self.rfa("//cc:threat")+self.rfa("//cc:assumption")+self.rfa("//cc:SO")+self.rfa("//cc:SOE")+self.rfa("//cc:OSP"):
            if aa.find("cc:description", NS) is not None:
                ccname = aa.attrib["name"]
                self.register_keyterm(ccname, ccname)
                
    def register_abbrs(self):
        for term in self.get_all_abbr_els():
            abbr = term.attrib["abbr"]
            self.register_keyterm(abbr, "long_abbr_"+abbr)
            if "plural" in term.attrib:
                self.register_keyterm(term.attrib["plural"], "long_abbr_"+abbr)
            
    def register_keyterm(self, word, id):
        if len(word) > 1 and not(word.startswith(".")):
            self.discoverables_to_ids[word]=id

    def add_text(self, node, text):
        pp_util.append_text(node,text)
        
    def categorize_sfrs(self):
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
        
        
    def make_edocs(self, workdir):
        ret = {}
        for external in self.root.findall(".//cc:*[cc:git]", NS):
            ret[external.attrib["id"]] = edoc.Edoc(external, workdir)
        return ret
    
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


    def xrefs_in_text(self, node, content, regex, insertspot=0):
        if regex is None or content is None:
            return content
        matches = regex.finditer(content)
        origtext = content
        try:
            match=next(matches)
        except:
            return content
        ret = origtext[:match.start()]
        last=match.end()
        matchtext = match.group()
        id = self.discoverables_to_ids[matchtext]
        prevnode = HTM_E.a({"href":"#"+id, "class":"discovered"}, matchtext)
        newnodes=[prevnode]
        for match in matches:
            prevnode.tail = origtext[last:match.start()]
            last = match.end()
            id = self.discoverables_to_ids[match.group()]
            prevnode = HTM_E.a({"href":"#"+id}, match.group())
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
        
    def add_discoverable_xrefs(self, node):
        keys = sorted(self.discoverables_to_ids.keys(), key=len, reverse=True)
        bracketed=set()
        for key in keys:
            if key[0]=='[':
                keys.remove(key)
                bracketed.add(key)
        regex_str = "("+"|".join(map(backslashify,bracketed))+")|(?<!-)\\b("+"|".join(map(backslashify, keys))+")\\b"
        print("Regex string is " + regex_str)
        regex = re.compile(regex_str)
        self.add_xrefs_recur(node, regex)        

    def fix_numbered_xrefs(self, doc):
        dynrefs = doc.xpath(".//*[contains(@class,'dynref')]")
        for dynref in dynrefs:
            refid = dynref.attrib["href"][1:]
            print("Looking for " + refid)
            reffed = doc.find(".//*[@id='"+refid+"']")
            if reffed is None:
                print("Could not find dynamic reference: " + refid)
                continue
            label_node = reffed.find("./*[@class='dynid_']")
            if label_node is None:
                text = reffed.text
            else:
                text = label_node.text
            print("Doing the thing: "+text + " yyy: " +text.split(" ")[-1])
            pp_util.append_text(dynref, " "+text)
        
    def to_html(self):
        doc = self.start()
        self.fix_numbered_xrefs(doc)
        self.add_discoverable_xrefs(doc)
        return doc
    
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

    def sec(self, *args):
        # h2 doesn't matter as the tag is changed
        ret = HTM_E.h2(*args)
        depth = len(self.outline)
        ret.tag="h"+str(depth)                       
        self.outline[-1]=self.outline[-1]+1
        if self.is_appendix:
            prefix=base_10_to_alphabet(self.outline[0])
            if len(self.outline)==1:
                prefix="Appendix " + prefix + " - " + NBSP
            else:
                prefix+="."+ ".".join(map(str, self.outline[1:]))
        else:
            prefix=".".join(map(str, self.outline))

        if "id" not in ret.attrib:
            ret.attrib["id"]="sec_"+prefix.replace(" ","_")+"-"
            
        self.outline.append(0)
        toc_entry=""
        for aa in range(depth):
            toc_entry += NBSP+ NBSP
        toc_entry +=  prefix + NBSP+ NBSP + NBSP + ret.text        
        ret.text = prefix+" "+ret.text

        self.toc.append(HTM_E.a({"href":"#"+ret.attrib["id"]}, toc_entry))
        return ret
    
    def end_section(self):
        if len(self.outline)==0:
            print("Poping from zero.")
        else:
            self.outline.pop()
        
    def start(self):
        head = HTM_E.head(
                HTM_E.meta({"content":"text/html;charset=utf-8", "http-equiv":"Content-Type"}),
                HTM_E.meta({"content":"utf-8","http-equiv":"encoding"}),
                HTM_E.title(self.title())
        )
        ret = HTM_E.html(head)
        pp_util.add_js(head)
        css_text = css_content.fx_pp_css()
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

    def handle_figure(self, el, par):
        id=el.attrib["id"]
        div=adopt(par, HTM_E.div({"class":"figure","id":"div_fig_"+id}))
        attrs={"id":"fig_"+id, "src":el.attrib["entity"]}
        div.append(HTM_E.img(attrs))
        div.append(HTM_E.br())
        self.create_ctr("figure", id, div, "Figure ")
        self.add_text(div, el.attrib["title"])


    
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
        self.toc = adopt(body, (HTM_E.div({"class":"toc","id":"toc"})))
        return 

    def fel_cc_id(self, node):
        fcomp = node.xpath("ancestor::cc:f-component", namespaces=NS)[0]
        index = fcomp.findall("cc:f-element",NS).index(node)+1
        return self.fcomp_cc_id(fcomp, suffix="."+str(index))
        
        
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
            self.add_text(parent, defcon)
            return False
        if node.text is None and len(node)==0:
            return False
        self.add_text(parent, node.text)
        for child in node:
            self.apply_templates_single(child,parent)
            self.add_text(parent,child.tail)
        return True
            
    def handle_section(self, node, title, id, parent):
        print("Handling section: "+ title)
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
            self.add_text(parent, "These assumptions are made on the Operational Environment (OE) in order to be able to ensure that the security functionality specified in the PP-Module can be provided by the TOE. If the TOE is placed in an OE that does not meet these assumptions, the TOE may no longer be able to provide all of its security functionality.")

    
    def doctype(self):
        return "PP"


    def get_all_dependencies(self, node):
        choices={}
        selections={}
        features={}
        externals={}
        bases={}
        for depends in node.findall("./cc:depends", NS):
            if depends.attrib is None:
                continue
            doc=None
            for external in depends.findall("./cc:external-doc", NS):
                doc=external.attrib["ref"]
            for attr in depends.attrib:
                theid = depends.attrib[attr]
                # ret[doc+depends.attrib[attr]]=1
                if doc is not None:
                    add_to_map_to_map(externals, doc, theid)
                else:
                    ided = self.rf("//cc:*[@id='"+theid+"']")
                    if ided is None:
                        print("Failed to find an item with the following id:\""+theid+"\".")
                    else:
                        if ided.getparent().getparent().tag == CC+"choice":
                            choices[theid]=1
                        elif ided.tag==CC+"base-pp":
                            bases[theid]=1
                        elif ided.tag==CC+"selectable":
                            selections[theid]=1
                        elif ided.tag==CC+"feature":
                            features[1]=1
                        else:
                            print("Failed to sort the dependee:\""+theid+"\".")
        return [choices, selections, features, externals, bases]

    
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
            for ecd in ecds:
                self.handle_ecd(ecd, classid, span)
            self.end_section()
        self.end_section()
        self.end_section()
        
    def handle_ecd(self, famnode, classid, span):
        famId = famnode.attrib["fam-id"]
        desc = famnode.find("cc:class-description",NS)
        self.handle_content(desc, span, defcon="This "+self.doctype() +\
                            " defines the following extended components as part of the "+\
                            classid + " class originally defined by CC Part 2:" )
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
        par.append(HTM_E.h4(cc_id+" "+sfr.attrib["name"]))
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

    def start_appendixes(self):
        self.outline[0]=-1
        self.is_appendix = True

            
    def opt_app(self,level,word,sfrs, par, suffix=""):
        par.append(self.sec({"id":word.replace(" ","-")+"-"},word+" Requirements"))
        if len(sfrs)==0:
            self.add_text(par, "This PP-Module does not define any "+word+" SFRs.\n")
        else:
            self.handle_sparse_sfrs(sfrs, par)
        self.end_section()


    def handle_optional_requirements(self, par):
        par.append(self.sec({"id":"optional-appendix-"},"Optional SFRs"))
        self.opt_app("2", "Strictly Optional", self.opt_sfrs, par)
        self.opt_app("2", "Objective", self.obj_sfrs, par)
        self.opt_app("2", "Implementation-based", self.impl_sfrs, par)
        self.end_section()

    def handle_selection_based_requirements(self, node, par):
        return self.opt_app("1", "Selection-based", self.sel_sfrs, par)

            
    def handle_security_objectives_operational_environment(self, parent):
        soes=self.rfa("cc:SOEs")
        if len(soes)>0:
            self.add_text(parent,"""The OE of the TOE implements technical and procedural measure
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
            self.add_text(parent, "This PP-Module does not define any objectives for the OE.")

        
    def create_ctr(self, ctrtype, id ,parent, prefix, sep=": ", child=None):
        ctrcount = str(self.get_next_counter(ctrtype))
        print("Counter count is: " + ctrcount)
        span = HTM_E.span({"class":"ctr",
                           "data-counter-type":"ct-"+ctrtype,
                           "id":id}, prefix,
                          HTM_E.span({"class":"counter"},ctrcount+sep)
                          )
        parent.append(span)
        self.handle_content(child, span)
        

        
    def create_bibliography(self, par):
        par.append(HTM_E.h1({"id":"appendix-bibliography"},"Bibliography"))
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
        
    def create_acronym_listing(self, par):
        par.append(HTM_E.h1({"id":"acronyms"},"Acronyms"))
        table = adopt(par, HTM_E.table())
        table.append(HTM_E.tr(HTM_E.th("Acronym"), HTM_E.th("Meaning")))
        suppress_el=self.rf("//cc:suppress")
        if suppress_el is None:
            suppress_list=[]
        else:
            suppress_list=suppress.text.split(",")
        term_els = self.get_all_abbr_els()
        term_els.sort(key=lambda t_el:t_el.attrib["full"].upper())
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
            parent.append(HTM_E.div("choices are made"))
        if len(externals)>0:
            parent.append(HTM_E.div("selections are are made in base"))
        if len(selections)>0:
            parent.append(HTM_E.div("selections are made"))
        if len(features)>0:
            parent.append(HTM_E.div("features are made"))
        if len(bases)>0:
            baselist = ""
            for base in bases:
                print("HEREHRERHE)")
                basenode = self.rf("//cc:*[@id='"+base+"']")
                self.make_xref(basenode, parent)
            parent.append(HTM_E.div("is a base. "))            


        
        
 #    <xsl:choose>
 #      <!-- When it depends on a choice -->
 #      <xsl:when test="//cc:choice[@prefix]//@id=current()//cc:depends/@*">
 #         <xsl:value-of select="//cc:choice[.//@id=current()//cc:depends/@*]/@prefix"/>
 #         <xsl:for-each select="cc:depends/@*">
 #            <xsl:if test="position()!=1">,</xsl:if>
            
 #            <xsl:apply-templates select="//cc:selectable[./@id=current()]" mode="make_xref"/>
 #         </xsl:for-each>
 #      </xsl:when>
 #      <!--If we're not looking at a row. Not sure where @hide comes from -->
 #      <!-- <xsl:when test="cc:depends[not(@hide)] and not(self::htm:tr)"><xsl:value-of select="$words"/> -->
 #      <xsl:when test="not(self::htm:tr)"><xsl:value-of select="$words"/>
 #      <ul> <xsl:for-each select="cc:depends"><li>
 #        <xsl:variable name="uid" select="@*[1]"/>
 #         <xsl:choose>
 #           <xsl:when test="cc:external-doc">
 #             <xsl:variable name="ref" select="cc:external-doc/@ref"/>
 #             <xsl:variable name="path" select="concat($work-dir,'/',$ref,'.xml')"/>

 #             <xsl:for-each select="@*"><xsl:if test="position()!=1">,<xsl:text> </xsl:text></xsl:if><span class="no-link-sel"><xsl:apply-templates select="document($path)//cc:selectable[@id=current()]" mode="make_xref"/></span>
 #             </xsl:for-each>
 #             is selected from 
 #             <xsl:apply-templates select="document($path)//cc:f-element[.//cc:selectable/@id=$uid]" mode="getId"/> from  <xsl:apply-templates select="//*[@id=$ref]" mode="make_xref"/> 
 #           </xsl:when><xsl:when test="//cc:f-element//cc:selectable/@id=$uid">
 #             <xsl:for-each select="@*"><xsl:if test="position()!=1">,<xsl:text> </xsl:text></xsl:if><xsl:apply-templates select="//cc:selectable[@id=current()]" mode="make_xref"/>
 #             </xsl:for-each>
 #             is selected from 
 #             <xsl:apply-templates select="//cc:f-element[.//cc:selectable/@id=$uid]" mode="getId"/>
 #           </xsl:when> <xsl:when test="//cc:selectable[@id=$uid]">For 
 #             <xsl:for-each select="@*">
 #               <xsl:if test="position()!=1">/</xsl:if>
 #             <xsl:apply-templates select="//cc:selectable[./@id=current()]"/>
 #             </xsl:for-each> TOEs
 #         </xsl:when><xsl:otherwise>
 #           the TOE implements 
 #           <xsl:for-each select="@*">
 #             <xsl:if test="position()!=1">, </xsl:if>
 #             "<xsl:value-of select="//cc:feature[@id=current()]/@title"/>"
 #           </xsl:for-each>
 #         </xsl:otherwise></xsl:choose>
 #              <!-- This is a module piece... -->
 #      </li></xsl:for-each> </ul>
 #      </xsl:when></xsl:choose>
 # </xsl:template>


        
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
            mfs = node.findall(".//cc:management-function[cc:app-note]",NS)
            #mfs = node.findall(".//cc:management-function",NS)
            if len(mfs)==0:
                return
            adopt(div_reqdesc,HTM_E.div({"id":"mf-spec-notes"},"Function-specific Application Notes"))
            for mf in mfs:
                self.set_shortcut(mf)
                note_head = adopt(div_reqdesc,HTM_E.div({"class":"mf-spec-note"}))
                self.make_xref(mf, note_head)
                self.handle_content(mf.find("cc:app-note", NS), div_reqdesc)
    
    def get_meaningful_ancestor(self, refid):
        ret = self.rx("//cc:f-element[.//@id='"+refid+"']|//cc:choice[.//@id='"+refid+"']|//cc:feature[.//@id='"+refid+"']")
        if len(ret) != 1:
            raise Exception("Should only be one thing")
        return ret[0]


    def get_fcomp_status_mingled(self, node):
        ret=""
        if node in self.sel_sfrs:
            ret="This is a selection-based component. Its inclusion depends upon selection from:"
            for dependsId in node.xpath("cc:depends/@*", namespaces=NS):
                fcomp = self.rx("//cc:f-element[.//cc:selectable//@id='"+dependsId+"']") 
                if len(fcomp)>0:
                    ret+=" " + self.fel_cc_id(fcomp[0])
            if node.find("cc:depends/cc:optional",NS) is not None:
                ret += "This component may also be optionally be included in the ST as if optional."
        elif node in self.obj_sfrs:
            ret="This is an objective component."
        elif node in self.opt_sfrs:
            ret="This is an optional component."
        return ret


    def get_fcomp_status_isolated(self, node):
        ret=""
        if node in self.sel_sfrs:
            ret="The inclusion of this selection-based component depends upon selection from:"
            for dependsId in node.xpath("cc:depends/@*", namespaces=NS):
                fels = self.rx("//cc:f-element[.//cc:selectable//@id='"+dependsId+"']")
                if len(fels)==1:
                    ret+=" " + self.fel_cc_id(fels[0])
                else:
                    print("WARNING: Failed to find exactly one element that contains a selectable with the id: "+dependsId)
            ret+="."
            if node.find("cc:depends/cc:optional",NS) is not None:
                ret += "This component may also be optionally be included in the ST as if optional."
        return ret


    
    def get_fcomp_status(self, node):
        if self.are_sfrs_mingled:
            return self.get_fcomp_status_mingled(node)
        else:
            return self.get_fcomp_status_isolated(node)
        
    
    def handle_fcomponent(self, node, par):
        formal = self.fcomp_cc_id(node)
        div = adopt(par, HTM_E.div({"class":"comp", "id":formal}))
        div.append(HTM_E.h4(formal + " "+ node.attrib["name"]))
        statustext=self.get_fcomp_status(node)
        if not statustext=="":
            div.append(HTM_E.div({"class":"statustag"}, statustext))
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
                if len(titles)>0:
                    self.end_section()
                titles[title]=1
                par.append(self.sec({"id":id}, title))
            self.handle_fcomponent(sfr, par)
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
        elif tag == "{https://niap-ccevs.org/cc/v1}section":
            self.template_oldsection(node, parent)
        elif tag == "{https://niap-ccevs.org/cc/v1}appendix":
            self.template_oldsection(node, parent)
        elif tag.startswith("{http://www.w3.org/1999/xhtml}"):
            self.template_html(node, parent)
        elif tag == "{https://niap-ccevs.org/cc/v1}xref":
            self.template_xref(node, parent)
        elif tag == "{https://niap-ccevs.org/cc/v1}tech-terms":
            self.template_tech_terms(node, parent)
        elif tag=="{https://niap-ccevs.org/cc/v1}usecases":
            self.template_usecases(node, parent)
        elif tag=="{https://niap-ccevs.org/cc/v1}assumptions"\
             or tag=="{https://niap-ccevs.org/cc/v1}cclaims"\
             or tag=="{https://niap-ccevs.org/cc/v1}threats"\
             or tag=="{https://niap-ccevs.org/cc/v1}OSPs"\
             or tag=="{https://niap-ccevs.org/cc/v1}SOs"\
             or tag=="{https://niap-ccevs.org/cc/v1}SOEs":
            self.template_assumptions_cclaims_threats_OSPs_SOs_SOEs(node, parent)
        elif tag=="{https://niap-ccevs.org/cc/v1}sfrs":
            self.template_sfrs(node, parent)
        elif tag=="{https://niap-ccevs.org/cc/v1}f-component" or\
             tag=="{https://niap-ccevs.org/cc/v1}ext-comp-def" or\
             tag=="{https://niap-ccevs.org/cc/v1}base-pp" or\
             tag=="{https://niap-ccevs.org/cc/v1}depends":
            return 
        elif tag=="{https://niap-ccevs.org/cc/v1}f-element":
            self.template_felement(node, parent)
        elif tag=="{https://niap-ccevs.org/cc/v1}title": 
            self.apply_templates(node, parent)
        elif tag=="{https://niap-ccevs.org/cc/v1}management-function-set":
            self.template_management_function_set(node, parent)
        elif tag=="{https://niap-ccevs.org/cc/v1}ctr":
            self.template_ctr(node, parent)
        elif tag=="{https://niap-ccevs.org/cc/v1}no-link":
            span=adopt(parent, HTM_E.span({"class":"no-link"}))
            self.handle_content(node, parent, span)
        elif tag=="{https://niap-ccevs.org/cc/v1}manager":
            td = adopt(parent, HTM_E.td())
            self.handle_content(node, td)
        elif tag=="{https://niap-ccevs.org/cc/v1}figure":
            self.handle_figure(node, parent)
        elif tag=="{https://niap-ccevs.org/cc/v1}text" or\
             tag=="{https://niap-ccevs.org/cc/v1}description":
            self.handle_content(node, parent)
        elif tag=="{https://niap-ccevs.org/cc/v1}selectables":
            self.template_selectables(node, parent)
        elif tag=="{https://niap-ccevs.org/cc/v1}assignable":
            self.template_assignable(node, parent)
        elif tag=="{https://niap-ccevs.org/cc/v1}int":
            self.template_int(node, parent)
        elif tag=="{https://niap-ccevs.org/cc/v1}_":
            self.make_xref(self.shortcut, parent)
        else:
            raise Exception("Can't handle: " + node.tag + ": " +node.text)


    def get_pre(self, el):
        if "pre" in el.attrib:
            return el.attrib["pre"]
        if el.tag == "{https://niap-ccevs.org/cc/v1}figure":
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
        self.add_text(par,"[")
        par.append(HTM_E.b("selection"))
        if pp_util.is_attr(node, "onlyone", "yes"):
            par.append(HTM_E.b(", choose one of"))
        self.add_text(par, ": ")
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
            self.add_text(par,lagsep)
            lagsep=sep
            span = adopt(par,HTM_E.span({"class":"selectable-content"+extraclass, "id":id}))
            self.handle_content(selectable, span)
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
    
    def set_shortcut(self, node):
        self.shortcut = node

    def make_xref_mf(self, id, parent):
        parent.append(HTM_E.a({"href":"#"+id,"class":"dynref"}))

    def make_xref_generic(self, target, parent, ref, deftext=""):
        a_el=adopt(parent, HTM_E.a({"href":"#"+target.attrib["id"],"class":"dynref"}))
        if not self.handle_content(ref, a_el):
            self.add_text(a_el, deftext)
        
    def make_xref_section(self, id, parent):
        parent.append(HTM_E.a({"href":"#"+id,"class":"dynref"},"section "))

    def make_xref_bibentry(self, node, parent):
        txt = "["+node.find("./cc:tag", NS).text+"]"
        anchor="#"+node.attrib["id"]
        parent.append(E.a(txt, href=anchor))
        
    def make_xref(self, target, parent, ref=None):
        if target.tag.startswith("{https://niap-ccevs.org/cc/v1/section}"):
            self.make_xref_section(target, pp_util.localtag(target.tag), parent)
        elif target.tag == "{https://niap-ccevs.org/cc/v1}base-pp":
            theid= target.attrib["id"]
            print("The id is " + theid)
            self.edocs[theid].make_xref_edoc(parent)
        elif target.tag == "{https://niap-ccevs.org/cc/v1}entry":
            self.make_xref_bibentry(target, parent)
        elif target.tag == "{https://niap-ccevs.org/cc/v1}management-function":
            self.make_xref_mf(self.derive_id(target), parent)
        elif target.tag == "{https://niap-ccevs.org/cc/v1}figure":
            self.make_xref_generic(target, parent, ref, "figure")
        elif target.tag == "{https://niap-ccevs.org/cc/v1}ctr":
            self.make_xref_generic(target, parent, ref, "figure")
            # findex = str(self.get_global_index(target))
            # id=self.derive_id(target)
            # parent.append(HTM_E.a({"href":"#"+id}, "Function "+findex))
            # # self.handle_content(target,parent)
        else:
            raise Exception("Cannot handle: " + target.tag + " " + target.text)

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

        


    
