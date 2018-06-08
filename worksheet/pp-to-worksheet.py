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
    def __init__(self, theroot):
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
        # Value for mandatory function
        self.man_fun_map['M']="X"
        # Value of N/A function
        self.man_fun_map['-']="-"
        # Value for Optional function
        self.man_fun_map['O']="<select onchange='update();' class='val'><option value='O'>O</option><option value='X'>X</option></select>"
        # Holds the root
        self.root=theroot
        # Maps IDs to elements
        self.idMap={}
        self.harvest_ids(self.root)

    # getElementById doesn't work well with minidom,
    # so we're faking.
    def harvest_ids(self, node):
        if node.nodeType == xml.dom.Node.ELEMENT_NODE:
            self.idMap[node.getAttribute("id")]=node
            for child in node.childNodes:
                self.harvest_ids(child)

    def handle_management_function_set(self, elem):
        ret = "<table class='mfun-table'>\n"
        defaultVal = elem.getAttribute("default")
        if defaultVal == "":
            defaultVal="O"
            
        ret+= "<tr><th>Management Function</th>"
        for col in getPpEls(elem, 'manager'):
            ret += "<th>"
            ret += self.handle_node(col, True)
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
            ret += "<td>"+self.handle_collection( getPpEls(row, 'text')[0], True) + "</td>"
            # And step through every other column
            for col in getPpEls(elem, 'manager'):
                ret += "<td>"
                colId = col.getAttribute("id")
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
                chk+= " onchange='update(); "+onChange+"'"
                chk+= " data-rindex='"+str(rindex)+"'"
                chk +=" class='val selbox"+classes+"'"
                chk +="></input><span>"+ contents+"</span>\n"
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
            ret += self.handle_collection(node, True)
            ret += "</span>"
            return ret

        elif node.localName == "assignable":
            ret = "<textarea onchange='update();' class='assignment val' rows='1' placeholder='"
            ret += ' '.join(self.handle_collection(node, True).split())
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
            ret += self.handle_collection(node, False)
            return ret

        elif node.localName == "ctr-ref" and show_text:
            refid=node.getAttribute('refid')
            ret="<a onclick='showTarget(\"cc-"+refid+"\")' href=\"#cc-"+refid+"\" class=\"cc-"+refid+"-ref\">"
            target=self.idMap[refid]
            prefix=target.getAttribute("ctr-type")+" "
            if target.hasAttribute("pre"):
                prefix=target.getAttribute("pre")
            ret+="<span class=\"counter\">"+refid+"</span>"
            ret+="</a>"
            return ret
            
            
        elif node.localName == "ctr" and show_text:
            ctrtype=node.getAttribute("ctr-type")
            prefix=ctrtype+" "
            if node.hasAttribute("pre"):
                prefix=node.getAttribute("pre")
            idAttr=node.getAttribute("id")
            ret="<span class='ctr' data-myid='"+idAttr+"+data-counter-type='ct-"
            ret+=ctrtype+"' id='cc-"+idAttr+"'>\n"
            ret+=prefix
            ret+="<span class='counter'>"+idAttr+"</span>"
            ret+=self.handle_collection(node, True)
            ret+="</span>"
            return ret
        
        elif node.localName == "f-element" or node.localName == "a-element":
            # Requirements are handled in the title section
            return self.handle_node( getPpEls(node, 'title')[0], True)

        elif node.localName == "f-component" or node.localName == "a-component":
            status= node.getAttribute("status")
            ret=""
            id=node.getAttribute("id")
            tooltip=""
            if status == "optional" or status == "objective":
                ret+="<div class='tooltipped'>"
                ret+="<input type='checkbox' onchange='modifyClass(this.nextSibling, \"disabled\", !this.checked)'></input>"
                tooltip="<span class='tooltiptext'>"+status+"</span>"

            ret+= "<span id='"+id+"'"
            # ret = "<div onfocusin='handleEnter(this)' id='"+id+"'"
            # The only direct descendants are possible should be the children
            child=getPpEls(node, 'selection-depends')
            ret+=" class='component"
            if status!="":
                ret+=" disabled"
            ret+="'>"
            #<a href='#"+id+"'>
            ret+="<span class='f-comp-status'></span><a onclick='toggle(this); return false;' href='#"+id+"' class='f-comp-title'>"+id.upper()+" &mdash; "+ node.getAttribute("name")+"</a>"
            ret+=tooltip
            ret+="\n<div class='reqgroup'>\n"
            ret+=self.handle_collection(node, False)
            ret+="\n</div></span></div><br></br>"
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
            ret+=self.handle_collection(node, True)
            ret+="</div>\n"
            ret+="</div>\n"
            return ret
        else:
            return self.handle_collection(node, show_text)
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
                    ret += self.handle_collection(node, True)
                    ret += "</"+tag+">"
                    return ret
        return ""

    def handle_collection(self, node, show_text):
        ret=""
        for child in node.childNodes:
            ret += self.handle_node(child, show_text)
        return ret

    def makeSelectionMap(self):
        """
        Makes a dictionary that maps the master requirement ID
        to an array of slave component IDs
        """
        for element in getPpEls(self.root, 'selection-depends'):
            # req=element.getAttribute("req")
            selIds=element.getAttribute("ids")
            slaveId=element.parentNode.getAttribute("id")
            for selId in selIds.split(','):
                reqs=[]
                if selId in self.selMap:
                    reqs =self.selMap[selId]
                reqs.append(slaveId)
                self.selMap[selId]=reqs


