import lxml.etree as ET
from lxml.builder import E
from lxml.builder import ElementMaker
import math
import edoc

# Mine
import css_content
import pp_util
from pp_util import log
import auto_xref

add_text=pp_util.append_text


NS = edoc.NS
CC="{"+NS['cc']+"}"
SEC="{"+NS['sec']+"}"

DONT_PROCESS={CC+"f-component",CC+"ext-comp-def",CC+"base-pp",CC+"depends",CC+"optional",
              CC+"TSS",CC+"Tests",CC+"Guidance", CC+"KMD", CC+"no-tests", CC+"a-component",
              CC+"f-element", CC+"a-element",CC+"audit-event", CC+"consistency-rationale",
              CC+"comp-lev", CC+"management", CC+"audit", CC+"dependencies", CC+"objective",
              CC+"optional", CC+"depends", CC+"ext-comp-def-title",CC+"elev"}
TRANSPARENT={CC+"aactivity", CC+"text",CC+"description", CC+"choice"}

# SVG_NS="http://www.w3.org/2000/svg"
# SVG="{%s}"%SVG_NS
# OUT_NSMAP={None: SVG_NS}
#SVG_E=ElementMaker(namespace="http://www.w3.org/2000/svg")
NBSP=str(chr(0xA0))
SVG_E=ElementMaker()
HTM_E=pp_util.get_HTM_E()
adopt=pp_util.adopt

def get_attr_or(el, attrname, default=None):
    if el is not None and attrname in el.attrib:
        return el.attrib[attrname]
    return default

def find_fix(xpath, docroot, el):
    target = docroot.xpath(xpath)
    if len(target)==0:
        return False
    parent = target[0]
    ctr_el = parent[0]
    el.text = ctr_el.text
    return True

def dynref(id, prefix="", suffix=""):
    return HTM_E.a({"href":"#"+id}, prefix, dynref_num(id), suffix)

def dynref_num(id):
    """ 
    This is only going to make the counter part.
    """
    return HTM_E.span({"data-target":id, "class":"dynref"})

def attrs(clazz,id=None):
    """
    Populates new dictionary with class and maybe id attributes
    
    :param clazz Value to be associated with 'class'
    :param id Value to be associated with 'id'
    :ret Dictionary for element attributes (Element.attrib)
    """
    ret={}
    if clazz is not None:
        ret["class"]=clazz
    if id is not None:
        ret["id"]=id
    return ret


A_UPPERCASE = ord('A')
ALPHABET_SIZE = 26

def add_grouping_row(table, text, size):
    """
    Adds a grouping row, which looks like a column that spans several rows

    :param table Output element 
    :param text Text to be written out
    :param size 
    :ret
    """
    rowspan=size+2
    # Add two blank rows, so that it doesn't screw up the alternating coloring
    attrs={"rowspan":str(rowspan)}
    table.append(HTM_E.tr({"class":"major-row"}, HTM_E.td(attrs, text), inv_cell))
    table.append(HTM_E.tr(inv_cell))

def is_in_choice(el):
    """
    Figures out whether the element is in a choice element.

    :param el The element in question
    :ret True if the element has a cc:choice ancestor. False otherwise
    """
    return len(el.xpath("ancestor::cc:choice", namespaces=NS))>0
    
    
def inv_cell():
    """
    Creates a unseen cell.

    :ret A hidden cell
    """
    return HTM_E.td({"style":"display:none;"})

def is_comment(node):
    """
    Checks if a node is an XML comment (and not an element)

    :param node The node in question.
    :ret True if it not an element
    """
    return not isinstance(node.tag,str)    

