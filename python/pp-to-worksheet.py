#!/usr/bin/env python3
""" 
Module that converts PP xml documents to an HTML worksheet
"""

from io import StringIO 
import re
import sys
import xml.dom.minidom
from xml.dom import minidom
from xml.sax.saxutils import escape

PPNS='https://niap-ccevs.org/cc/v1'

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
        # index
        self.index=""
        # Map from management function table values to HTML
        self.man_fun_map={}
        self.man_fun_map['M']="X"
        self.man_fun_map['-']="-"
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
            if child.nodeType == xml.dom.Node.ELEMENT_NODE and child.tagName == "selectable":
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
                        classes=sel+"_m "
                        onChange+=delim+"\""+sel+"\""
                        delim=","
                    onChange+="]);"
                chk+= " onchange='update(); "+onChange+"'";
                chk+= " data-rindex='"+str(rindex)+"'"
                chk +=" class='val "+classes+"'"
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

    def handle_node(self, node, show_text):
        """Converts singular XML nodes to text."""
        if show_text and node.nodeType == xml.dom.Node.TEXT_NODE:
            return escape(node.data)
        elif node.nodeType == xml.dom.Node.ELEMENT_NODE:
#            print("Handling " + node.tagName);
            if node.tagName == "selectables":
                return self.handle_selectables(node)
            
            elif node.tagName == "refinement":
                ret = "<span class='refinement'>"
                ret += self.handle_parent(node, True)
                ret += "</span>"
                return ret
            
            elif node.tagName == "assignable":
                ret = "<textarea onchange='update();' class='assignment val' rows='1' placeholder='"
                ret += ' '.join(self.handle_parent(node, True).split())
                ret +="'></textarea>"
                return ret
            
            elif node.tagName == "abbr" or node.tagName == "linkref":
                if show_text:
                    return node.getAttribute("linkend")

            elif node.tagName == "management-function-set":
                ret=self.handle_management_function_set(node)
                return ret

            elif node.tagName == "section":
                idAttr=node.getAttribute("id").upper()
                ret =""
                if "SFRs" == idAttr or "SARs" == idAttr:
                    ret+="<h2>"+node.getAttribute("title")+"</h2>\n"
                ret += self.handle_parent(node, False)
                return ret

            elif node.tagName == "f-element" or node.tagName == "a-element":
                # Requirements are handled in the title section
                return self.handle_node( getPpEls(node, 'title')[0], True);
            
            elif node.tagName == "f-component" or node.tagName == "a-component":
                id=node.getAttribute("id").upper()

                # This builds the side index.
