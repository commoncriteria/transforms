#!/usr/bin/env python3

from io import StringIO 
import re
import sys
import xml.dom.minidom
from xml.dom import minidom
from xml.sax.saxutils import escape

class State:
    def __init__(self):
        # Maps selection IDs to Requirements
        # If the selection is made, then the requirement is included
        self.selMap={}
        # Maps component IDs to sections
        self.compMap={}
        # Current index for the selectables
        self.selectables_index=0
        # index
        self.index=""

    def node_to_text(self, node):
        ret=""
        if node.nodeType == xml.dom.Node.TEXT_NODE:
            ret += escape(node.data)
        elif node.nodeType == xml.dom.Node.ELEMENT_NODE:
            # sys.stderr.write("Tagname is"+ node.tagName)
            if node.tagName == "selectables":
                sels=[]
                contentCtr=0
                ret+="<span class='selectables' data-rindex='"+ str(self.selectables_index) +"'>"
                self.selectables_index+=1
                rindex=0
                for child in node.childNodes: # Hopefully only selectable
                    if child.nodeType == xml.dom.Node.ELEMENT_NODE and child.tagName == "selectable":
                        contents = self.title_to_form(child)
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
                        chk +=">"+ contents+"</input>\n";
                        sels.append(chk)
                        rindex+=1
                if contentCtr < 50:
                    for sel in sels:
                        ret+= sel
                else:
                    ret+="<ul>\n"
                    for sel in sels:
                        ret+= "<li>"+sel+"</li>\n"
                    ret+="</ul>\n"
                ret+="</span>"
            elif node.tagName == "refinement":
                ret += "<span class='refinement'>"
                ret += self.title_to_form(node)
                ret += "</span>"
            elif node.tagName == "assignable":
                ret += "<textarea onchange='update();' class='assignment val' rows='1' placeholder='"
                ret += ' '.join(self.title_to_form(node).split())
                ret +="'></textarea>"

            elif node.tagName == "abbr" or node.tagName == "linkref":
                ret += node.getAttribute("linkend")
            elif node.tagName == "h:strike":
                pass
            elif ":" in node.tagName:
                tag = re.sub(r'.*:', '', node.tagName)
                ret += "<"+tag
                attrs = node.attributes
                for aa in range(0,attrs.length) :
                    attr =attrs.item(aa)
                    ret+=" " + attr.name + "='" + escape(attr.value) +"'"
                ret += ">"
                ret += self.title_to_form(node)
                ret += "</"+tag+">"
        return ret


    def makeSelectionMap(self, root):
        for element in root.getElementsByTagNameNS('https://niap-ccevs.org/cc/v1', 
                                                   'selection-depends'):
            # req=element.getAttribute("req");
            selIds=element.getAttribute("ids");
            slaveId=element.parentNode.getAttribute("id");
            for selId in selIds.split(','):
                reqs=[]
                if selId in self.selMap:
                    reqs =self.selMap[selId];
                reqs.append(slaveId)
                self.selMap[selId]=reqs



    def title_to_form(self, title):
        ret=""
        for node in title.childNodes:
            ret+=self.node_to_text(node)
        return ret

    def descend(self, root):
        ret=""
        for node in root.childNodes:
            if node.nodeType == xml.dom.Node.ELEMENT_NODE:
                if node.tagName == "section":
                    idAttr=node.getAttribute("id")
                    if "SFRs" == idAttr or "SARs" == idAttr:
                        ret+="<h2>"+node.getAttribute("title")+"</h2>\n"
                elif node.tagName == "f-component" or node.tagName == "a-component":
                    id=node.getAttribute("id")
                    self.index+="<tr><td>&#x2714;</td><td><a href='#"+id+"'>"+id+"</a></td></tr>\n"

                    ret+="<div id='"+id+"'"
                    # The only direct descendants are possible should be the children
                    child=node.getElementsByTagNameNS('https://niap-ccevs.org/cc/v1', 
                                                'selection-depends')
                    if child.length > 0:
                        ret+=" class='disabled'"
                    ret+=">"
                    ret+="<h3>"+id+" &mdash; "+ node.getAttribute("name")+"</h3>\n"
                    ret+=self.descend(node)
                    ret+="</div>"
                    continue
                elif node.tagName == "title":
                    self.selectables_index=0
                    ret+="<div id='"+node.parentNode.getAttribute('id') +"' data-id='" + node.parentNode.getAttribute('id') + "'>"
                    ret+=self.title_to_form(node)
                    # ret+="<br></br>"
                    # ret+="<textarea rows='5' cols='70' class='notes'></textarea>"
                    ret+="</div>\n"
                ret+=self.descend(node)
        return ret



if len(sys.argv) < 2:
    print("Usage: <check-it.py> <protection-profile>[:<output-file>]")
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
/*
.disabled *{
   display: none;
}
*/


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
       <script type='text/javascript'>

const AMPERSAND=String.fromCharCode(38);
const LT=String.fromCharCode(60);

var cookieJar=[];

function performActionOnVals(fun){
    // Run through all the elements with possible
    // values
    var aa;
    var elems = document.getElementsByClassName("val");
    for(aa=0; elems.length> aa; aa++){
       fun(elems[aa], "v_"+aa);
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
        alert("Most browsers do not store cookies from local pages (i.e, 'file:///...').\\n"+
              "When you close this page, all data will most likely be lost." );
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
    report += LT+"report xmlns='https://niap-ccevs.org/cc/pp/report/v1'>"
    report += generateReportHelper(document.body);
    report += LT+"/report>"
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

function generateReportHelper(root){
   var ret=""
   var reqid = root.getAttribute('data-id');
   if( reqid ){
      ret+=LT+"req id='"+reqid+"'>";
      ret+=getRequirements(root.children);
      ret+=LT+"/req>\\n";
      return ret;
   }
   else{
      var children = root.children;
      var aa;
      for (aa=0; aa!=children.length; aa++){
         ret += generateReportHelper(children[aa]);
      }
      return ret;
   }
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
     
      var masters = document.getElementsByClassName(id+"_m");
      enabled=false;
      console.log("Checking " + masters.length);
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
   sched = setTimeout(saveVals, 1000);
}

function saveVals(){
   performActionOnVals(saveToCookieJar);
   saveAllCookies(cookieJar);
   sched = undefined;
}

function toggleFirstCheckboxExcept(root, exc){
   if (root == exc) return;
   if ( isCheckbox(root)){
      root.disabled=exc.checked;
      return;
   }
   var children = root.children;
   var aa;
   for (aa=0; aa!=children.length; aa++){
      toggleFirstCheckboxExcept(children[aa], exc);
   }
}

       </script>
   </head>
   <body onload='init();'><div id="main">
"""

form +=  "      <h1>Worksheet for the " + root.getAttribute("name") + "</h1>\n"
form +=  "         <h2 id='file-url-warning'></h2>

form += state.descend(root)
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