def add_to_map_to_map(mappy, key, attr):
    """
    Adds a 
    
    :param
    :ret
    """
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

    :param number: The number in question
    """
    while number: 
        number, remainder = divmod(number-1, ALPHABET_SIZE)
        yield remainder

def base_10_to_alphabet(number):
    """Convert a decimal number to its base alphabet representation
    :param number: The number in question
    :returns A string representing the number
    """
    return ''.join(
            chr(A_UPPERCASE + part)
            for part in _decompose(number+1)
    )[::-1]

def make_sort_key_stringnum(s):
    """
    :param
    :ret
    """
    spl=s.split(".")
    return spl[0]+"."+spl[1].rjust(3)

def sec_impl(outline, is_appendix, toc, h_el):
    """
    Calculates a heading for an outline style heading numbering.
    Adds it to the table of contents.

    :param outline: Stack that records the state of the headings
    :param is_appendix: Boolean indicating whether this is an appendix
    :param toc: Output XML element for the table of contents
    :param h_el: The output element
    
    :returns: h_el for convenience
    """
    # h2 doesn't matter as the tag is changed
    depth = len(outline)
    h_el.tag="h"+str(depth)
    outline[-1]=outline[-1]+1

    prefix=""
    if is_appendix:
        ctr=base_10_to_alphabet(outline[0])
        if len(outline)==1:
            prefix = "Appendix "
            ctr=ctr + " - " + NBSP
        else:
            ctr+="."+ ".".join(map(str, outline[1:]))
    else:
        ctr=".".join(map(str, outline))

    if "id" not in h_el.attrib:
        h_el.attrib["id"]="sec_"+ctr.replace(" ","_")+"-"
    outline.append(0)
    toc_entry=""
    for aa in range(depth):
        toc_entry += NBSP+ NBSP
    prevtext = h_el.text
    toc_entry +=  prefix + ctr + NBSP+ NBSP + NBSP + prevtext
    h_el.text = prefix
    adopt(h_el, HTM_E.span({"class":"ctr"},ctr)).tail = " " + prevtext
    toc.append(HTM_E.a({"href":"#"+h_el.attrib["id"]}, toc_entry))
    return h_el



def def_attr(id):
    """
    Creates attributes for an HTML element that defines something

    :param id: Unique id of node
    :returns Dictionary of attributes
    """
    return {"id":id, "class":"def_", "href":"#"+id}

defargs={'fill':'black',
         'font-size':'15'}
boxargs={'height':'17','fill':'none','stroke':'black'}


def drawbox(parent, ybase,boxtext,ymid, xbase=0):
    """
    Creates an SVG rectangle with text

    :param parent: HTML element that should be there parent
    :param ybase: Y-coordinate that roughly corresponds to the bottom of the box
    :param boxtext: Text for the box
    :param ymid: Y-coordinate for the base box
    :param xbase: X-ccordinate for the base box
    """
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

def is_empty(node):
    """
    Checks if this node is empty

    :param node: The node in question
    :returns True if this node has no text and no children.
    """
    if node.text is not None and node.text != "":
        return False
    return len(node)==0
        

def is_optional(node):
    """
    Checks if this Element is considered optional.
    It's mostly for f-component and audit-event elements.

    :param node: The node in question
    :ret True if the node has direct child that is 'optional'
    """
    return node.find("cc:optional", NS) is not None

        
def get_convention_explainer():
    """
    :returns a div element containing the convention explainer.
    """
    return HTM_E.div(
    "The following conventions are used for the completion of operations:",
        HTM_E.ul(HTM_E.li(HTM_E.b("Refinement")," operation (denoted by ", HTM_E.b("bold text")," or ", HTM_E.strike("strikethrough text"), "): Is used to add details to a requirement (including replacing an assignment with a more restrictive selection) or to remove part of the requirement that is made irrelevant through the completion of another operation, and thus further restricts a requirement."),
             HTM_E.li(HTM_E.b("Selection"),"(denoted by ", HTM_E.i("italicized text"),"): Is used to select one or more options provided by the [CC] in stating a requirement."),
             HTM_E.li(HTM_E.b("Assignment")," operation (denoted by ", HTM_E.i("italicized text"),"): Is used to assign a specific value to an unspecified parameter, such as the length of a password. Showing the value in square brackets indicates assignment."),
             HTM_E.li(HTM_E.b("Iteration")," operation: Is indicated by appending the SFR name with a slash and unique identifier suggesting the purpose of the operation, e.g. \"/EXAMPLE1.\"")
     )
    )
        

def convert_none_text_to_emptys(node):
    """
    This converts elements that have text==None to text=="", so
    that they will be written out as <span></span> instead of <span/>
    which browsers have trouble reading. Break elements (<br/>) are 
    the only elements which should have text==None. It recurs on
    all child nodes of the given node.

    :param node: The root element of the tree that is to be converted.
    """
    if node.tag is None or pp_util.localtag(node.tag) == "br":
        return
    if node.text is None:
        node.text=""
    for child in node:
        convert_none_text_to_emptys(child)


def harvest_ids(ids, el):
    """
    Retrieves all the ids from a subtree

    :param ids: A set to which ids should be added
    :param el: The root element of the subtree
    """
    if "id" in el.attrib:
        ids.add(el.attrib["id"])
    for child in el:
        harvest_ids(ids, child)
                
def does_rule_contain_id(rule, ids):
    """
    Figures out whether a rule references any id in ids

    :param rule: The XML element of the rule containing the needles.
    :param ids: A set of IDs (haystack) to be searched.
    :returns True if any of the 'ref-id' elements references an
    id in _ids_
    """
    for refid in rule.findall(".//cc:ref-id", NS):
        if refid.text.strip() in ids:
            return True
    return False
        
class generic_pp_doc(object):
    """
    Superclass for PP, Module, and Package documents.
    """
    def __init__(self, root, workdir, boilerplate):
        """
        Initializes a generic PP document
        :param  root: Root element of the input document
        :param  workdir: The working directory
        :param  boilerplate: The boilerplate object
        :ret A generic PP document
        """

        self.root = root
        # A cache that keeps of list of things that are globally numbered, like 'selectables'
        self.globaltags = {}                              
        self.boilerplate = boilerplate
        self.pkgs = self.make_edocs(workdir)
        self.sel_sfrs = {}
        self.opt_sfrs = {}
        self.obj_sfrs = {}
        self.impl_sfrs = {}
        self.fams_to_sfrs = {}
        self.test_titles={}
        self.man_sfrs = self.rx("//cc:f-component[not(cc:depends or cc:objective or cc:optional)]")
        self.are_sfrs_mingled = False
        self.node_to_ccid={}
        self.group_audit_map={}
        self.categorize_sfrs()
        self.abbrs = {}                       # Full set of abbreviaiotns
        self.xreffer = auto_xref.auto_xreffer()
        
        #        self.plural_to_abbr = {}              # Map from plural abbreviations to abbreviation
        #        self.used_abbrs = set()               # Set of abbreviations that we've seen
        #        self.full_abbrs = {}                  # Map from full in-text definition to abbreviation
        #        self.test_number_stack = [0]
        self.register_threats_assumptions_objectives_policies()
        self.register_sfrs()
        # self.register_abbrs()
        self.counters={}
        
        # Keeping: tuple( target_node, output anchor, element , 
        # self.broken_refs=set()


    def maybe_make_usecase_appendixes(self, out):
        """
        Makes a usecase appendix if there exists usecases with rules
        :param  out: The output HTML where we're writing to
        """
        
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
                add_text(out, "The use case ")
                self.make_xref(uc_id, out)
                add_text(out," makes no changes to the base requirements.")
            else:
                add_text(out, "The configuration for ")
                self.make_xref(uc_id, out)
                add_text(out," modifies the base requirements as follows:")
                out_div = adopt(out, HTM_E.div())
                self.apply_use_case_templates(config_in, out_div)
            self.end_section()
        self.end_section()
        


        
    def derive_plural(self):
        """
        Derives a term that describes the class of 
        products (e.g. "operating systems") 
        that this document applies to.

        :returns A string representing the class of products.
        """
        
        return edoc.derive_products(self.root)
        
    def get_next_counter(self, ctr_type):
        """
        Gets the numeric value of the next counter.
        Increments the counter type
        
        :param ctr_type: A string that designating
        this counter's type (e.g. "Figure" or "Table")
        :returns The number of ctrs of this 
        """
        
        if ctr_type in self.counters:
            self.counters[ctr_type]+=1
            return self.counters[ctr_type]
        else:
            self.counters[ctr_type]=1
            return 1

    # def register_keyterm(self, term, id):
    #     self.xreffer.register_keyterm(term, id)
        
    def register_sfrs(self):
        """
        Registers the SFRs (components and elements)  with 
        the XRef discovery mechanism.
        """
        
        for fcomp in self.root.findall(".//cc:f-component", NS):
            id = self.fcomp_cc_id(fcomp)
            # self.register_keyterm(id,id)
            for fel in fcomp.findall(".//cc:f-element", NS):
                felid=self.fel_cc_id(fel)
                # self.register_keyterm(felid.upper(), felid)

                
    def get_all_abbr_els(self):
        """
        Retrieves all the abbreviations that apply to this document.
        Both the document itself and the boilerplate.

        :returns A iterable list of XML abbreviations elements.
        """
        
        return self.rfa("//cc:term[@abbr]")+\
            self.boilerplate.findall("//cc:cc-terms/cc:term[@abbr]", NS)

    def register_threats_assumptions_objectives_policies(self):
        """
        Registers all the threats, assumptions, objectives, and
        security policies with the automatic XREF mechanisms.
        """
        
        for aa in self.rfa("//cc:threat")+self.rfa("//cc:assumption")\
            +self.rfa("//cc:SO")+self.rfa("//cc:SOE")+self.rfa("//cc:OSP"):
            if aa.find("cc:description", NS) is not None:
                ccname = aa.attrib["name"]
                # self.register_keyterm(ccname, ccname)

    def get_ccid_for_ccel(self, ccel_el):
        """
        Retries the CC ID for an f-element or a-element.
        Once the value is calculated, it is stored in the 
        self.node_to_ccid cache.

        :param  ccel_el: The CC XML f-element in question
        :returns A string representing the CC ID
        """
        
        if ccel_el in self.node_to_ccid:
            return self.node_to_ccid[ccel_el]
        component = ccel_el.xpath("ancestor::cc:a-component[1]|ancestor::cc:f-component[1]", namespaces=NS)[0]
        comp_cc_id = component.attrib["cc-id"].upper()+"."
        suffix=""
        if "iteration" in component.attrib:
            suffix="/"+component.attrib["iteration"]
        if ccel_el.tag == CC+"f-element":
            kid_els = component.xpath("cc:f-element", namespaces=NS)
            ctr=0
            for kid in kid_els:
                ctr+=1
                self.node_to_ccid[kid]=comp_cc_id+str(ctr)+suffix
        else:
            aels = component.xpath("cc:a-element", namespaces=NS)
            d_c_e = self.sort_aelements(aels)
            for tipe in d_c_e:
                ctr=0
                for ael in d_c_e[tipe]:
                    ctr+=1
                    self.node_to_ccid[ael]=comp_cc_id+str(ctr)+tipe # No Suffix
                    print("Added " + self.node_to_ccid[ael])

        return self.node_to_ccid[ccel_el]
        
                
    # def register_abbrs(self):
    #     """
    #     Registers all the abberviations used in this document
    #     both in the user-provided XML and the boilerplate
    #     with the automatic cross-referencer.
    #     """
        
    #     for term in self.get_all_abbr_els():
    #         abbr = term.attrib["abbr"]
    #         self.register_keyterm(abbr, "long_abbr_"+abbr)
    #         self.abbrs[abbr]=term.attrib["full"]
    #         if "plural" in term.attrib:
    #             plural=term.attrib["plural"]
    #             self.abbrs[plural]=term.attrib["full"]
    #             self.register_keyterm(plural, "long_abbr_"+abbr)

        
    def categorize_sfrs(self):
        """
        Initialization function that categorizes the XML document
        into the different sets: self.obj_sfrs, self.opt_sfrs,
        self.impl_sfrs, self.sel_sfrs. (Man_sfrs are already set). 
        If it can't figure out which category (like if it's dependent on a base),
        it calls self.handle_unknown_depends, which should call the module-specific
        method.
        """
        
        for sfr in self.man_sfrs:
            self.maybe_register_sfr_with_fam(sfr)
        for sfr in self.rx("//cc:f-component[cc:objective]"):
            self.maybe_register_sfr_with_fam(sfr)
            self.obj_sfrs[sfr]=1
        for sfr in self.rx("//cc:f-component[cc:optional and not(cc:depends)]"):
            self.maybe_register_sfr_with_fam(sfr)
            self.opt_sfrs[sfr]=1
        dep_sfrs = self.rx("//cc:f-component[cc:depends]")
        for sfr in dep_sfrs:
            should_register = True
            # We're just looking at the first one
            depends=sfr.find("cc:depends[1]", NS)
            if depends.find("cc:external-doc", NS) is not None:
                self.sel_sfrs[sfr]=1
            else:
                for attr in depends.attrib:
                    el = self.rf("//*[@id=\""+depends.attrib[attr]+"\"]")
                    if el is None:
                        raise Exception("Cannot find dependee for " + depends.attrib[attr])
                    elif el.tag == CC+"selectable":
                        self.sel_sfrs[sfr]=1
                    elif el.tag == CC+"feature":
                        self.impl_sfrs[sfr]=1
                    else:
                        # This really only handles modified.
                        self.handle_unknown_depends(sfr, depends.attrib[attr])
                        should_register=False
                    break
            if should_register:
                self.maybe_register_sfr_with_fam(sfr)
        
        
    def make_edocs(self, workdir):
        """
        Makes XML representations of packages and bases (external documents).
        
        :param workdir: The directory where the documents should
        be loacated.
        :returns A dictionary where IDs are mapped to an XML representation
        of the external document associated with them.
        """
        
        ret = {}
        # for external in self.root.findall(".//cc:*[cc:git]", NS):
        for external in self.rfa("//cc:include-pkg")+self.rfa("//cc:base-pp"):
            ret[external.attrib["id"]] = edoc.Edoc(external, workdir)
        return ret
    
    def handle_unknown_depends(self, sfr, attr):
        """
        Raises an exception (meant to be overwritten by the module class so that 
        it can find bases)

        :param  sfr: Doesn't matter
        :param  attr: Doesn't matter
        """
        
        raise Exception("Can't handle this dependent sfr:"+sfr.attrib["cc-id"])




            
    def to_sd(self):
        """
        Builds the "Supporting Document"
        
        :returns: The root node of the SD built.
        """
        print("Now building supporting document.")
        self.outline = [0]
        self.is_appendix = False
        body=HTM_E.body()
        ret=HTM_E.html(
            HTM_E.head(
                HTM_E.title("Supporting Document "+self.title()),
                HTM_E.style({"type":"text/css"}, css_content.fx_common_css()),
            ),body)
        self.meta_data(body)
        self.write_forward(body)
        body.append(HTM_E.h2("Contents"))
        self.toc = adopt(body, (HTM_E.div({"class":"toc","id":"toc"})))
        self.sd_intro(body)
        self.sd_sfrs(body)
        self.sd_sars(body)
        body.append(self.sec("Required Supplementary Information"))
        body.append(HTM_E.p("This Supporting Document has no required supplementary information beyond the ST, operational guidance, and testing."))
        self.end_section()
        self.start_appendixes()
        self.create_bibliography(body)
        return ret






        # sar_sec_els = self.rx(".//*[@title='Evaluation Activities for SARs']|.//sec:Evaluation_Activites_for_SARs")
        # if len(sar_sec_els)==0:
        #     wurds=
        #     out.append
            
        #     """The PP-Module does not define any SARs beyond those defined within the base NDcPP to which it must claim conformance. It is important to note that a TOE that is evaluated against the PP-Module is inherently evaluated against this Base-PP as well. The NDcPP includes a number of Evaluation Activities associated with both SFRs and SARs. Additionally, the PP-Module includes a number of SFR-based Evaluation Activities that similarly refine the SARs of the Base-PPs. The evaluation laboratory will evaluate the TOE against the Base-PP and supplement that evaluation with the necessary SFRs that are taken from the PP-Module."""

            
        # elif not is_empty(sar_sec_els[0]):
        #     raise Exception("Haven't implemented SD with SARs yet.")
            
    def sd_sfrs(self, out):
        """
        Builds the SFR section for a supporting document.

        :param out: The parent output node
        """
        
        out.append(self.sec({"id":"sfrs-"},"Evaluation Activities for SFRs"))
        out_p = adopt(out, HTM_E.p("""The EAs presented in this section capture the 
        actions the evaluator performs 
        to address technology specific aspects covering specific SARs (e.g. ASE_TSS.1, 
        ADV_FSP.1, AGD_OPE.1, and ATE_IND.1) – this is in addition to the CEM workunits 
        that are performed in Section """))
        self.make_xref("eas_for_sars-", out_p)
        add_text(out_p, ".")
        #    <a href="#sar_aas" class="dynref"></a>
        out.append(HTM_E.p("""Regarding design descriptions (designated 
        by the subsections labeled TSS, as 
        well as any required supplementary material that may be treated as proprietary), 
        the evaluator must ensure there is specific information that satisfies the EA. 
        For findings regarding the TSS section, the evaluator’s verdicts will be 
        associated with the CEM workunit ASE_TSS.1-1.
        Evaluator verdicts associated with the supplementary evidence will also be 
        associated with ASE_TSS.1-1, 
        since the requirement to provide such evidence is specified in ASE in the PP."""))
        out.append(HTM_E.p("""For ensuring the guidance documentation provides 
        sufficient information for 
        the administrators/users as it pertains to SFRs, the evaluator’s verdicts will 
        be associated with CEM workunits ADV_FSP.1-7, AGD_OPE.1-4, and AGD_OPE.1-5."""))
        out.append(HTM_E.p("""Finally, the subsection labeled Tests is where 
        the authors have determined 
        that testing of the product in the context of the associated SFR is necessary.
        While the evaluator is expected to develop tests, there may be instances where 
        it is more practical for the developer to construct tests, or where the 
        developer may have existing tests. 
        Therefore, it is acceptable for the evaluator to witness developer-generated 
        tests in lieu of executing the tests. 
        In this case, the evaluator must ensure the developer’s tests are executing both 
        in the manner declared by the developer and as mandated by the EA. 
        The CEM workunits that are associated with the EAs specified in this section 
        are: ATE_IND.1-3, ATE_IND.1-4, ATE_IND.1-5, ATE_IND.1-6, and ATE_IND.1-7."""))
        self.sd_handle_bases(out)
        none_mesg="The "+ self.doctype_short() + " does not define any mandatory SFRs."
        self.sd_handle_sfr_type("TOE SFR Evaluation Activities", self.man_sfrs, none_mesg, "man_sfrs", out)
        none_mesg="The "+ self.doctype_short() + " does not define any strictly optional SFRs."
        self.sd_handle_sfr_type("Evaluation Activities for Strictly Optional SFRS", self.opt_sfrs, none_mesg, "opt_sfrs", out)
        none_mesg="The "+ self.doctype_short() + " does not define any objective SFRs."
        self.sd_handle_sfr_type("Evaluation Activities for Objective SFRS", self.obj_sfrs, none_mesg, "obj_sfrs", out)
        none_mesg="The "+ self.doctype_short() + " does not define any implementation-based SFRs."
        self.sd_handle_sfr_type("Evaluation Activities for Implementation-based SFRS", self.impl_sfrs, none_mesg, "impl_sfrs", out)
        none_mesg="The "+ self.doctype_short() + " does not define any selection-based SFRs."
        self.sd_handle_sfr_type("Evaluation Activities for Selection-based SFRS", self.impl_sfrs, none_mesg, "sel_sfrs", out)
        self.end_section()


    def sd_handle_sfr_type(self, title, sfrs, none_mesg, sfr_type, out):
        """
        Adds specific SFR type sections (e.g. "Selection based", "Optional"
        
        :param  title: The heading name
        :param  sfrs: The list of SFRs
        :param  none_mesg: A message to display if there's none
        :param  sfr_type: The type of SFR
        :param  out: The output HTML node
        """

        out.append(self.sec(title))
        if len(sfrs) == 0:
            out.append(HTM_E.p(none_mesg))
        else:
            self.handle_sparse_sfrs(sfrs, out, sfr_type, True)
        self.end_section()
        

    def sd_handle_bases(self, out):
        """
        Does nothing (Meant to be overwritten by Module class).

        :param  out:
        """
        
        return
    
    def meta_data(self, parent):
        """
        Builds the clerical portion of the SD document.

        :param parent: The root of the output HTML node.
        """
        
        div = HTM_E.div(
            {"style":"text-align: center; margin-left: auto; margin-right: auto;"},
            HTM_E.h1({"class":"title","style":"page-break-before:auto;"},"Supporting Document",HTM_E.br(), "Mandatory Technical Document"),
            HTM_E.img({"src":"images/niaplogo.png","alt":"NIAP"}),
            HTM_E.hr({"width":"50%"}),
            HTM_E.noscript(HTM_E.h1({"style":"text-align:center; border-style: dashed; border-width: medium; border-color: red;"},"This page is best viewed with JavaScript enabled!")),HTM_E.br())
        add_text(div, self.title())
        div.append(HTM_E.br())
        version_date = edoc.derive_version_and_date(self.root)
        pp_util.append_text(div, "Version: "+version_date[0])
        div.append(HTM_E.br())
        pp_util.append_text(div, version_date[1])
        div.append(HTM_E.br())
        div.append(HTM_E.b(self.derive_author()))
        parent.append(div)


    def write_forward(self, out):
        """
        Writes the forward for an SD document.

        :param out: HTML node where the document part is written.
        """
        
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
        """
        Does nothing (Meant to be overwritten).

        :param  out: -
        """
        
        return

    def sd_intro(self, out):
        """
        Writes the intro for a Supporting Document.

        :param out: The HTML output node.
        """
        
        out.append(self.sec({"id":"introduction-","class":"indexable"},"Introduction"))
        out.append(self.sec({"id":"scope-","class":"indexable"},"Technology Area and Scope of Supporting Document"))
        out.append(HTM_E.p("The scope of the "+ self.title() + " is to describe the security functionality of "+
                           self.derive_plural() + " products in terms of [CC] and to define functional and assurance requirements for them."))
        self.write_base_intro(out)
        out.append(HTM_E.p("""Although Evaluation Activities are defined mainly for the evaluators to follow, 
    in general they also help developers to prepare for evaluation by identifying specific requirements for their TOE.
    The specific requirements in Evaluation Activities may in some cases clarify the meaning of Security
    Functional Requirements (SFR), and may identify particular requirements for the content of Security
    Targets (ST) (especially the TOE Summary Specification), user guidance documentation, and possibly
    supplementary information (e.g. for entropy analysis or cryptographic key management architecture)."""))
        self.end_section()
        out.append(self.sec({"id":"structure-"},"Structure of the Document"))

        out.append(HTM_E.p("""Evaluation Activities can be defined for both SFRs and Security Assurance Requirements (SAR),
        which are themselves defined in separate sections of the SD."""))

        out.append(HTM_E.p("""If any Evaluation Activity cannot be successfully completed in an evaluation, then
        the overall verdict for the evaluation is a 'fail'.
        In rare cases there may be acceptable reasons why an Evaluation Activity
        may be modified or deemed not applicable for a particular TOE, 
        but this must be approved by the Certification Body for the evaluation."""))

        out.append(HTM_E.p("""In general, if all Evaluation Activities (for both SFRs and SARs) are successfully
        completed in an evaluation then it would be expected that the overall verdict for 
        the evaluation is a ‘pass’.
        To reach a ‘fail’ verdict when the Evaluation Activities have been successfully 
        completed would require a specific justification from the evaluator as to why the 
        Evaluation Activities were not sufficient for that TOE.
        """))
        out.append(HTM_E.p("""Similarly, at the more granular level of assurance components, if the Evaluation 
        Activities for an assurance component and all of its related SFR Evaluation 
        Activities are successfully completed in an evaluation then it would be expected 
        that the verdict for the assurance component is a ‘pass’.
        To reach a ‘fail’ verdict for the assurance component when these Evaluation 
        Activities have been successfully completed would require a specific justification 
        from the evaluator as to why the Evaluation Activities were not sufficient for that TOE. 
        """))
      
        self.end_section()

        self.apply_templates(self.rfa("//cc:tech-terms"), out)
        