#                self.index+="<tr id='sn_"+id+"'><td colspan='2'><a href='#"+id+"'>"+id+"</a></td></tr>\n"

                ret = "<div id='"+id+"'"
                # The only direct descendants are possible should be the children
                child=getPpEls(node, 'selection-depends')
                if child.length > 0:
                    ret+=" class='disabled'"
                ret+=">"
                ret+="<h3><a href='#"+id+"'>"+id+" &mdash; "+ node.getAttribute("name")+"</a></h3>\n"
                ret+=self.handle_parent(node, True)
                ret+="</div>"
                return ret
            
            elif node.tagName == "title":
                self.selectables_index=0
                id = node.parentNode.getAttribute('id').upper();
                ret=""
                self.index+="<tr id='sn_"+id+"'><td><span class='stat'/></td><td><a href='#"+id+"'>"+id+"</a></td></tr>\n"
                ret+="<div id='"+ id +"' class='requirement'>"
                ret+="<div class='f-el-title'>"+id+"</div>"
                ret+="<div class='words'>"
                ret+=self.handle_parent(node, True)
                ret+="</div>\n"
                ret+="</div>\n"
                return ret
                
            elif node.tagName == "h:strike":
                # Just ignore text that is striked out
                pass

            # This assumes that prefixed nodes are part of the html namespace
            # and non prefix nodes are from the CC namespace.
            elif ":" in node.tagName:
                if show_text:
                    # Just remove the HTML prefix and recur.
                    tag = re.sub(r'.*:', '', node.tagName)
                    ret = "<"+tag
                    attrs = node.attributes
                    for aa in range(0,attrs.length) :
                        attr =attrs.item(aa)
                        ret+=" " + attr.name + "='" + escape(attr.value) +"'"
                    ret += ">"
                    ret += self.handle_parent(node, True)
                    ret += "</"+tag+">"
                    return ret;
            else:
                return self.handle_parent(node, show_text)
        return ""

    def handle_parent(self, node, show_text):
        ret=""
        for child in node.childNodes:
            ret +=self.handle_node(child, show_text)
        return ret

    def makeSelectionMap(self, root):
        """
        Makes a dictionary that maps the master requirement ID
        to an array of slave component IDs
        """
        for element in getPpEls(root, 'selection-depends'):
            # req=element.getAttribute("req");
            selIds=element.getAttribute("ids");
            slaveId=element.parentNode.getAttribute("id");
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

    form =  "<html xmlns='http://www.w3.org/1999/xhtml'>\n   <head>"
    form += "<meta charset='utf-8'></meta><title>"+root.getAttribute("name")+"</title>"
    form += """
           <style type="text/css">

    input[type=checkbox] + span {
       opacity: .6;
    }

    input[type=checkbox]:checked + span {
       opacity: 1;
    }

    .words{
       padding-left: 40px;
    }
    .f-el-title{
       font-family: monospace;
       font-size: x-large;
    }

    .sidenav .valid .stat::before,
    .valid .f-el-title::before{
       content: "\\2713";
       color: #0F0;
    }

    .sidenav .invalid .stat::before,
    .invalid .f-el-title::before{
       content: "\\2715";
       color: #F00;
    }
    
    .disabled {
       opacity: .2;
       pointer-events: none;
    }
    
    .warning{
       text-align:center;
       border-style: dashed;
       border-width: medium;
       border-color: red;
    }
    .sidenav {
        height: 100%;            /* 100% Full-height */
        position: fixed;         /* Stay in place */
        z-index: 1;              /* Stay on top */
        top: 0;                  /* Stay at the top */
        left: 0;
        width: 40px; 
        overflow-x: hidden;      /* Disable horizontal scroll */
        transition: 0.5s;        /* 0.5 second transition effect to slide in the sidenav */
        background-color: #FFF;  /* Black*/
        border-right: thin dotted #AAA;
     }

    .sidenav:hover{
        width: 200px;
    }

    .sidenav a{
        display: none;
        text-decoration: none;
    }


    .sidenav:hover a{
        display: inline;
    }
    #main{
       margin-left:50px;
    }

           </style>
           <Script Type='text/javascript'>

    const AMPERSAND=String.fromCharCode(38);
    const LT=String.fromCharCode(60);

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

    function saveToCookieJar(elem, index){
        var id = getId(index);
        if( isCheckbox(elem)){
            cookieJar[id]=elem.checked;
        }
        else if( elem.tagName == 'SELECT' ){
            cookieJar[id]=elem.selectedIndex;
        }
        else{
            if(elem.value != undefined && elem.value != "undefined" ){
               cookieJar[id]=elem.value;
            }
        }
    }

    function retrieveFromCookieJar(elem, index){
        var id = getId(index);
        if( isCheckbox(elem)){
            elem.checked= (cookieJar[id] == "true");
        }
        else if( elem.tagName == 'SELECT' ){
            if( id in cookieJar ){
               elem.selectedIndex = cookieJar[id];
            }
        }
        else{
            if( id in cookieJar && cookieJar[id] != "undefined"){
                elem.value= cookieJar[id];
            }
        }
    }

    function init(){
        if( document.URL.startsWith("file:///") ){
           var warn = document.getElementById("url-warning");
           warn.style.display='block';
        }
        cookieJar = readAllCookies();
        performActionOnClass("val", retrieveFromCookieJar);
        validateRequirements();
    }

    function readAllCookies() {
            ret=[];
            var ca = document.cookie.split(';');
            var aa,bb;
            for(aa=0;aa != ca.length; aa++) {
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
    //    var ca = document.cookie.split(';');
    //    var aa,bb;
    //    // Delete all existing cookies
    //    for(aa=0;aa != ca.length; aa++) {
    //       if (3>ca[aa].length){ continue;}
    //       var blah=ca[aa].split('=');
    //       if (2 != blah.length)  continue;
    //       eraseCookie( blah[0] );
    //    }
    //    // Save off everything in the cookie jar
        var key;
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

    function generateReport(){
        var report = LT+"?xml version='1.0' encoding='utf-8'?>\\n"
        var aa;
       
        report += LT+"report xmlns='https://niap-ccevs.org/cc/pp/report/v1'>"
        var kids = document.getElementsByClassName('requirement');
        for(aa=0; kids.length>aa; aa++){
            report += "\\n"+LT+"req id='"+kids[aa].id+"'>";
            report +=getRequirement(kids[aa]);
            report += LT+"/req>\\n";
        }
        report += LT+"/report>";
        initiateDownload('Report.text', report);
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
        ret = ret.replace(/\\&/g, '&amp;');
        ret = ret.replace(/\\</g, '&lt;');
        ret = ret.replace(/\\]\\]\\>/g, ']]&gt;');
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
                  ret+=getRequirement(node.nextSibling);
                  ret+=LT+"/selectable>";
               }
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

    function initiateDownload(filename, data) {

        var blob = new Blob([data], {type: 'text/xml'});
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

    function updateDependency(root, ids){
       var aa, bb;

       var delta=root.checked?1:-1;
       for(aa=0; ids.length>aa; aa++){
          id=ids[aa];

          var masters = document.getElementsByClassName(id+"_m");
          enabled=false;
          for(bb=0; masters.length>bb; bb++){
                if (masters[bb].checked){
                    enabled=true;
                }
          }
          if(enabled){
             document.getElementById(id).classList.remove('disabled');
          }
          else{
             document.getElementById(id).classList.add('disabled');
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
             var indy =   document.getElementById("sn_"+reqs[aa].id);
             if(reqValidator(reqs[aa])){
                 indy.classList.add('valid');
                 indy.classList.remove('invalid');
                 reqs[aa].classList.add('valid');
                 reqs[aa].classList.remove('invalid');
             }
             else{
                 indy.classList.add('invalid');
                 indy.classList.remove('valid');
                 reqs[aa].classList.add('invalid');
                 reqs[aa].classList.remove('valid');
             }
        }
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

           </script>
       </head>       <body onload='init();'><div id="main">
    """

    form +=  "      <h1>Worksheet for the " + root.getAttribute("name") + "</h1>\n"
    form +=  """
<noscript>
    <h1 class="warning">This page requires JavaScript.</h1></noscript>
    <h2 class="warning" id='url-warning' style="display: none;">
Most browsers do not store cookies from local pages (i.e, 'file:///...').
When you close this page, all data will most likely be lost.
             </h2>\n
    """

    form += state.handle_node(root, False)
    form += """
          <br/>
          <button type="button" onclick="generateReport()">Generate Report</button>
        </div> <!-- End of main -->
       <div class="sidenav">
       <div style="font-size: xx-large">&#187;</div>
         <table>
    """
    form += state.index
    form +="""
         </table>
       </div>

       </body>
    </html>
    """
    #      <button type="button" onclick="saveVals()">SaveOff</button>

    with open(outfile, "w") as out:
        out.write(form)

