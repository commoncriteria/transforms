#!/usr/bin/env python3
""" 
Module that converts PP xml documents to an HTML worksheet
"""

import base64
from io import StringIO 
import re
import sys
import xml.dom.minidom
from xml.dom import minidom
from xml.sax.saxutils import escape
PPNS='https://niap-ccevs.org/cc/v1'
HTMNS="http://www.w3.org/1999/xhtml"

def warn(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def getPpEls(parent, name):
    return parent.getElementsByTagNameNS(PPNS, name)

class State:
    """Keeps track of certain values for a PP """
    def __init__(self):
        """ Initializes State"""
        # Maps selection IDs to Requirements
        # If the selection is made, then the requirement is included
        self.selMap={}
        # Maps component IDs to sections
        self.compMap={}
        # Current index for the selectables
        self.selectables_index=0
        # Map from management function table values to HTML
        self.man_fun_map={}
        # Value for mandatory requirement
        self.man_fun_map['M']="X"
        # Value of N/A requirement
        self.man_fun_map['-']="-"
        # Value for Optional requirement
        self.man_fun_map['O']="<select onchange='update();' class='val'><option value='O'>O</option><option value='X'>X</option></select>"


    def handle_management_function_set(self, elem):
        ret = "<table class='mfun-table'>\n"
        defaultVal = elem.getAttribute("default")
        if defaultVal == "":
            defaultVal="O"

            
        ret+= "<tr><th>Management Function</th>"
        for col in getPpEls(elem, 'manager'):
            ret += "<th>"
            ret += self.handle_node(col, True);
            ret += "</th>"
        ret+= "</tr>\n"

        # Step through the rows
        for row in getPpEls(elem, 'management-function'):
            val={}
            # Build a dictionary where the key is 'ref' and
            # it maps to 'M', 'O', or '-'.
            for man in getPpEls(row, 'M'):
                val[man.getAttribute('ref')]='M'
            for opt in getPpEls(row, 'O'):
                val[man.getAttribute('ref')]='O'
            for das in getPpEls(row, '_'):
                val[man.getAttribute('ref')]='-'
            # Now we convert this to the expected columns
            ret += "<tr>\n"
            # First column is the management function text
            ret += "<td>"+self.handle_parent( getPpEls(row, 'text')[0], True) + "</td>"
            # And step through every other column
            for col in getPpEls(elem, 'manager'):
                ret += "<td>"
                colId = col.getAttribute("id");
                if colId in val:
                    ret += self.man_fun_map[ val[colId] ]
                else:
                    ret += self.man_fun_map[ defaultVal ]
                ret += "</td>"
            ret += "</tr>\n"
        ret += "</table>\n"
        return ret

    def handle_selectables(self, node):
        """Handles selectables elements"""
        sels=[]
        contentCtr=0
        ret="<span class='selectables"
        if node.getAttribute("exclusive")=="yes":
            ret+=" onlyone"
        ret+="' data-rindex='"+ str(self.selectables_index) +"'>"

        self.selectables_index+=1
        rindex=0
        for child in node.childNodes: # Hopefully only selectable
            if child.nodeType == xml.dom.Node.ELEMENT_NODE and child.localName == "selectable":
                contents = self.handle_node(child,True)
                contentCtr+=len(contents)
                chk = "<input type='checkbox'"
                onChange=""
                classes=""
                if child.getAttribute("exclusive") == "yes":
                    onChange+="chooseMe(this);"
                id=child.getAttribute("id")
                if id!="" and id in self.selMap:
                    onChange+="updateDependency(this,"
                    delim="["
                    for sel in self.selMap[id]:
                        classes+=" "+sel+"_m"
                        onChange+=delim+"\""+sel+"\""
                        delim=","
                    onChange+="]);"
                chk+= " onchange='update(); "+onChange+"'";
                chk+= " data-rindex='"+str(rindex)+"'"
                chk +=" class='val selbox"+classes+"'"
                chk +="></input><span>"+ contents+"</span>\n";
                sels.append(chk)
                rindex+=1
        # If the text is short, put it on one line
        if contentCtr < 50:
            for sel in sels:
                ret+= sel
        # Else convert them to bullets
        else:
            ret+="<ul>\n"
            for sel in sels:
                ret+= "<li>"+sel+"</li>\n"
            ret+="</ul>\n"
        return ret+"</span>"

    def handle_cc_node(self, node, show_text):
        if node.localName == "selectables":
            return self.handle_selectables(node)

        elif node.localName == "refinement":
            ret = "<span class='refinement'>"
            ret += self.handle_parent(node, True)
            ret += "</span>"
            return ret

        elif node.localName == "assignable":
            ret = "<textarea onchange='update();' class='assignment val' rows='1' placeholder='"
            ret += ' '.join(self.handle_parent(node, True).split())
            ret +="'></textarea>"
            return ret

        elif node.localName == "abbr" or node.localName == "linkref":
            if show_text:
                return node.getAttribute("linkend")

        elif node.localName == "management-function-set":
            ret=self.handle_management_function_set(node)
            return ret

        elif node.localName == "section":
            idAttr=node.getAttribute("id")
            ret =""
            if "SFRs" == idAttr or "SARs" == idAttr:
                ret+="<h2>"+node.getAttribute("title")+"</h2>\n"
            ret += self.handle_parent(node, False)
            return ret

        elif node.localName == "f-element" or node.localName == "a-element":
            # Requirements are handled in the title section
            return self.handle_node( getPpEls(node, 'title')[0], True);

        elif node.localName == "f-component" or node.localName == "a-component":
            id=node.getAttribute("id")
            ret = "<div onfocusin='handleEnter(this)' id='"+id+"'"
            # The only direct descendants are possible should be the children
            child=getPpEls(node, 'selection-depends')
            ret+=" class='component"

            if child.length > 0:
                ret+=" disabled"
            ret+="'>"
            #<a href='#"+id+"'>
            ret+="<span class='f-comp-status'></span><a href='#"+id+"' class='f-comp-title'>"+id.upper()+" &mdash; "+ node.getAttribute("name")+"</a><div class='reqgroup'>\n"
            ret+=self.handle_parent(node, True)
            ret+="</div></div>"
            return ret
            
        elif node.localName == "title":
            self.selectables_index=0
            req_id = node.parentNode.getAttribute('id')
            com_id = node.parentNode.parentNode.getAttribute('id')
            slaves = getPpEls(node.parentNode.parentNode, 'selection-depends')
            ret=""
            ret+="<div id='"+ req_id +"' class='requirement'>"
            ret+="<div class='f-el-title'>"+req_id.upper()+"</div>"
            ret+="<div class='words'>"
            ret+=self.handle_parent(node, True)
            ret+="</div>\n"
            ret+="</div>\n"
            return ret
        else:
            return self.handle_parent(node, show_text)
        return ""

            
    def handle_node(self, node, show_text):
        """Converts singular XML nodes to text."""
        if show_text and node.nodeType == xml.dom.Node.TEXT_NODE:
            return escape(node.data)
        elif node.nodeType == xml.dom.Node.ELEMENT_NODE:
            if node.namespaceURI == PPNS:
                return self.handle_cc_node(node, show_text)
            elif node.namespaceURI == HTMNS:
                if node.localName != "strike" and show_text:                     # Just ignore text that is striked out
                    # Just remove the HTML prefix and recur.
                    tag = re.sub(r'.*:', '', node.localName)
                    ret = "<"+tag
                    attrs = node.attributes
                    for aa in range(0,attrs.length) :
                        attr =attrs.item(aa)
                        ret+=" " + attr.name + "='" + escape(attr.value) +"'"
                    ret += ">"
                    ret += self.handle_parent(node, True)
                    ret += "</"+tag+">"
                    return ret;
        return ""

    def handle_parent(self, node, show_text):
        ret=""
        for child in node.childNodes:
            ret += self.handle_node(child, show_text)
        return ret

    def makeSelectionMap(self, root):
        """
        Makes a dictionary that maps the master requirement ID
        to an array of slave component IDs
        """
        for element in getPpEls(root, 'selection-depends'):
            # req=element.getAttribute("req");
            selIds=element.getAttribute("ids");
            slaveId=element.parentNode.getAttribute("id")
            for selId in selIds.split(','):
                reqs=[]
                if selId in self.selMap:
                    reqs =self.selMap[selId];
                reqs.append(slaveId)
                self.selMap[selId]=reqs


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: <pp-to-worksheet.py> <protection-profile>[:<output-file>]")
        sys.exit(0)

    # Split on colon
    out=sys.argv[1].split(':')
    infile=out[0]
    outfile=""
    if len(out) < 2:
        outfile=infile.split('.')[0]+"-worksheet.html"
    else:
        outfile=out[1]

    # Parse the PP
    root = minidom.parse(infile).documentElement

    state=State()

    state.makeSelectionMap(root);

    with open(infile, "rb") as in_handle:
        inb64 = base64.b64encode(in_handle.read()).decode('ascii')
        
    form =  "<html xmlns='http://www.w3.org/1999/xhtml'>\n"
    form += "   <head>\n"
    form += "      <meta charset='utf-8'></meta>\n"
    form += "      <title>"+root.getAttribute("name")+"</title>\n"
    form += """    <style type="text/css">
    body{
       margin-left: 8%;
       margin-right: 8%;
    }

    h1{
       border-bottom-style: double;
    }

    h2{
       border-bottom-style: ridge;
    }

    input[type=checkbox] + span {
       opacity: .6;
    }

    input[type=checkbox]:checked + span {
       opacity: 1;
    }

    .words{
       padding-left: 40px;
    }

    a {
       text-decoration: none;
       color: cornflowerblue;
    }    

    a:visited {
       color: cornflowerblue;
    }

    div.component{
       padding-top: 20px;
    }

    .f-comp-title{
       font-family: monospace;
       font-size: x-large;
    }

    .f-el-title{
       font-family: monospace;
       font-size: large;
       padding-left: 10px;
    }

    div{
       transition: sliding-vertically 5s ease-in-out;
    }

    .component.valid .f-comp-status::before,
    .valid .f-el-title::before{
       content: "\\2713";
       color: #0F0;
    }

    .component.invalid .f-comp-status::before,
    .requirement.invalid .f-el-title::before{
       content: "\\2715";
       color: #F00;
    }

    .disabled {
       opacity: .2;
       pointer-events: none;
    }

    .disabled .f-comp-status{
       display: none;
    }
    
    .warning{
       text-align:center;
       border-style: dashed;
       border-width: medium;
       border-color: red;
    }

    @media screen{
       .hide.component .f-el-title{
          display: none;
       } 
   
       .hide.component .invalid.f-el-title{
          display: none;
       } 
   
       .hide.component .words{
          display: none;
       } 
   
       .component .f-comp-title::after{
          display: inline-block;
          height: auto;
          content: url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8A\
AAAPCAYAAAA71pVKAAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAQOFAAEDhQGl\
VDz+AAAAB3RJTUUH4gIXFDM7fhmr1wAAAfRJREFUKM+dkk9I02EYxz/P+25uurWR\
tTkzI4NGl4jQgkq71K1DhnTQIDolRAQFQYSHTtGhU4e6eujQofBSFLOg0C4RUSjh\
FnmqTTdKpj/mfv/eX4cUpmRYn9vz8v3w8D7PA/AWGADCbI4QcAb4AnAF8IBJEdX+\
N0tEda40C4AHADviW1LFvpOX6+FwtAacVzqkGiWtwxo4F21OuPu7+yvxRNoDEhpY\
cpzavkQyc7D76FCk+vN7j7VU6RdR4xAsikjGGP9FKrN3sPfEpajv2i2zhckR4JUG\
UCr0erFavLkn2ytd2WPxcFOsZb74+SIQA0YPHBqIdB8Z6tChJv1m/N4P33OGAUsD\
BIFxPNcOkq07jyeSbbo1tTu2q6vHEqU7D/ddSKcz2ZQJjBSmx925b9NjwEMAafha\
eyQa/3Dq7O0243sCIEoRGAOA59nm5dM7OHVruzH+AkDjYEp23RrLT+U8Ub+fV0UR\
oVyaMfVa9fqquF5GKX3ja2FCuc6yWbMipYNP755UgEdr8o2FMf5ivVYdKRfzRkRW\
RfJTOc+2rWdAcUN5hdGP7x8viGgAXLvGbGFCKxW6tj74J3nOqVvP89M5V6kQ86UZ\
f7lWvWWMt7Sp41VKb21uSfqnB++6kWi8BLTzL4ioq7H4tgC4z3/QAZSBxEaBXygN\
v+jeFnAPAAAAAElFTkSuQmCC');
          max-width: 15px;
       }
   
       .hide.component .f-comp-title::after{
   	          content: url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8A\
AAAPCAYAAAA71pVKAAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAQOFAAEDhQGl\
VDz+AAAAB3RJTUUH4gIXFC4BR3keeQAAAfZJREFUKM+d0k1PE1EUBuB37h2nQ+30\
w5YObR0FhIppqBgWuDCaSBQjiQZNTIxLfoAkBHXh2vg7xID+ABPXBl3UdAMaN1CR\
j5ZijZ22DKW9d44LP1KMROvZnMU5z+KcvBzAAgADwCdV1RzXlYQ26tYhrYM6u/qX\
ATwCcKodrAOYv3z9IV28OuP6/NHPAGYZ45G/QQ5AAFjNbyzdTA2NewcGx7xeI5wu\
FZenQOQQuasHncN/9IJo1sn+unkpbqVFIJhgydQo13VjDKCJSnnLBJAHUPoTBoA3\
uzvlfiNgDhn+KMiVCB6xYCZSoaPHz5wrba/cbuztpBWFvQLI+R2DSGZqleKNuJX2\
cVVjAIExDo/uV7pPjGhSNntrleI9+n7Ox33Y549Wq/ZWTyh8rNcfjPlaZ4xzZvUM\
ezrNvnJ+fXFCiL2k2rpQq2wnAqH4tYjZFyZq/Y8CKZoim51z1nIZQ4jGNIC5fZhz\
7fHA4JVuj26AyIWiMDSbdTi1L/T29RO7ahdfKgqbInJLANCKZ6Kx5J24dVowztW6\
Y+8WNt91FNYXc4WN988BzAL4QOT+Aj/x8GFf+MHI+UlI2cBS9kVlLZfxSFdMS9GY\
V1WtKETDPShhz85emLRHx++TETBLAJ4qCov8c7ajsZMr/5PtBQB3AXSpqsbagd8A\
O+HMRUtPNsQAAAAASUVORK5CYII=');
       }
    }
    @media print{
       .warning-pane, BUTTON{
          display: none;
       }
       .hide{
          display: block;
       }
    }

    #main{
       margin-left:50px;
    }

           </style>
           <script type='text/javascript'>//<![CDATA[
"""
    form+= " const ORIG64='"+inb64+"""'
    const AMPERSAND=String.fromCharCode(38);
    const LT=String.fromCharCode(60);


    /// Holds the prefix for the settings we care about
    var prefix="";

    /// Dictionary to hold all the cookies
    var cookieJar=[];
    /**
     * This runs some sort of function on
     * all elements of a class.
     * @param classname Value of the class 
     * @param fun Function that is run on all elements. 
     *    For its 1st parameter, it takes the element. For the 2nd
     *    it's the number of the element.
     */
    function performActionOnClass(classname, fun){
        // Run through all the elements with possible
        // values
        var aa;
        var elems = document.getElementsByClassName(classname);
        for(aa=0; elems.length> aa; aa++){
           fun(elems[aa], aa);
        }
    }
    var prevCheckbox = false;
    function isPrevCheckbox(elem){
        var ret = prevCheckbox;
        prevCheckbox = false;
        return ret;
    }

    function isCheckbox(elem){
        return elem.getAttribute("type") == "checkbox";
    }

    function getId(index){
        return "v_" + index;
    } 

    function retrieveBase(name){
       var xhttp = new XMLHttpRequest();
       xhttp.onreadystatechange = function() {
          if (this.readyState == 4 && this.status == 200) {
	     pp_xml = xhttp.responseXML.documentElement
          }
       };
       xhttp.open("GET", name, true);
       xhttp.send();
    }

    function saveToCookieJar(elem, index){
        var id = prefix+":"+getId(index);
        if( isCheckbox(elem)){
            cookieJar[id]=elem.checked;
        }
        else if( elem.tagName == 'SELECT' ){
            cookieJar[id]=elem.selectedIndex;
        }
        else{
            if(elem.value != undefined){
               if( elem.value != "undefined" ) cookieJar[id]=elem.value;
            }
        }
    }

    // elem is a component element
    function handleEnter(elem){
       if (elem != null){
          elem.classList.remove('hide');
       }

       var compsIter, comps;
       comps = document.getElementsByClassName('component');
       for (compsIter=comps.length-1; compsIter>=0; compsIter--){
          if (comps[compsIter]==elem) continue;
          comps[compsIter].classList.add('hide');
       }
     }

    function retrieveFromCookieJar(elem, index){
        var id = prefix+":"+getId(index);
        if( isCheckbox(elem)){
            elem.checked= (cookieJar[id] == "true");
        }
        else if( elem.tagName == 'SELECT' ){
            if( id in cookieJar ){
               elem.selectedIndex = cookieJar[id];
            }
        }
        else{
            if( id in cookieJar) {
               if(cookieJar[id] != "undefined"){
                  elem.value= cookieJar[id];
               }
            }
        }
    }

    function init(){
        if( document.URL.startsWith("file:///") ){
           var warn = document.getElementById("url-warning");
           warn.style.display='block';
        }
        var url = new URL(document.URL);
        prefix=url.searchParams.get("prefix");
        if (prefix==null) prefix="";
        cookieJar = readAllCookies();
        performActionOnClass("val", retrieveFromCookieJar);
        validateRequirements();
        handleEnter(null);
    }
    function resolver(pre){
       if(pre=='cc') return 'https://niap-ccevs.org/cc/v1';
       else return "http://www.w3.org/1999/xhtml";
    }
    function readAllCookies() {
            ret=[];
            var ca = document.cookie.split(';');
            var aa,bb;
            for(aa=0;ca.length > aa ; aa++) {
                if (3>ca[aa].length){ continue;}
                var blah=ca[aa].split('=');
                if (2 != blah.length){
                   console.log("Malformed Cookie.");
                   continue;
                }
                key=blah[0].trim();
                val=decodeURIComponent(blah[1]);
                ret[key]=val;
            }
            return ret;
    }

    function saveAllCookies(cookies){
        var key;
        // run through the cookies
        for (key in cookies) {
           createCookie(key, cookies[key] );
        }
    }

    function createCookie(name,value) {
        var date = new Date();
        // 10 day timeout
        date.setTime(date.getTime()+(10*24*60*60*1000));
        var expires = "; expires="+date.toGMTString();
        document.cookie = name+"="+encodeURIComponent(value)+expires+"; path=/";

    }

    function eraseCookie(name) {
        createCookie(name,"",-1);
    }
    function fullReport(){
       var pp_xml = new DOMParser().parseFromString(atob(ORIG64), "text/xml");
       //- Fix up selections
       var xsels = pp_xml.evaluate("//cc:selectable", pp_xml, resolver, XPathResult.ANY_TYPE, null);
       var hsels = document.getElementsByClassName('selbox');
       var hsindex = 0;
       var choosens = new Set();
       while(true){
          var xmlsel = xsels.iterateNext();
          if( xmlsel == null ) break;
          if( hsindex == hsels.length) break;
          if( hsels[hsindex].checked ){
             // Can't mutate it while iterating
             // Keep a set
             //xmlsel.setAttribute("selected", "yes");
             choosens.add(xmlsel);
          }
          hsindex++;
       }
       for(let choosen of choosens){
          choosen.setAttribute("selected", "yes");
       }
       var ctr=0;

       //- Fix up assignments
       var xassigns = pp_xml.evaluate("//cc:assignable", pp_xml, resolver, XPathResult.ANY_TYPE, null)
       var assignments = [];
       while(true){
          var xassign = xassigns.iterateNext();
          if(xassign == null) break;
          assignments[ctr] = xassign;
          ctr++;
       }
       var hassigns = document.getElementsByClassName('assignment');
       for(ctr = 0; hassigns.length>ctr; ctr++){
          if(hassigns[ctr].value){
             assignments[ctr].setAttribute("val", hassigns[ctr].value);
          }
       }

       //- Fix up components
       var xcomps = pp_xml.evaluate("//cc:f-component|//cc:a-component", pp_xml, resolver, XPathResult.ANY_TYPE, null);
       var hcomps = document.getElementsByClassName('component');
       var disableds = new Set();
       for(ctr=0; hcomps.length>ctr; ctr++){
          var xcomp = xcomps.iterateNext();
          if(xcomp==null) break;
          if( hcomps[ctr].classList.contains('disabled') ){
             disableds.add(xcomp);
             console.log("Adding something");
          }
       }
       for(let disabled of disableds){
          disabled.setAttribute("disabled", "yes");
       }

       var serializer = new XMLSerializer();
       var xmlString = serializer.serializeToString(pp_xml);
       initiateDownload('FullReport.txt', xmlString, 'text/xml');
    }


    function generateReport(){
        var report = LT+"?xml version='1.0' encoding='utf-8'?>\\n"
        var aa;
        report += LT+"report xmlns='https://niap-ccevs.org/cc/pp/report/v1'>"
        var kids = document.getElementsByClassName('requirement');
        var isInvalid = false;
        for(aa=0; kids.length>aa; aa++){
            if( kids[aa].classList.contains("invalid") ){
               isInvalid = true;
            }
            report += "\\n"+LT+"req id='"+kids[aa].id+"'>";
            report +=getRequirement(kids[aa]);
            report += LT+"/req>\\n";
        }
        report += LT+"/report>";
        if( isInvalid ){
            alert("Warning: You are downloading an incomplete report.");
        }
        initiateDownload('Report.txt', report, 'text/xml');
    }

    function getRequirements(nodes){
      ret="";
      var bb=0;
      for(bb=0; bb!=nodes.length; bb++){
         ret+=getRequirement(nodes[bb]);
      }
      return ret;
    }

    function convertToXmlContent(val){
        var ret = val;
        ret = ret.replace(/\\x26/g, AMPERSAND+'amp;');
        ret = ret.replace(/\\x3c/g, AMPERSAND+'lt;');
        ret = ret.replace(/\\]\\]\\>/g, ']]'+AMPERSAND+'gt;');
        return ret;
    }

    function getRequirement(node){
        var ret = ""
        // If it's an element
        if(node.nodeType==1){
           if(isPrevCheckbox(node)){
               return "";
           }
           if(isCheckbox(node)){
               if(node.checked){
                  ret+=LT+"selectable index='"+node.getAttribute('data-rindex')+"'>"; 
                  // Like a fake recurrence call here
                  ret+=getRequirement(node.nextSibling);
                  ret+=LT+"/selectable>";
               }
               // Skip the next check.
               prevCheckbox=true;
           }
           else if(node.classList.contains("selectables")){
               ret+=LT+"selectables>"
               ret+=getRequirements(node.children);
               ret+=LT+"/selectables>"
           }
           else if(node.classList.contains("assignment")){
               var val = "";
               if(node.value){
                 val=node.value;
               }
               ret+=LT+"assignment>";
               ret+=convertToXmlContent(val);
               ret+=LT+"/assignment>\\n";
           }
           else if(node.classList.contains('mfun-table')){
               ret += LT+"management-function-table>"
               var rows = node.getElementsByTagName("tr");
               // Skip first row
               for(var row=1; rows.length>row; row++){
                  ret += LT+"management-function>";
                  var cols=rows[row].getElementsByTagName("td");
                  for( var col=1; cols.length>col; col++){
                     ret += LT+"val>"; 
                     if( cols[col].children.length == 0 ){
                        ret += cols[col].textContent;
                     }
                     else{
                        var si = cols[col].children[0].selectedIndex;
                        if(si!=-1){
                           ret += cols[col].children[0].children[si].textContent;
                        }
                     }
                     ret += LT+"/val>";
                  }
                  ret += LT+"/management-function>\\n";
               }
               ret += LT+"/management-function-table>";
           }
           else{
               ret+=getRequirements(node.children);
           }
        }
        // If it's text
        else if(node.nodeType==3){
           return node.textContent;
        }
        return ret;
    }

    function initiateDownload(filename, data, mimetype) {
        var blob = new Blob([data], {type: mimetype});
        if(window.navigator.msSaveOrOpenBlob) {
            window.navigator.msSaveBlob(blob, filename);
        }
        else{
            var elem = window.document.createElement('a');
            elem.href = window.URL.createObjectURL(blob);
            elem.download = filename;        
            document.body.appendChild(elem);
            elem.click();        
            document.body.removeChild(elem);
        }
    }

    function chooseMe(sel){
       var common = sel.parentNode;
       while( common.tagName != "SPAN" ){
          common = common.parentNode;
       }
       toggleFirstCheckboxExcept(common, sel);
    }

    var selbasedCtrs={}

    function areAnyMastersSelected(id){
       var masters = document.getElementsByClassName(id+"_m");
       for(bb=0; masters.length>bb; bb++){
          if (masters[bb].checked){
             return true;
          }
       }
       return false;
    }

    function modifyClass( el, clazz, isAdd ){
      if(el == null){
          console.log("Failed to find element with id: " + id);
          return false;
      }
      if(isAdd) el.classList.add(clazz);
      else      el.classList.remove(clazz);
      return true;
    }
    /* 
     * This design does not account for cascading dependent components .
     * There are none currently, so this limitation is acceptable.
     */
    function updateDependency(root, ids){
       var aa, bb;

       // Run through all 
       for(aa=0; ids.length>aa; aa++){     
          var enabled = areAnyMastersSelected(ids[aa]);
          // We might need to recur on these if the selection-based
          // requirement had a dependent selection-based requirement.
          modifyClass( document.getElementById(ids[aa]), "disabled", !enabled);
          var sn_s = document.getElementsByClassName(ids[aa]);
          for(bb=0; sn_s.length>bb; bb++){
             modifyClass(sn_s[bb], "disabled", !enabled)
          }
       }
    }

    var sched;
    function update(){
       if (sched != undefined){
         clearTimeout(sched);
       }
       sched = setTimeout(delayedUpdate, 1000);
    }

    function validateSelectables(sel){
       var child  = sel.firstElementChild;
       if( child.tagName == 'UL' ){
          child=child.firstElementChild;
       }
       var numChecked=0;
       // Now we either have a checkbox or an li
       while(child!=null){
          if(child.tagName == "LI"){
             if(child.firstElementChild.checked){
                numChecked++;
                if( !reqValidator(child) ){
                   return false;
                }
             }
          }
          else if(child.checked){
                numChecked++;
                if( !reqValidator(child) ){
                   return false;
                }
          }
          child = child.nextElementSibling;
       }
       if(numChecked==0) return false;
       if(numChecked==1) return true;
       return !sel.classList.contains("onlyone");
    }
    function setFocusOnComponent(comp){
       comp.getElementsByClassName('f-comp-title')[0].focus();
       return true;
    }
 
    function handleKey(event){
       if(! event.ctrlKey ) return;
       var key = event.which || event.keyCode;
       var curr = document.activeElement;
       var comps = document.getElementsByClassName('component');
       if (comps.length == 0) return;
       if (curr==document.body){
          curr=null;
       }
       var aa;
       if( key == 28){
          if (curr == null) curr =  comps[comps.length-1];
          for(aa=comps.length-1; aa >= 0; aa--){
             if(comps[aa] == curr) break;
             if(comps[aa].contains(curr)) break;
          }
          for(aa--; aa>=0; aa--){
             if(comps[aa].classList.contains('disabled')) continue;
             if(comps[aa].classList.contains('invalid')){
                return setFocusOnComponent(comps[aa]);
             }
          }
          return "";
       }
       else if( key == 30){
          if (curr == null) curr =  comps[0];
          for(aa=0; comps.length > aa; aa++){
             if(comps[aa] == curr) break;
             if(comps[aa].contains(curr)) break;
          }
          for(aa++; comps.length > aa; aa++){
             if(comps[aa].classList.contains('disabled')) continue;
             if(comps[aa].classList.contains('invalid')){
                return setFocusOnComponent(comps[aa]);
             }
          }
          return "";
       }
       else if (key==31){
          handleHelpRequest();
       }
    }
    function handleHelpRequest(){
    }


    function reqValidator(elem){
        var child = elem.firstElementChild;
        var ret;
        while(child != null){
           if( child.classList.contains("selectables")){
              ret = validateSelectables(child);
              if(!ret) return false;
           }
           else if( child.classList.contains("assignment")){
              if(! child.value) return false;
           }
           else{
              ret = reqValidator(child);
              if(!ret) return false;
           }
           child = child.nextElementSibling;
        }
        return true;
    }

    function validateRequirements(){
        var aa;
        var reqs = document.getElementsByClassName('requirement');
        for(aa=0; reqs.length > aa; aa++){
             if(reqValidator(reqs[aa])){
                 addRemoveClasses(reqs[aa],'valid','invalid');
             }
             else{
                 addRemoveClasses(reqs[aa],'invalid','valid');
             }
        }
        var components = document.getElementsByClassName('component');
        for(aa=0; components.length > aa; aa++){
           if(components[aa].getElementsByClassName('invalid').length == 0 ){
              addRemoveClasses(components[aa],'valid','invalid');
           }
           else{
              addRemoveClasses(components[aa],'invalid','valid');
           }
        }
    }

    function addRemoveClasses(elem, addClass, remClass){
        elem.classList.remove(remClass);
        elem.classList.add(addClass);
    }

    function delayedUpdate(){
       performActionOnClass("val", saveToCookieJar);
       saveAllCookies(cookieJar);

       validateRequirements();
       sched = undefined;
    }

    function toggleFirstCheckboxExcept(root, exc){
       if (root == exc) return;
       if ( isCheckbox(root)){
          if( exc.checked ){
             root.disabled=true;
             root.classList.add('disabled');
             root.nextSibling.classList.add('disabled');
             root.checked=false;
          }
          else{
             root.disabled=false;
             root.classList.remove('disabled');
             root.nextSibling.classList.remove('disabled');
          }
          return;
       }
       var children = root.children;
       var aa;
       for (aa=0; aa!=children.length; aa++){
          toggleFirstCheckboxExcept(children[aa], exc);
       }
    }
//]]>
           </script>
       </head>       <body onkeypress='handleKey(event); return true;' onload='init();'>
"""

    form +=  "      <h1>Worksheet for the " + root.getAttribute("name") + "</h1>\n"
    form +=  """
<div class='warning-pane'>
   <noscript><h2 class="warning">This page requires JavaScript.</h2></noscript>
    <h2 class="warning" id='url-warning' style="display: none;">
    Most browsers do not store cookies from local pages (i.e, 'file:///...').
    When you close this page, all data will most likely be lost.</h2>
</div>
    """

    form += state.handle_node(root, False)
    form += """
          <br/>
          <button type="button" onclick="generateReport()">Download XML </button>
          <button type="button" onclick="fullReport()">Download HTML</button>
       </body>
    </html>
"""
    with open(outfile, "w") as out:
        out.write(form)