#     <x:apply-templates select="//cc:tech-terms">
#       <x:with-param name="num" select="1"/>
#     </x:apply-templates>
#   </x:template>
        self.end_section()
        
        
    #     <x:call-template name="foreward"/>
    #     <x:call-template name="toc"/>
    #     <x:call-template name="intro"/>
    #     <x:call-template name="sfrs"/>
    #     <x:apply-templates select="/cc:*" mode="sars"/>
    #     <x:call-template name="sup-info"/>
    #     <x:call-template name="references"/>
    #   </body>
    # </html>


    def fix_dynrefs(self , same_doc, other_doc, root=None,):
        """
        Fixes numbered xrefs in a doc

        :param doc: The document in question
        """
        if root==None:
            root = same_doc
        if auto_xref.has_class(root.attrib, "dynref"):
            xpath=".//*[@id='"+root.attrib["data-target"]+"']"
            if not find_fix(xpath, same_doc, root): 
                if find_fix(xpath, other_doc, root):
                    parent = root.xpath("ancestor::*[1]")[0]
                    parent.tag = "span"
                    
        for child in root:
            self.fix_dynrefs(same_doc, other_doc, child)
            
    def fix_numbered_xrefs(self, main, sd):
        """
        Fixes numbered xrefs in a doc

        :param doc: The document in question
        """
        self.fix_dynrefs(main, sd)
        self.fix_dynrefs(sd, main)
        pass


        # for broken_ref in self.broken_refs:
        #     self.fix_xref(doc, broken_ref[0], broken_ref[1], broken_ref[2])

    # def fix_xref(self, doc, refid, link, ref):
    #     """
    #     Fixes the content of an anchor that points to something else.

    #     :param  doc: Root node of the HTML document
    #     :param  refid: The ID that is the target of the link
    #     :param  link: The output link.
    #     :param  ref: The input XML node that created the xref.
    #     It can be None if it's programmatically generated.
    #     """
        
    #     link.attrib["href"]="#"+refid
    #     reffed = doc.find(".//*[@id='"+refid+"']")
    #     # It's possible that this item might
    #     # be in the companion document. Like the SD
    #     # is pointing back to the main document or
    #     # vice-versa.
    #     if reffed is None:
    #         print("Could not find dynamic reference: '" + refid+"'")
    #         return
    #     label_node = reffed.find("./*[@class='dynid_']")
    #     if label_node is None:
    #         text = pp_util.flatten(reffed)
    #     else:
    #         text = pp_util.flatten(label_node)
    #     pp_util.append_text(link,text)

    def to_html(self):
        main = self.to_main()
        sd = self.to_sd()

        self.fix_numbered_xrefs(main, sd)
        self.xreffer.add_discoverable_xrefs(main)
        convert_none_text_to_emptys(main)

        self.xreffer.add_discoverable_xrefs(sd)
        convert_none_text_to_emptys(sd)

        
        return main, sd
    
    def rf(self, findexp):
        """
        Performs a _find_ from the root node. 'cc' and 'sec' 
        should be used as namespace prefixes.
        
        :param findexp: A find expression string
        :returns The results from root.find
        """
        
        return self.root.find( "."+findexp, NS)
    
    def rfa(self, findexp):
        """
        Performs a _findall_ from the root node. 'cc' and 'sec' 
        should be used as namespace prefixes.
        
        :param findexp: A find expression string
        :returns The results from root.find
        """
        
        return self.root.findall( "."+findexp, NS)

    def rx(self, xpath):
        """
        Performs an _xpath_ from the root node. 'cc' and 'sec' 
        should be used as namespace prefixes.
        
        :param xpath: An xpath expression string
        :returns The results from root.xpath
        """
        
        return self.root.xpath(xpath , namespaces=NS)

    def maybe_register_sfr_with_fam(self, sfr):
        """
        Registers an SFR with a family for the purposes of Extended Component Definitions
        if the SFR in question has a "comp-lev" child and does not have a 'notnew' child.

        :param sfr: XML f-component element node of the sfr inquestion.
        """
        
        if sfr.find("cc:comp-lev",NS) is None:
            return
        if sfr.find("cc:notnew", NS) is not None:
            return
        fam = sfr.attrib["cc-id"].split(".")[0]
        if fam not in self.fams_to_sfrs:
            self.fams_to_sfrs[fam]=[]
        self.fams_to_sfrs[fam].append(sfr)


    
    def sec(self, *args):
        """
        Creates a section in the numbered heading mode

        :param args: The arguments that will be passed to the 
        (h2) element constructor. It then is adjusted to reflect
        the correct level.

        :returns HTML element representing the parent node.
        """
        
        return sec_impl(self.outline, self.is_appendix, self.toc, HTM_E.h2(*args))


        
    def end_section(self):
        """
        Ends the current section. Should be paired with _sec_ function above.
        """
        
        if len(self.outline)==0:
            print("Popping from zero.")
        else:
            self.outline.pop()


  # <xsl:template match="cc:*[@id='obj_map']" mode="hook" name="obj-req-map">
    def objectives_to_requirements(self, par):
        """
        Writes out the "TOE Security Functional Requirements Rationale Section" (if
        an cc:SO has an 'cc:addressed-by' element.

        :param par: The output HTML node where the section good.
        """
        
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
        add_text(caption, "SFR Rationale")
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

        
        
    def to_main(self):
        """
        Builds an HTML skeleton for the main document.

        :returns The root element for the HTML tree.
        """
        
        self.outline = [0]
        self.is_appendix = False
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
        """
        Derives the title for main document.

        :returns A string representing the title
        """
        
        return edoc.derive_title(self.root, self.doctype())

    def handle_figure(self, el, par):
        """
        Writes out a figure section.

        :param el: The figure XML element
        :param par: The parent HTML output element.
        :returns
        """
        
        id=el.attrib["id"]
        div=adopt(par, HTM_E.div({"class":"figure","id":"div_fig_"+id}))
        attrs={"id":"fig_"+id, "src":el.attrib["entity"]}
        div.append(HTM_E.img(attrs))
        div.append(HTM_E.br())
        self.create_ctr("figure", id, div, "Figure ")
        add_text(div, el.attrib["title"])


    def get_text_or(self, xpath, default=""):
        """
        Gets the text at an xpath nodes (concatenated) or
        what's in the default.

        :param xpath XPath expression from the root
        :param default String to be returned if the XPath is empty
        :returns The text of all the nodes found (but not tails) or
               default if none can be found
        """
        els = self.rx(xpath)
        if len(els)==0:
            return default
        ret=""
        for el in els:
            ret+=el.text
        return ret
    
    def derive_author(self):
        """
        Derives the author of this document.

        :returns The text in the 'cc:author' node or "NIAP".
        """
        
        return self.get_text_or( "cc:author", "National Information Assurance Partnership")


    def make_logo(self):
        """
        Makes the logo section

        :returns the root of the subtree created
        """
        
        version_date = edoc.derive_version_and_date(self.root)
        return HTM_E.div({"class":"center"},
                         HTM_E.img({"src":"images/niaplogo.png","alt":"NIAP Logo"}),
                         HTM_E.br(),
                         "Version: "+version_date[0],
                         HTM_E.br(),
                         "     "+version_date[1],
                         HTM_E.br(),
                         HTM_E.b(self.derive_author()),
                         HTM_E.br())    



    def write_revision_history(self, body):
        """
        Writes the revision history section.

        :param body: The place to write the sectionl
        """
        
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


    def handle_comments(self, body):
        """
        Writes out the comments that were put in the document.

        :param body The place to write the comments
        """
        
        comments_els = self.rfa("//cc:comment")
        if not comments_els:
            return
        div=HTM_E.div({"id":"commentbox-"})
        ctr=0
        for comment_el in comment_els:
            id=self.doc.derive_id(comment_el)
            div.append(HTM_E.a({"href":"#"+id},"Comment: " + id))
            div.append(HTM_E.br())


        
    def fx_body_begin(self, body):
        """
        Writes out the beginning of the HTML document body

        :param body: The root of the HTML output tree to be written
        """
        
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

    def fel_cc_id(self, node):
        """
        Retrieves the cc-id of an f-element

        :param node: The f-element XML element in question
        :returns a string representing the cc-id
        """
        
        fcomp = node.xpath("ancestor::cc:f-component", namespaces=NS)[0]
        index = fcomp.findall("cc:f-element",NS).index(node)+1
        return self.fcomp_cc_id(fcomp, suffix="."+str(index))
        
        
    def fcomp_cc_id(self, node, suffix=""):
        """
        Retrieves the cc-id of an f-component or f-element.

        :param node: The f-component or f-element XML element in question
        :returns a string representing the cc-id element.
        """
        
        ret = node.attrib["cc-id"].upper() + suffix
        if "iteration" in node.attrib:
            ret += "/"+node.attrib["iteration"]
        return ret
        
                
    def handle_content(self, node, out,defcon=""):
        """
        Writes out the content provided by the XML element in _node_ to the 
        HTML element pointed to by _out_. If _node_ is empty it adds 
        the appends the string provided by _defcon_ to the text of _node_.

        
        :param node: Root XML element of the tree to be written out
        :param out: Root HTML element of the tree where the content will go
        :param defcon: Text that is written out if node is None (DEFault CONtent).
        :returns False if anything (besides _defcon_)was written out
        """
        
        if node is None:
            add_text(out, defcon)
            return False
        if node.text is None and len(node)==0:
            return False
        add_text(out, node.text)
        for child in node:
            self.apply_templates_single(child,out)
            add_text(out,child.tail)
        return True
            
    def handle_section(self, node, title, id, parent):
        """
        Writes out a section

        :param  node: XML Element representing the section
        :param  title: The name of the section
        :param  id: The ID of the section
        :param  parent: The HTML Element where the output goes
        """
        
        title_el = self.sec({"id":id},title)
        parent.append(title_el)
        self.handle_section_hook(title, node, parent)
        self.handle_content(node, parent)
        self.handle_post_section_hook(title, node, parent)
        self.end_section()

    def handle_post_section_hook(self, title, node, parent):
        """
        Does nothing (hook to be overwritten).

        :param  title: ignored
        :param  node: ignored
        :param  parent: ignored
        """
        
        pass
        
    def handle_section_hook(self, title, node, parent):
        """
        Checks whether ignoring boilerplates is on for this section.

        :param  title: Title of the section
        :param  node: XML node of the input section
        :param  parent: HTML node where the section is written
        """
        
        if "boilerplate" in node.attrib and node.attrib["boilerplate"]=="no":
            return 
        self.handle_section_hook_base(title, node, parent)

    def handle_conformance_claims(self, node, out):
        """
        Writes out a conformance claims section

        :param node: ignored
        :param out: HTML node where the section is written
        """
        
        dl=HTM_E.dl()
        out.append(dl)
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
            add_text(dd, "does not claim conformance to any packages")
        else:
            lagsep=""
            for pk in pks:
                ctr=ctr-1
                add_text(dd, lagsep)
                lagsep=","
                if ctr==2 :
                    lagsep="and"
                self.make_xref_edoc(pk, dd)
            add_text("conformant")
        add_text(dd,".")


        
    def handle_section_hook_base(self, title, node, out):
        """
        Looks for any sections with hooks and adds them
        
        :param  title: string representing the title
        :param  node: XML input node that represents the section
        :param  out: HTML output node where the content goes
        """
        
        if title=="Conformance Claims":
            self.handle_conformance_claims(node, out)
        elif title=="Implicity Satisfied Requirements":
            self.handle_implicitly_satisfied_requirements(out)
        elif title=="Security Objectives Rationale":
            self.handle_security_objectives_rationale(node, out)
        elif title=="Security Objectives for the Operational Environment":
            self.handle_security_objectives_operational_environment(out)
        elif title=="Assumptions":
            add_text(out, "These assumptions are made on the Operational Environment (OE) in order to be able to ensure that the security functionality specified in the "+self.doctype_short()+" can be provided by the TOE. If the TOE is placed in an OE that does not meet these assumptions, the TOE may no longer be able to provide all of its security functionality.")
        elif title=="Validation Guidelines":
            self.handle_rules_appendix(out) 
    
    def get_all_dependencies(self, node):
        """
        Gets all the dependencies of a node.

        :param node: The element in question. Usually an f-component.
        :returns An array contain a list of [choices, selections, featuress, externals, bases] which the node depends on.
        """
        
        choices=set()
        selections=set()
        features=set()
        externals=set()
        bases=set()
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
                            choices.add(theid)
                        elif ided.tag==CC+"base-pp":
                            bases.add(theid)
                        elif ided.tag==CC+"selectable":
                            selections.add(theid)
                        elif ided.tag==CC+"feature":
                            features.add(theid)
                        else:
                            print("Failed to sort the dependee:\""+theid+"\".")
        return [choices, selections, features, externals, bases]

    
    def make_ecd_table(self, par, ecdsecs):
        """
        Writes out an extended components definition section and table.
        
        :param  par: HTML element where the section goes
        :param  ecdsecs: The sections in the ecd table.
        """
        
        par.append(self.sec({"id":"ext-comp-defs-bg-"},"Extended Components Table"))
        add_text(par,"All extended components specified in the "+self.doctype()+" are listed in this table:")
        par.append(HTM_E.br())
        # b_el = adopt(par, HTM_E.div({"class":"table_caption"}))
        table = adopt(par, HTM_E.table({"class":"sort_kids_"}))
        caption = adopt(table, HTM_E.caption())
        self.create_ctr("Table","t-ext-comp_map-", caption, "Table ")
        add_text(caption, "Extended Component Definitions")
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
        """
        Writes out the extended component definitions Appendix.

        :param par: The element where the definitions are added.
        """
        
        if self.rf("//cc:ext-comp-def") is None:
            return 
        par.append(self.sec({"id":"ext-comp-defs"},"Extended Component Definitions"))
        add_text(par, "This appendix contains the definitions for all extended requirements specified in the " + self.doctype()+".\n")

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
            add_text(span, "This "+self.doctype() +\
                          " defines the following extended components as part of the "+\
                          classid + " class originally defined by CC Part 2:" )

            for ecd in ecds:
                self.handle_ecd(ecd, span)
            self.end_section()
        self.end_section()
        self.end_section()
        
    def handle_ecd(self, famnode, out):
        """
        Writes out an extended component definition .

        :param  famnode: The ext-comp-def element
        :param  out: The HTML output node
        """
        
        famId = famnode.attrib["fam-id"]
        desc = famnode.find("cc:class-description",NS)
        self.handle_content(desc, out)
        out.append(self.sec({"id":"ecd-"+famId}, famId+" "+famnode.attrib["title"]))

        div = adopt(out, HTM_E.div())
        # div = adopt(out, HTM_E.div({"style":"margin-left: 1em;"}))
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
        """
        Writes out the ECD sections for an sfr.

        :param  sfr: The sfr in question
        :param  cc_id: The CC id of the sfr (convenience)
        :param  par: The HTML output node
        """
        
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
        """
        Instructs the indexer that appendices have started
        """
        
        self.outline[0]=-1
        self.is_appendix = True

    def implementation_based_section(self, id, out):
        """
        Writes out the Implementation-based section.

        :param  id: The ID of the section
        :param out: The HTML output node
        """
        
        attrs={"id":id}
        out.append(self.sec(attrs, "Implementation-based Requirements"))
        features=self.rfa("//cc:feature")
        if len(features)==0:
            add_text(out, "This "+self.doctype_short()+" does not define any Implementation-based SFRs.\n")
        for feature in features:
            out.append(self.sec(feature.attrib["title"]))
            self.handle_content(feature,out)
            f_id=feature.attrib["id"]
            sfrs = self.rx(".//cc:f-component[./cc:depends/@*='"+f_id+"']")
            self.handle_sparse_sfrs(sfrs, out, "impl_sfrs")
            self.end_section()
        self.end_section()

    def add_optional_appendix_explainer(self, par, opt_id, obj_id, imple_id):
        """
        Hook to add an optional appendix explainer
        (overwritten by pp_doc class)

        :param  par: Unused
        :param  opt_id: Unused
        :param  obj_id: Unused
        :param  imple_id: Unused
        """

        pass

    def handle_sfr_section(self, sfrs, none_msg, audittype, title, out, idval):
        """
        Writes out one of the main SFR sections

        :param  sfrs: The group of SFRs
        :param  none_msg: A message if there's no SFRs
        :param  audittype: The type of audit associated with these
        :param  title: The title of the section
        :param  out: HTML output node
        :param  idval: The prefix ID that should be added to subsections
                that contain SFRs to prevent collisions.
        :returns
        """
        
        if len(sfrs)==0:
            add_text(out, none_msg)
        else:
            if audittype is not None:
                self.create_audit_table_section(title, audittype, out)
            self.handle_sparse_sfrs(sfrs, out, idval)

    # QQQQ
    def sfr_appendix(self,title,sfrs,preamble,audittype,idval,par):
        """
        Writes out an SFR in appendix form

        :param  title: The title of the section
        :param  sfrs: The group of SFRs
        :param  preamble: Any explainer
        :param  audittype: The type of audit associated with these
        :param  par: HTML output node
        :param  idval: The prefix ID that should be added to subsections
                that contain SFRs to prevent collisions.
        :returns
        """
        
        # attrset=attrs(None,title.replace(" ","-")+"-")
        attrset={"id":idval}
        par.append(self.sec(attrset,title+" Requirements"))
        add_text(par, preamble)
        none_msg = "This "+self.doctype_short()+" does not define any "+title+" SFRs.\n"
        self.handle_sfr_section(sfrs, none_msg, audittype, title, par, idval)
        self.end_section()

    def handle_optional_requirements(self, par):
        """
        Creates an appendix section for optional requirements.

        :param par: HTML output node
        """
        
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
        """
        Creates an section which houses an audit table

        :param  title: The name of the type of requirements
        :param  audittable: The type of audittable table created
        :param  par: HTML output node
        """
        
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
        """
        Gets the explainer for the selection-based requirements.

        :returns explainer in string form
        """
        
        DT=self.doctype()
        return "As indicated in the introduction to this "+DT+\
            ", the baseline requirements (those that must be performed by the TOE or its "+\
            "underlying platform) are contained in the body of this "+DT+\
            ". There are additional requirements based on selections in the body of "+\
            "the "+DT+": if certain selections are made, then additional "+\
            "requirements below must be included."
        
    def handle_selection_based_requirements(self, par):
        """
        Creates an appendix for selection-based requirements

        :param  node: Unused
        :param  par: The HTML output node
        """
        
        words=self.sel_appendix_preamble()
        self.sfr_appendix("Selection-based", self.sel_sfrs, words,"sel-based","sel-based-", par)


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
    
    def handle_security_objectives_operational_environment(self, out):
        """
        Writes out content concerning security objectives for the operational environment

        :param out: The HTML output node.
        """
        
        soes=self.rfa("//cc:SOE")
        if len(soes)>0:
            add_text(out,generic_pp_doc.OE_PREAMBLE)
        else:
            add_text(out, "This "+self.doctype()+" does not define any objectives for the OE.")

        
    def create_ctr(self, ctrtype, id ,parent, prefix, sep=": ", child=None):
        """
        Writes out a counter.

        :param  ctrtype: The type of counter
        :param  id : The ID assocaited with this counter
        :param parent: The HTML output node
        :param  prefix: A prefix for this node
        :param  sep=": ": The separate between prefix
        :param  child=None: Any other input content to be displayed
        """
        
        print("Creating counter for: " + id)
        ctrcount = str(self.get_next_counter(ctrtype))
        span = HTM_E.span({"class":"ctr",
                           "data-counter-type":"ct-"+ctrtype,
                           "id":id}, prefix,
                          HTM_E.span({"class":"counter"},ctrcount)
                          )
        parent.append(span)
        add_text(span, sep)
        self.handle_content(child, span)
        
    def handle_conformance_statement(self, out):
        """
        Writes out the conformance statement

        :param out: The HTML output node.
        """
        
        node.append(HTM_E.dd("An ST must claim exact conformance to this "+self.doctype()+", as defined in the CC "+
                        "and CEM addenda for Exact Conformance, Selection-based SFRs, and Optional SFRs (dated May 2017)."))
        

        
    def create_bibliography(self, out):
        """
        Writes out a bibliography.

        :param out: The HTML output node
        """
        
        out.append(self.sec({"id":"appendix-bibliography"},"Bibliography"))
        table = adopt(out, HTM_E.table())
        table.append(HTM_E.tr(HTM_E.th("Identifier"),HTM_E.th("Title")))
        entries = (self.rfa("//cc:bibliography/cc:entry") +
                   self.boilerplate.xpath("//*[@id='cc-docs']/cc:entry",namespaces=NS))
        entries.sort(key=lambda x: pp_util.flatten(x.find("cc:description", NS)))
        for entry in entries:
            keyterm= "["+entry.find("cc:tag", NS).text+"]"
            entry_id = self.derive_id(entry)            
            # self.register_keyterm(keyterm, entry_id)
            
            tr = adopt(table, HTM_E.tr())
            tr.append(HTM_E.td( HTM_E.span({"id":entry_id, "class":"definition"},keyterm)))

            td = adopt(tr, HTM_E.td())
            self.handle_content(entry.find("cc:description",NS), td)
        self.end_section()


            
    def create_acronym_listing(self, out):
        """
        Creates an acronym listing section.

        :param out: HTML output node
        """
        
        out.append(self.sec({"id":"acronyms"},"Acronyms"))
        table = adopt(out, HTM_E.table())
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

            attrs = {"class":"abbr definition", "id":"abbr_"+abbr}
            if "plural" in term_el.attrib:
                attrs["data-others"]=term_el.attrib["plural"]
            if "others" in term_el.attrib:
                attrs["data-others"]=term_el.attrib["others"]
            tr.append(HTM_E.td(HTM_E.span(attrs, abbr)))
            tr.append(HTM_E.td(HTM_E.span({"id":"long_abbr_"+abbr}, full)))
        self.end_section()
            
    def handle_security_objectives_rationale(self, node, out):
        """
        Writes out a section for the Security Objectives Rationale.

        :param node: Unused
        :param out: The HTML output element
        """
        
        add_text(out, """This section describes how the assumptions, threats, and organizational 
security policies map to the security objectives.""")
        table = adopt(out, HTM_E.table())
        caption = adopt(table, HTM_E.caption())
        self.create_ctr("Table","t-sec-obj-rat-", caption, "Table ")
        add_text(caption, "Security Objectives Rationale")
        tr = adopt(table, HTM_E.tr({"class":"header"}))
        tr.append(HTM_E.td("Threat, Assumption, or OSP"))
        tr.append(HTM_E.td("Security Objectives"))
        tr.append(HTM_E.td("Rationale"))
        objrefers=self.rx("//cc:threat/cc:objective-refer | //cc:OSP/cc:objective-refer | //cc:assumption/cc:objective-refer")
        firstcol=""
        for objrefer in objrefers:
            out = objrefer.find("..")
            pname = out.attrib["name"]
            attrs={}
            if pname != firstcol:
                tr = adopt(table, HTM_E.tr({"class":"major-row"}))
                firstcol=pname
                numkids = len(out.findall("cc:objective-refer", NS))
                pname_wrap = pp_util.make_wrappable(pname)
                from_el = out.find("cc:from", NS)
                if not from_el is None:
                    pname_wrap+=" (from "+from_el.attrib["base"]+")"
                tr.append(HTM_E.td({"rowspan":str(numkids)},pname_wrap))
            else:
                tr = adopt(table,HTM_E.tr())
            adopt(tr, HTM_E.td(pp_util.make_wrappable(objrefer.attrib["ref"])))
            td = adopt(tr,HTM_E.td())
            self.handle_content(objrefer.find("cc:rationale",NS), td)

        
    def handle_implicitly_satisfied_requirements(self, out):
        """
        Creates a section for implicitly satisfied requirements

        :param out: The HTML output node.
        """
        
        out.append(HTM_E.p("This appendix lists requirements that should be considered satisfied by products\n"+
                           "successfully evaluated against this "+self.doctype_short()+". These requirements are not featured\n"+
                           "explicitly as SFRs and should not be included in the ST. They are not included as \n"+
                           "standalone SFRs because it would increase the time, cost, and complexity of evaluation.\n"+
                           "This approach is permitted by",
                           HTM_E.a({"href":"#bibCC"},"[CC]"),
                           "Part 1, 8.2 Dependencies between components."))
        out.append(HTM_E.p("This information benefits systems engineering activities which call for inclusion of particular "+
                           "security controls. Evaluation against the "+self.doctype_short()+" provides evidence that these controls are present "+
                           "and have been evaluated."))

    # Don't know if it makes sens for the cclaims to be in this with the others.
    # The definition class means that the text content of the
    # can be discovered by the cross-referencer and should
    # point to the 'id' attribute.
    def template_assumptions_cclaims_threats_OSPs_SOs_SOEs(self, node, out):
        """
        Creates a definition list for assumptions, claims, threats, OSPs, SOs, or SOEs.

        :param node: The parent node of the group.
        :param out: The HTML output node
        """
        
        defs = node.findall("cc:*[cc:description]", NS)
        if len(defs)>0:
            dl = adopt(out, HTM_E.dl())
            for defined in defs:
                classtype=pp_util.localtag(defined.tag)
                name= defined.attrib["name"]
                dl.append(HTM_E.dt({"class":classtype+" definition","id":name}, name))
                dd = adopt(dl, HTM_E.dd())
                self.apply_templates(defined.findall("./cc:description",NS), dd)
                self.apply_templates(defined.findall("./cc:appnote",NS), dd)
        else:
            add_text(out, "This document does not define any additional " + pp_util.localtag(node.tag))
            
        
    def template_xref(self, node, out):
        """
        Writes out a cross reference.

        :returns
        :param  node:
        :param  out:
        """
        
        attrs = {}
        if "to" in node.attrib:
            to=node.attrib["to"]
        else:
            to=node.attrib["g"]
            if to=='CC':
                out.append(HTM_E.a({'href':'#bibCC'},"[CC]"))
                return
        if "format" in node.attrib:
            attrs["data-post"]=node.attrib["format"]
        refs = self.rx(".//cc:*[@id='"+to+"']|.//sec:*[local-name()='"+to+"']")
        if len(refs)==0:
            pp_util.log("Failed to find a reference to "+to)
            out.append( HTM_E.a(attrs))
            return 
        elif len(refs)>1:
            pp_util.log("Found multipled targets for "+ to)
        self.make_xref(refs[0], out, node)

        
    def get_list_of(self, fulltag):
        """
        Gets a list of items in the document that have the tag.

        :param  fulltag: A fulltag, i.e. CC+"selectable"
        :returns A list of items in the document with that tag
        """
        
        if fulltag in self.globaltags:
            return self.globaltags[fulltag]
        nodes = self.root.findall(".//"+fulltag)
        self.globaltags[fulltag] = nodes
        return nodes


    
    def get_global_index(self, node):
        """
        Retrieves the global index of the tag. Like the 5th selectable

        :param: Node the node in question
        :returns An integer (starting from 1) for the global index of the node.
        """
        
        allof = self.get_list_of(node.tag)
        return allof.index(node)+1

    def derive_id(self, node):
        """
        Calculates the ID of a node.

        :param node: The node in question
        :returns String representing the ID of the node.
        """
        
        if node.attrib is not None and "id" in node.attrib:
            return node.attrib["id"]
        if node.tag.startswith("{https://niap-ccevs.org/cc/v1/section}"):
            return node.tag.split("}")[1]
        return pp_util.localtag(node.tag)+"_"+str(self.get_global_index(node))+"-"
    
        
    def get_section_title(self, node):
        """
        Gets a title of a sec:* or cc:title section.
 
        :param node: The node in question.
        :returns A string representing the title.
        """
        
        if "title" in node.attrib:
            return node.attrib["title"]
        return node.tag.split("}")[1].replace("_", " ")
    
    def template_oldsection(self, node, out):
        """
        Writes out a section that's in the form of cc:section.

        :param node: The cc:section element
        :param out: The HTML output section
        :returns
        """

        id = self.derive_id(node)
        return self.handle_section(node,node.attrib["title"],id ,out)
        
    def template_newsection(self, node, out):
        """
        Writes out a section that's in the form of sec:*

        :param node: The cc:section element
        :param out: The HTML output section
        :returns
        """
        
        id = pp_util.localtag(node.tag)
        title = pp_util.get_attr_or(node, "title", id.replace("_", " "))
        return self.handle_section(node, title, id, out)

    def make_term_table(self, term_els, out, ignores=""):
        """
        Writes out a term table

        :param term_els: The cc:term elements
        :param out: The HTML output node
        :param ignores: Comma delimited list of terms to ignore ( must be prefixed and suffixed with commas)
        """
        
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
            self.template_glossary_entry(termdic[term], out)
        
    def template_tech_terms(self, node, out):
        """
        Writes out the CC and tech terms sections.

        :param node: Link containing the terms.
        :param out: The output HTML node
        """
        
        divy = HTM_E.div({"class":"no-link"})
        out.append(divy)
        divy.append(self.sec({"id":"glossary"}, "Terms"))
        add_text(divy,"The following sections list Common Criteria and technology terms used in this document.")
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
        
    def template_glossary_entry(self, node, out):
        """
        Writes out an entry in the the glossary term

        :param node: Term element to be written out
        :param out: The HTML output node
        """
        
        full = node.attrib["full"]
        tr = HTM_E.tr()
        out.append(tr)
        id=full.replace(" ", "_")
        td = adopt(tr, HTM_E.td())
        div = adopt(td, HTM_E.div({"id":id}))
        add_text(div, full)
        if "abbr" in node.attrib:
            add_text(div, " ("+node.attrib["abbr"]+")")
        deftd = adopt(tr, HTM_E.td())
        self.handle_content(node, deftd)


      
    def template_html(self, node ,out):
        """
        Writes out an HTML element

        :param node: The HTML element to be written out
        :param out: The HTML graft point
        """

        depends = node.findall("cc:depends", NS)
        if len(depends)>0:
            out = adopt(out, HTM_E.div({"class":"dependent"}))
            self.depends_explainer(out, node)
        tag = pp_util.localtag(node.tag)
        html_el = ET.Element(tag, node.attrib)
        out.append(html_el)
        self.handle_content(node, html_el)

    def add_refs(self, ref_ids, out):
        """
        Adds references for HTML elements that have dependencies.

        :param ref_ids: A list of reference IDs
        :param out: The HTML output element
        """

        ul_out = adopt(out, HTM_E.ul())
        for ref_id in ref_ids:
            print("Ref_id is " + str(ref_id))
            ref = self.rf("//cc:*[@id='"+ref_id+"']")
            self.make_xref(ref, adopt(ul_out, HTM_E.li()))
        
    def depends_explainer(self,out, node,
                          words="The following content should be included if:"):
        """
        For HTML elements with dependents, it adds the appropriate explainer section
        
        :param out: The HTML output node
        :param node: The HTML element that has the dependencies.
        :param word: Words that should be issued as part of the explainer.
        """
        depends_ids = self.get_all_dependencies(node)
        choices=depends_ids[0]
        selections=depends_ids[1]
        features=depends_ids[2]
        externals=depends_ids[3]
        bases=depends_ids[4]
        add_text(out, words)
        if len(choices)>0:
            self.add_refs(choices, out);
            out.append(HTM_E.div("choices are made"))
        if len(externals)>0:
            self.add_refs(externals, out);
            out.append(HTM_E.div("selections are made in base"))
        if len(selections)>0:
            self.add_refs(selections, out);
            out.append(HTM_E.div("selections are made"))
        if len(features)>0:
            self.add_refs(features, out);
            out.append(HTM_E.div("features are implemented"))
        if len(bases)>0:
            baselist = ""
            for base in bases:
                basenode = self.rf("//cc:*[@id='"+base+"']")
                self.make_xref(basenode, out)
            out.append(HTM_E.div("is a base. "))            

            
    def apply_templates(self, nodelist, out):
        """ Applies the python 'templates' (like XSL) to a list of 
        nodes.
        
        :param nodelist: Elements to be written out
        :param out: The HTML output element
        """
        if nodelist is None:
            return
        for node in nodelist:
            self.apply_templates_single(node, out)
    
    def template_usecases(self, node, out):
        """
        Writes out the general, human-language defintion of the usecases.

        :param  node: The element defining the usecases
        :param  out: The output HTML element
        """
        dl=HTM_E.dl()
        out.append(dl)
        ctr = 1
        for usecase in node.findall("cc:usecase", NS):
            id = usecase.attrib["id"]
            dl.append(HTM_E.dt({"id":id},"[USE CASE "+str(ctr)+"] "+usecase.attrib["title"]))
            dd=HTM_E.dd()
            dl.append(dd)
            self.apply_templates(usecase.findall("./cc:description",NS), dd)
            config = node.find("./cc:config", NS)
            if config is not None:
                dd.append(HTM_E.p("For changes to included SFRs, selections, and assignments required for this use case, see",
                                  dynref("appendix-"+id, "section "), "."))
            ctr += 1

            
    def handle_felement(self, fel_el,  out):
        """
        Writes out an f-element

        :param
        :param
        :returns
        """
        formal_id = self.get_ccid_for_ccel(fel_el)
        print("Handling f-element: " + formal_id)
        div_fel=adopt(out, HTM_E.div({"class":"element"}))
        reqid=self.derive_id(fel_el)
        div_fel.append(
            HTM_E.a({"id":formal_id,\
                     "href":"#"+formal_id,\
                     "class":"felement definition"}, formal_id)
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
        """
        Writes out an f-component when they are mingled amongs the other nodes.

        :param node: The f-component element
        :param out: The output HTML element
        :returns
        """
        if node in self.sel_sfrs:
            add_text(out, "This is a selection-based component. Its inclusion depends upon selection from:")
            for dependsId in node.xpath("cc:depends/@*", namespaces=NS):
                fcomp = self.rx("//cc:f-element[.//cc:selectable//@id='"+dependsId+"']") 
                if len(fcomp)>0:
                    add_text(out, " " + self.fel_cc_id(fcomp[0]))
            if is_optional(node):
                add_text(out, "This component may also be optionally be included in the ST as if optional.")
        elif node in self.obj_sfrs:
            add_text(out,"This is an objective component.")
        elif node in self.opt_sfrs:
            add_text(out, "This is an optional component.")
        return None


    def get_fcomp_status_isolated(self, node, out):
        """
        Gets the words for the human language status box of an f-component when they are not
        intermingled (the release version).

        :param node: The f-component element
        :param out: The HTML output element
        :returns
        """
        if node in self.sel_sfrs:
            add_text(out, "The inclusion of this selection-based component depends upon selection in:")
            for dependsId in node.xpath("cc:depends/@*", namespaces=NS):
                fels = self.rx("//cc:f-element[.//cc:selectable//@id='"+dependsId+"']")
                if len(fels)==1:
                    add_text(out, " " + self.fel_cc_id(fels[0]))
                else:
                    print("WARNING: Failed to find exactly one element that contains a selectable with the id: "+dependsId)
            add_text(out, ".")
            if is_optional(node):
                add_text(out, "This component may also be optionally be included in the ST as if optional.")

                
    
    def get_fcomp_status(self, node, out):
        """
        Writes the contents for an f-component element in the status box.

        :param node: The f-component element in question
        :param out: The HTML output node
        """
        if self.are_sfrs_mingled:
            self.get_fcomp_status_mingled(node, out)
        else:
            self.get_fcomp_status_isolated(node, out)

    def add_rule_longref(self, rule, out_el, ruleindex=None):
        """
        Writes out a long reference to a rule

        :param  rule: The rule in question
        :param  out_el: The HTML output node
        :param  ruleindex: Optional, the index of the rule. Calculated if not given
        """
        out = adopt(out_el, HTM_E.div({"class":"ruleref"}))
        if ruleindex==None:
            ruleindex = self.get_rule_index(rule)
        attrs={"href":"#"+self.derive_id(rule), "class":"ruleref"}
        out.append(HTM_E.a(attrs,"Rule #"+ruleindex))
        desc = rule.find("cc:description", NS)
        if desc is not None:
            add_text(out, ": ")
            self.handle_content(desc, out)
        
    def add_rules(self, fel_el, out):
        """
        Writes out the rules that concern this f-element.

        :param fel_el: The element that defines this f-element in question
        :param out: The HTML output rule
        """
        ids=set()
        harvest_ids(ids, fel_el)
        ctr=0
        for rule in self.rfa("//cc:rule"):
            ctr+=1
            if does_rule_contain_id(rule, ids):
                self.add_rule_longref(rule, out, ruleindex=str(ctr))
                
    
    def handle_component(self, node, out):
        """
        Writes out a component (either a-component or f-component)

        :param node: The component in question
        :param out: The HTML output node.
        """
        formal = self.fcomp_cc_id(node)
        div = adopt(out, HTM_E.div({"class":"comp"}))
        div.append(
            HTM_E.h4(
                HTM_E.span({"id":formal, "class":"definition"}, formal),
                " "+node.attrib["name"]))
        status_el = HTM_E.div({"class":"statustag"})
        self.get_fcomp_status(node, status_el)
        if not is_empty(status_el):
            div.append(status_el)
        self.handle_content(node, out)
        if node.tag==CC+"f-component":
            for f_el in node.findall(".//cc:f-element", NS):
                self.handle_felement(f_el, div)
        else:
            self.handle_aelements(node.findall("cc:a-element",NS), out)
        self.handle_fcomp_activities(node, formal, out)

    def sd_handle_component(self, comp, out):
        """
        Writes out the component for a supporting document

        :param comp: Either an f-element or a-element element.
        :param out: The HTML output node
        """
        formal = self.fcomp_cc_id(comp)
        div = adopt(out, HTM_E.div({"class":"comp", "id":formal}))
        div.append(HTM_E.h4(formal + " "+ comp.attrib["name"]))
        self.write_fcomp_activities_out(comp, formal, out)

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
#     <xsl:if test="out::cc:or"><xsl:apply-templates mode="or_path" select=".."/><xsl:value-of select="count(preceding-sibling::cc:*)+1"/></xsl:if>
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
#     <xsl:if test="not(out::cc:or or preceding-sibling::cc:*[1][self::cc:or])">
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


        

    def handle_aelements(self, els, out):
        """
        Writes out a list of cc:a-element elements.

        :param  els: List of elements
        :param  out: HTML output node
        """
        agroups = self.sort_aelements(els)
        for title in "Developer action", "Content and presentation", "Evaluator action":
            tipe=title[0:1]
            if len(agroups[tipe])>0:
                out.append(HTM_E.h4(title+" elements:"))
                for el in agroups[tipe]:
                    self.handle_felement(el, out)

    def sort_aelements(self, els):
        """
        Sorts the a-elements into three bins: Developer, Content and Presentation, and Evaluator.
        It bases this on whether it has a 'type' attribute or, lacking that, whether the title starts 
        with 'The developer shall', 'The evaluator shall', or other.


        :param els: List of elements
        :returns A dictionary with keys 'D', 'C', and 'E' that have lists of 
        Developer, Content and Presentation, and Evaluator a-elements.
        """
        ret={"D":[], "C":[], "E":[]}
        for el in els:
            if self.add_based_on_attr(el, ret):
                continue
            title=el.find("cc:title",NS).text
            if title.startswith("The developer shall"):
                ret["D"].append(el)
            elif title.startswith("The evaluator shall"):
                ret["E"].append(el)
            else:
                ret["C"].append(el)
        return ret
            

            
    def add_based_on_attr(self, el, theset):
        """
        Adds an a-element to the appropriate dictionary based on if it
        has a 'type' attribute.

        :param el: The a-element element.
        :param theset: A dictionary contain the 'D', 'E', and 'C' bins.
        :returns True if it has a 'type' attribute, false otherwise
        """
        if "type" in el.attrib:
            theset[el.attrib["type"]].append(el)
            return True
        return False


    def make_aactivity_pane(self):
        """
        Writes out an activity pane.
        """
        return HTM_E.div(attrs("activity_pane hide"),
                                  HTM_E.div(attrs("activity_pane_header"),
                                            HTM_E.a({"onclick":"toggle(this);return false;","href":"#"},
                                                    HTM_E.span(attrs("activity_pane_label"),"Evaluation Activities"),
                                                    HTM_E.span(attrs("toggler"))
                                                    )
                                            )
                                  )

        
    def handle_fcomp_activities(self, fcomp, formal, out):
        """
        Writes out the f-component activities (plus the div wrapper)

        :param fcomp: The f-component to write out
        :param formal: The CCid of the f-component
        :param out: The HTML output element
        """
        div = self.make_aactivity_pane()
        div_out = adopt(div, HTM_E.div(attrs("activity_pane_body")))
        if self.write_fcomp_activities_out(fcomp, formal, div_out):
            out.append(div)
            
            
    def write_fcomp_activities_out(self,  fcomp, formal, out):
        """
        Writes out the f-component activities

        :param fcomp: The f-component to write out
        :param formal: The CCid of the f-component
        :param out: The HTML output element
        """
        comp_acts = fcomp.xpath(".//cc:aactivity[not(cc:elev)]", namespaces=NS)
        should_add=self.handle_grouped_activities(formal, comp_acts, out)
        for fel in fcomp.xpath(".//cc:*[cc:aactivity/cc:elev]", namespaces=NS):
            # out.append(HTM_E.div(attrs("element-activity-header"), ))
            fel_id = self.fel_cc_id(fel)
            self.handle_grouped_activities(fel_id, fel.findall("cc:aactivity[cc:elev]", NS), out, "element")
            should_add=True
        return should_add

            
    def handle_grouped_activities(self, formal, aacts, out, classprefix="fcomp"):
        """
        Handles the activities at the component classprefix. Gathering all the
        f-component aactivities from the various elements.

        :param  formal: String header
        :param  aacts: List of the aactivity elements
        :param  out: the HTML output element
        :param  classprefix: Prefix that goes in the class attribute 

        """
        if len(aacts)==0:
            return False
        general_div=adopt(out, HTM_E.div(HTM_E.div(attrs(classprefix+"-activity-header"),formal)))
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
        """
        Finds the first section of the input document with the title.

        :param title: A string of the title
        :returns A reference to the XML element with the title (or None if none is found)
        """
        sections = self.find_sections_with_title(title)
        if len(sections)==0:
            return None
        else:
            return sections[0]
    
    def find_sections_with_title(self, title):
        """
        Finds all sections of the input document with the title.
        
        :param title: A string of the title
        :returns A list of elements from the input document with that title
        """
        underscored_title = title.replace(" ", "_")
        xpath="//*[@title='"+title+"']|sec:"+underscored_title+"[not(@title)]"        
        return self.rx(xpath)

    
    def handle_sparse_sfrs(self, sfrs, out, sfr_category, is_sd=False):
        """
        Converts a group of SFRs to HTML equivalent. Putting section
        headers in and grouping the SFRs appropriately underthem.

        :param sfrs: An iterable group of f-component XML elements
        :param out: The XML output out
        :param sfr_category: A string reflecting the type of sfrs (e.g. optional, sel-based)
        :param is_sd: Boolean whether it's being called to write to a SD
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
                out.append(self.sec({"id":id}, title))
                if not is_sd:
                    self.handle_content(sec,out)
            if is_sd:
                self.sd_handle_component(sfr, out)
            else:
                self.handle_component(sfr, out)
        if len(titles)>0:
            self.end_section()
# WE HAVE TO CLOSE THESE SECTIONS            
        
    def apply_templates_single(self, node, out):
        """
        Converts node to HTML.
        
        :param  node: The node to convert to.
        :param  out: The HTML node to write to
        :returns False if the node is None or a comment. True otherwise.
        """
        if node is None or is_comment(node):
            return False
        self.apply_template_to_element(node, out)
        return True

    
    def apply_template_to_element(self, node, out):
        """
        Converts an element to HTML.
        
        :param  node: The node to convert to.
        :param  out: The HTML node to write to
        """
        tag = node.tag
        print("Applying: " + tag)
        if tag.startswith("{https://niap-ccevs.org/cc/v1/section}"):
            self.template_newsection(node, out)
        elif tag == CC+"section":
            self.template_oldsection(node, out)
        elif tag == CC+"appendix":
            self.template_oldsection(node, out)
        elif tag.startswith("{http://www.w3.org/1999/xhtml}"):
            self.template_html(node, out)
        elif tag == CC+"xref":
            self.template_xref(node, out)
        elif tag == CC+"tech-terms":
            self.template_tech_terms(node, out)
        elif tag==CC+"usecases":
            self.template_usecases(node, out)
        elif tag==CC+"assumptions"\
             or tag==CC+"cclaims"\
             or tag==CC+"threats"\
             or tag==CC+"OSPs"\
             or tag==CC+"SOs"\
             or tag==CC+"SOEs":
            self.template_assumptions_cclaims_threats_OSPs_SOs_SOEs(node, out)
        elif tag==CC+"sfrs":
            self.template_sfrs(out)
        elif tag in DONT_PROCESS:
            return
        elif tag in TRANSPARENT:
            self.handle_content(node, out)
        elif tag==CC+"management-function-set":
            self.template_management_function_set(node, out)
        elif tag==CC+"ctr":
            self.template_ctr(node, out)
        elif tag==CC+"no-link":
            span=adopt(out, HTM_E.span({"class":"no-link"}))
            self.handle_content(node, out, span)
        elif tag==CC+"manager":
            td = adopt(out, HTM_E.td())
            self.handle_content(node, td)
        elif tag==CC+"figure":
            self.handle_figure(node, out)
        elif tag==CC+"audit-table":
            self.template_audit_table(node, out)
        elif tag==CC+"selectables":
            self.template_selectables(node, out)
        elif tag==CC+"assignable":
            self.template_assignable(node, out)
        elif tag==CC+"int":
            self.template_int(node, out)
        elif tag==CC+"_":
            self.make_xref(self.shortcut, out)
        elif tag==CC+"refinement":
            span = adopt(out, HTM_E.span({"class":"refinement"}))
            self.handle_content(node, span)
        elif tag==CC+"testlist":
            self.handle_testlist(node, out)
        elif tag == CC+"consistency_rationale":
            print("Not doing a-compoents")
        elif tag == CC+"equation":
            self.handle_equation(node, out)
        elif tag == CC+"Objective" or tag == CC+"Evidence":
            localtag = pp_util.localtag(node.tag)
            obj_out = adopt(out, HTM_E.div({"class":"test_"+localtag}))
            obj_out.append(HTM_E.b(localtag+": "))
            self.handle_content(node, obj_out)
        else:
            raise Exception("Can't handle: " + pp_util.debug_node(node))

    def handle_equation(self, node, out):
        """
        Converts a cc:equation element to HTML.

        :param  node: The cc:equation element
        :param  out: The HTML node to write to
        """
        id=self.derive_id(node)
        eq_out = HTM_E.td("$$")
        self.handle_content(node, eq_out)
        add_text(eq_out, "$$")
        ctr_out = HTM_E.td("(")
        self.create_ctr("equation", id, ctr_out, "", sep="")
        add_text(ctr_out,")")
        out.append(HTM_E.table({"class":"equation_"},
            HTM_E.tr(eq_out, ctr_out)
            ))
        

    def get_test_title(self, testnode):
        """
        Gets the title of a cc:test element.

        :param testnode: The test element
        :returns A unique string for this test element.
        """
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
        self.derive_test_title_recur(aa_el, cc_id+"#")
        return self.test_titles[testnode]

    def derive_test_title_recur(self, node, prefix, stack=[0]):
        """
        Assigns titles to all test elements in a subtree.

        :param  node: The root element of the subtree.
        :param  prefix: The prefix to assign to all nodes in this subtree.
        :param  stack: An integer array that serves as a stack.
        """
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
        """
        Writes out a cc:testlist element to HTML

        :param  testlist: A cctestlist element
        :param  out: The HTML node to write to
        """
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
                add_text(li, "[conditional,aaaa]")
            add_text(li, ":")
            self.handle_content(test, li)

    def get_title_n_sfrs(self, thistable):
        """
        Gets a tuple that connects the type of table to the formal title name and
        group of SFRs related to that table.
        
        :param thistable: One of 'mandatory', 'optional', 'objective', 'feat-based',
        'sel-based'.
        :returns A tuple of nice name and list of SFRs
        :raises an Exception if thistable is not one of the aforementioned values.
        """
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
        
  
    def template_audit_table(self, node, out, thistable=None):
        """
        Creates an auditable section with table.
        :param  node: The audit-table element if there is one. None if there is not.
        :param  out: The HTML output node
        :param  thistable: The type of audit table. If it's None, the method attempts to get it from
        the _node_ parameter
        """
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
        out.append(div)

    # This assumes the group never changes
    def get_sfrs_with_audit_events(self, sfrs, table):
        """
        Creates a mapping from each of the SFRs given to the appropriate audit events.

        :param  sfrs: Group of SFRs in question.
        :param  table: The table we're looking for.
        :returns
        """
        if not table in self.group_audit_map:
            entry={}
            for sfr in sfrs:
                events = sfr.xpath(".//cc:audit-event[not(@table) or @table='"+table+"']", namespaces=NS)
                if len(events)>0:
                    entry[sfr]=events
            self.group_audit_map[table]=entry
        return self.group_audit_map[table]

            
    def make_audit_row_from_event(self, event, table):
        """
        Makes an audit event row in an audit event table.

        :param event: The cc:audit-event to be written out
        :param table: The HTML output table element
        """
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
        """
        Writes a cell in an audit table.

        :param  nodein: The node to write out
        :param  out: The HTML output node
        :param  decider=None: The node that is checked to decide whether this is optional
        :param  nowords="None": What to write out as the other selection if it's optional.
        """
        if decider==None:
            decider=nodein
        if is_optional(decider):
            out.append(HTM_E.b("[selection"))
            add_text(out, ": ")
            self.handle_content(nodein, out)
            add_text(out, ", "+nowords)
            out.append(HTM_E.b("]"))
        else:
            self.handle_content(nodein, out)
            
            
        # for fcomp in self.rx("//cc:f-component[cc:audit-event]|//cc:f-component[@id=//cc:audit-event[not(out::cc:external-doc)]/@affects]"):
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

  #       <xsl:variable name="listy"><xsl:for-each select="//cc:audit-event[@table=$thistable and out::cc:external-doc/@ref=current()/@id]/@ref-cc-id"><xsl:value-of select="."/>,</xsl:for-each>
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
        """
        Gets the prefix for a counter elment.
        :param el: The counter element

        :returns The string prefix.
        """
        if "pre" in el.attrib:
            return el.attrib["pre"]
        if el.tag == CC+"figure":
            return "Figure "
        return pp_util.get_attr_or(el, "ctr-type", default="Table ")
    
    def template_ctr(self, node, out):
        """
        Writes counter input elements to HTML

        :param node: The cc:ctr element
        :param  out: The HTML node to write to
        """
        ctrtype = node.attrib["ctr-type"]
        prefix=ctrtype+" "
        if "pre" in node.attrib:
            prefix=node.attrib["pre"]
        id = self.derive_id(node)
        self.create_ctr(ctrtype, id, out, prefix, child=node)

        # count = str(self.get_next_counter(ctrtype))
        # span = adopt(par, HTM_E.span({"class":"ctr","data-counter-type":"ct-"+ctrtype,
        #                               "id":id}, ))
        # add_text(span,self.get_pre(node))
        # span.append(HTM_E.span({"class":"counter"}, id))
        # self.handle_content(node, span)

        
    def template_int(self, node):
        """
        Gets the text for an cc:int element.

        :param node: The cc:int element
        :returns The helpful text for an assignment (or none if hide is yes).
        """
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

    def template_assignable(self, node, out):
        """
        Converts a cc:assignable to HTML

        :param node: The cc:assignable element
        :param out: The HTML output node
        """
        id=self.derive_id(node)
        add_text(out,"[")
        out.append(HTM_E.b("assignment"))
        add_text(out,": ")
        span=adopt(out, HTM_E.span({"class":"assignable-content","id":id}))
        self.handle_content(node, span)
        add_text(out,"]")

    # def template_appendix(self, node, out):
    #     id=self.derive_id(node)
    #     title=node.attrib["title"]
    #     out.append(HTM_E.h1({"id":id},title))
    #     if "boilerplate" in node.attrib and node.attrib["boilerplate"]=="no":
    #         return
    #     self.handle_section_hook_base(title, node, out)
    #     self.handle_content(node, out)

    def template_selectables(self, node, out):
        """
        Converts a selectables element to HTML

        :param  node: The cc:selectables element
        :param  out: The HTML node to write to
        """
        if not is_in_choice(node):
            add_text(out,"[")
            out.append(HTM_E.b("selection"))
            if node.find("cc:onlyone", NS) is not None:
                out.append(HTM_E.b(", choose one of"))
            add_text(out, ": ")
            
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
            add_text(out,lagsep)
            lagsep=sep
                
            span = adopt(out,HTM_E.span({"class":"selectable-content"+extraclass, "id":id}))
            self.handle_content(selectable, span)
        if not is_in_choice(node):
            add_text(out,"]")
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
        
            
    def template_management_function_set(self, node, out):
        """
        converts a cc:management_function_set element to HTML
        
        :param  node: The cc:management_function_set element
        :param  out: The HTML node to write to
        """
        
        table = adopt(out, HTM_E.table({"class":"mfs","style":"width: 100%;"}))
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


    def make_mf_val(self, tag, node, out):
        """
        Populates a management function cell.

        :param  tag: An 'O', 'M', or 'NA' any other value will cause
        the node itself to be processed.
        :param  node: If tag isn't an O,M, or NA, it is converted 
        to the contents of the cell
        :param  out: The HTML node to write to
        """
        attrs = {"class":"tooltiptext"}
        if tag == "O":
            out.append(HTM_E.div("O",HTM_E.span(attrs,"Optional")))
        elif tag =="M":
            out.append(HTM_E.div("M",HTM_E.span(attrs,"Mandatory")))
        elif tag == "NA":
            out.append(HTM_E.div("-",HTM_E.span(attrs,"N/A")))
        else:
            self.handle_content(node, out)


    def make_mf_row(self, mf, prefix, managers, defval, out):
        """
        Writes out a row in the managment function table.

        :param  mf: cc:management-function element
        :param  prefix: The string that is prepended the the title
        :param  managers: A set of cc:manager elements that hand this
        :param  defval: String representing the default value
        :param  out: The HTML output node
        """
        
        mf_num = str(self.get_global_index(mf))
        mf_id = self.derive_id(mf)
        tr = adopt(out, HTM_E.tr())
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
        """
        Sets the shortcut (the element referred to by '<_/>')
        
        :param node: The element to set to the shortcut
        """
        self.shortcut = node

        
    # def make_xref_mf(self, id, out):
    #     """
        
    #     :param id: The ID of the management fuction
    #     :param out: The output node
    #     :returns
    #     """

    #     out.append(HTM_E.a({"href":"#"+id,"class":"dynref"}))

    # def make_xref_generic(self, target, out, ref, deftext=""):
    #     """
    #     Creates a a generic

        
    #     :outam
    #     :outam
    #     :returns
    #     """
    #     a_el=adopt(out, HTM_E.a({"href":"#"+target.attrib["id"],"class":"dynref"}))
    #     if not self.handle_content(ref, a_el):
    #         add_text(a_el, deftext)

    # def make_xref_section(self, id, out):
    #     out.append(HTM_E.a({"href":"#"+id,"class":"dynref"},"section "))

    def make_xref_bibentry(self, node, out):
        """
        Writes out a cross-reference to an entry in the bibliography.

        :param node: The bibiography element that is being cross-referenced.
        :param out: The HTML output node.
        """
        txt = "["+node.find("./cc:tag", NS).text+"]"
        anchor="#"+node.attrib["id"]
        out.append(E.a(txt, href=anchor))

    def make_xref_feature(self, target, out, ref=None):
        """
        Writes out a cross-reference to an implementation-dependent thing.

        :param target: The element being cross-referenced.
        :param out: The HTML output node.
        :param ref: The element doing the cross-reference (if there is one)
        """
        refid = self.derive_id(target)
        a_out = adopt(out, HTM_E.a({"href":"#"+refid}, target.attrib["title"]))

        
    def make_xref_selectable(self, target, out, ref):
        """
        Writes out a cross-reference to a selectable.

        :param target: The element being cross-referenced.
        :param out: The HTML output node.
        :param ref: The element doing the cross-reference.
        """
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



            
    def make_xref_ctr(self, target, out, ref):
        prefix = get_attr_or(target, "prefix")
        prefix = get_attr_or(ref, "prefix", prefix)
        if prefix is None:
            prefix = get_attr_or(ref, "ctr-type", "")
        suffix = ""
        suffix = get_attr_or(target, "suffix", suffix)
        suffix = get_attr_or(ref, "suffix", suffix)

        out.append(dynref(target.attrib["id"],prefix=prefix, suffix=suffix))

        

    def make_xref(self, target, out, ref=None):
        """
        Writes a cross-reference out.

        :param target: The element being cross-referenced.
        :param out: The HTML output node.
        :param ref: The element doing the cross-reference (or None).
        """
        if not hasattr(target, "tag"):
            out.append(dynref(target))
        elif target.tag == CC+"entry":
            self.make_xref_bibentry(target, out)
        elif target.tag == CC+"base-pp" or target.tag == CC+"include-pkg":
            theid= target.attrib["id"]
            self.pkgs[theid].make_xref_edoc(out)
        elif target.tag == CC+"f-element":
            ccid=self.get_ccid_for_ccel(target)
            id=self.derive_id(target)
            out.append(HTM_E.a({"href":"#"+id}, ccid))
        elif target.tag == CC+"selectable":
            self.make_xref_selectable(target, out, ref)
        elif target.tag == CC+"feature":
            self.make_xref_feature(target, out, ref)
        elif target.tag == CC+"ctr":
            self.make_xref_ctr(target, out, ref)
        else:
            out.append(dynref(self.derive_id(target), ""))
            # self.broken_refs.add( (self.derive_id(target), , ref) )
        # if target.tag.startswith("{https://niap-ccevs.org/cc/v1/section}"):
        #     self.make_xref_section(pp_util.localtag(target.tag), out)
        # elif target.tag == CC+"section":
        #     self.make_xref_section(target.attrib["id"], out)
        # elif target.tag == CC+"management-function":
        #     self.make_xref_mf(self.derive_id(target), out)
        # elif target.tag == CC+"test":
        #     self.make_xref_generic(target, out, ref, "")
        # elif target.tag == CC+"figure":
        #     self.make_xref_generic(target, out, ref, "figure")
        # elif target.tag == CC+"ctr":
        #     self.make_xref_generic(target, out, ref, "")
        # elif target.tag == CC+"appendix":
        #     self.make_xref_generic(target, out, ref, "Appendix")
        # elif target.tag == CC+"equation":
        #     self.make_xref_generic(target, out, ref, "equation")
        # else:
        #     raise Exception("Cannot reference: " + target.tag + " " + target.text)

    
    # def is_base(self, attr):
    #     """
        
    #     """
    #     b_el = self.rf("//cc:base-pp[@id='"+attr+"']")
    #     if b_el is not None:
    #         raise Exception("Should not have a base")
    #     return False
        
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
        """
        Writes out an appendix for rules.

        :param out: The HTML output node.
        """
        
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
        """
        This is like the 'usecase' mode in XSL. It only applies 
        the templates to the tags recognized in the usecase structure.

        :param nodes: The usecase elements.
        :param out: The HTML output node.
        """
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
        """
        Writes out cc:and in usecases.
        
        :param and_el: An cc:and element
        :param out: The HTML output node.
        """
        for child in and_el:
            print("Anding :"+ child.tag)
            self.apply_use_case_templates(child, out)
            
            # <xsl:template match="cc:and" mode="use-case" name="use-case-and">
            #   <xsl:apply-templates mode="use-case"/>
            # </xsl:template>
            

    def or_use_case(self, or_el, out):
        """
        Writes out a cc:or element in usecases.
        
        :param or_el: An cc:or element
        :param out: The HTML output node.
        """
        table_attrs = {"class":"uc_table_or", "style":"border: 1px solid black"}
        table_out = adopt(out, HTM_E.table(table_attrs,
                                           HTM_E.tr(
                                               HTM_E.td({"class":"or_cell", "rowspan":len(or_el)}, "OR"),
                                               inv_cell()
                                           )
                                           ))



    def doc_use_case(self, doc_el, out):
        """
        Writes out a cc:doc element in usecases.
        
        :param doc_el: An cc:doc element
        :param out: The HTML output node.
        """
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
        add_text(out, " include ")
        for sub in doc_el:
            target_edoc.make_xref_sub(sub.text, out)
        add_text(out, " in the ST. ")
            



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
        """
        Writes out a cc:refid element in usecases.
        
        :param refid_el: A cc:refid element
        :param out: The HTML output node.
        """
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
            add_text(out_div, " module in the ST ")
        elif target.tag == CC+"selectable":
            out_div = adopt(out,HTM_E.div({"class":"uc selectable"},start+"nclude "))
            self.make_xref(target, out_div)
            print("HANDLING ANCESTORS")
            add_text(out_div, " selectable in the ST ")
        elif target.tag == CC+"f-component":
            out_div = adopt(out,HTM_E.div({"class":"uc fcomp"},start+"nclude "))
            self.make_xref(target, out_div)
            add_text(out_div, " in the ST ")
        elif target.tag == CC+"management-function":
            print("HANDLING ANCESTORS")
            out_div = adopt(out,HTM_E.div({"class":"uc mf"},start+"nclude "))
            self.make_xref(target, out_div)
            add_text(out_div, " in the ST ")
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
        """
        Writes out a cc:then (and its cc:if element) element in usecases.
        
        :param refid_el: A cc:refid element
        :param out: The HTML output node.
        """
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