if __name__ == "__main__":
    if len(sys.argv) < 5:
        #        0       1          2          3                 4
        print("Usage: <js-file> <css-file> <xsl-file> <protection-profile>[:<output-file>]")
        sys.exit(0)

    jsfile=sys.argv[1]
    cssfile=sys.argv[2]
    xslfile=sys.argv[3]
    # Split on colon
    out=sys.argv[4].split(':')
    infile=out[0]
    outfile=""
    if len(out) < 2:
        outfile=infile.split('.')[0]+"-worksheet.html"
    else:
        outfile=out[1]

    # Parse the PP and make state from it
    state=State(minidom.parse(infile).documentElement)

    state.makeSelectionMap()



    with open(jsfile, "r") as in_handle:
        js = in_handle.read()

    with open(cssfile, "r") as in_handle:
        css = in_handle.read()

    with open(infile, "rb") as in_handle:
        inb64 = base64.b64encode(in_handle.read()).decode('ascii')

    with open(xslfile, "rb") as in_handle:
        xslb64 = base64.b64encode(in_handle.read()).decode('ascii')



    form =  "<html xmlns='http://www.w3.org/1999/xhtml'>\n"
    form += "   <head>\n"
    form += "      <meta charset='utf-8'></meta>\n"
    form += "      <title>"+state.root.getAttribute("name")+"</title>\n"
    form += "      <style type='text/css'>\n"
    form += css
    form += """      </style>
           <script type='text/javascript'>//<![CDATA[
"""
    form+= " const ORIG64='"+inb64+"';\n"
    form+= " const XSL64='"+xslb64+"';\n"
    form+= js
    form+="""
//]]>
           </script>
       </head>       <body onkeypress='handleKey(event); return true;' onload='init();'>
"""

    form +=  "      <h1>Worksheet for the " + state.root.getAttribute("name") + "</h1>\n"
    form +=  """
<div class='warning-pane'>
   <noscript><h2 class="warning">This page requires JavaScript.</h2></noscript>
    <h2 class="warning" id='url-warning' style="display: none;">
    Most browsers do not store cookies from local pages (i.e, 'file:///...').
    When you close this page, all data will most likely be lost.</h2>
</div>
    """

    form += state.handle_node(state.root, False)
    form += """
          <br/>
          <button type="button" onclick="generateReport()">XML Record</button>
          <button type="button" onclick="fullReport()">HTML Report</button>
          <div id='report-node' style="display: none;"/>
       </body>
    </html>
"""
    with open(outfile, "w") as out:
        out.write(form)

