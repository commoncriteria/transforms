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
        self.man_fun_map['O']="<select><option value='-'>-</option><option value='X'>X</option></select>"


    def handle_management_function_set(self, elem):
        ret = "<table>\n"
        defaultVal = elem.getAttribute("default")
        if defaultVal == "":
            defaultVal="O"

            
        ret+= "<tr><th>Management Function</th>"
        for col in getPpEls(elem, 'manager'):
            ret += "<th>"
            ret += self.handle_node(col, True);
            ret += "</th>"
        ret+= "</tr>\n"


        for row in  getPpEls(elem, 'management-function'):
            val={}
            for man in getPpEls(row, 'M'):
                val[man.getAttribute('ref')]='M'
            for opt in getPpEls(row, 'O'):
                val[man.getAttribute('ref')]='O'
            for das in getPpEls(row, '_'):
                val[man.getAttribute('ref')]='-'
                
            ret += "<tr>\n"
            ret += "<td>"+self.handle_parent( getPpEls(row, 'text')[0], True) + "</td>"
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
        ret="<span class='selectables' data-rindex='"+ str(self.selectables_index) +"'>"
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
                chk +="><span>"+ contents+"</span></input>\n";
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
                idAttr=node.getAttribute("id")
                ret =""
                if "SFRs" == idAttr or "SARs" == idAttr:
                    ret+="<h2>"+node.getAttribute("title")+"</h2>\n"
                ret += self.handle_parent(node, False)
                return ret
            elif node.tagName == "f-element" or node.tagName == "a-element":
                return self.handle_node( getPpEls(node, 'title')[0], True)
            elif node.tagName == "f-component" or node.tagName == "a-component":
                id=node.getAttribute("id")
                self.index+="<tr><td>&#x2714;</td><td><a href='#"+id+"'>"+id+"</a></td></tr>\n"
                ret = "<div id='"+id+"'"
                # The only direct descendants are possible should be the children
                child=getPpEls(node, 
                                            'selection-depends')
                if child.length > 0:
                    ret+=" class='disabled'"
                ret+=">"
                ret+="<h3>"+id+" &mdash; "+ node.getAttribute("name")+"</h3>\n"
                ret+=self.handle_parent(node, True)
                ret+="</div>"
                return ret
            elif node.tagName == "title":
                self.selectables_index=0
                ret=""
                ret+="<div id='"+node.parentNode.getAttribute('id') +"' class='requirement'>"
                ret+=self.handle_parent(node, True)
                ret+="</div>\n"
                return ret
                
            elif node.tagName == "h:strike":
                # Just ignore text that is striken
                pass

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
        width: 160px;
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

    function performActionOnVals(fun){
        // Run through all the elements with possible
        // values
        var aa;
        var elems = getPpEls(document, "v_"+aa);
        }
    }

    function isCheckbox(elem){
        return elem.getAttribute("type") == "checkbox";
    }

    function saveToCookieJar(elem, id){
        if( isCheckbox(elem)){
            cookieJar[id]=elem.checked;
        }
        else{
            if(elem.value != undefined && elem.value != "undefined" ){
               console.log("Saving " + elem.value + " to " + id + "("+elem.tagName+")");
               cookieJar[id]=elem.value;
            }
        }
    }

    function retrieveFromCookieJar(elem, id){
        if( isCheckbox(elem)){
            elem.checked= (cookieJar[id] == "true");
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
        performActionOnVals(retrieveFromCookieJar);
    }

    function readAllCookies() {
            ret=[];
            var ca = document.cookie.split(';');
            console.log("Cookies are " + document.cookie);
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
    //            console.log("Reading " + val+" for |" + key+"|");
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
    //       console.log("Saving off " + cookies[key] + " to "+key);
           createCookie(key, cookies[key] );
        }
    }

    function createCookie(name,value) {
        var date = new Date();
        // 10 day timeout
        date.setTime(date.getTime()+(10*24*60*60*1000));
        var expires = "; expires="+date.toGMTString();
        console.log("Creating: " + name+"="+encodeURIComponent(value)+expires+"; path=/");
        document.cookie = name+"="+encodeURIComponent(value)+expires+"; path=/";

    }

    function eraseCookie(name) {
        createCookie(name,"",-1);
    }

    function generateReport(){
        var report = LT+"?xml version='1.0' encoding='utf-8'?>\\n"
        var aa;
       
        report += LT+"report xmlns='https://niap-ccevs.org/cc/pp/report/v1'>"
        var kids = getPpEls(document, report);
    }

    function getRequirements(nodes){
      ret="";
      var bb=0;
      for(bb=0; bb!=nodes.length; bb++){
        ret+=getRequirement(nodes[bb]);
      }
      return ret;
    }

    function getRequirement(node){
        var ret = ""
        if(node.nodeType==1){
           if(isCheckbox(node)){
               if(node.checked){
                  ret+=LT+"selectable index='"+node.getAttribute('data-rindex')+"'>"; 
                  ret+=getRequirements(node.children);
                  ret+=LT+"/selectable>";
               }
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
               ret+=val;
               ret+=LT+"/assignment>\\n";
           }
           else{
               ret+=getRequirements(node.children);
           }
        }
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
       console.log("Here");

       var delta=root.checked?1:-1;
       for(aa=0; ids.length>aa; aa++){
          id=ids[aa];

          var masters = getPpEls(document, 1000);
    }

    function saveVals(){
       performActionOnVals(saveToCookieJar);
       saveAllCookies(cookieJar);
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

