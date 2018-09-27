#!/usr/bin/env python3
""" 
Module that converts PP xml documents to an HTML worksheet
"""

import base64
from io import StringIO 
import warnings
import re
import sys
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape
PPNS='https://niap-ccevs.org/cc/v1'
HTMNS="http://www.w3.org/1999/xhtml"
ns={"cc":PPNS, "htm":HTMNS}



def cc(tag):
    """ Creates a CC tag """
    return "{"+PPNS+"}"+tag

def htm(tag):
    return "{"+HTMNS + "}"+tag


def attr(el,at):
    if at in el.attrib: 
        return el.attrib[at]
    return ""


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
        self.parent_map = {c:p for p in self.root.iter() for c in p}
        # Used to run 'getElementByClassname'
        self.create_classmapping()

    def up(self, node):
        return self.parent_map[node]

    def create_classmapping(self):
        "Builds database to emulate getElementByClassname"
        self.classmap={}
        for el in self.root.findall(".//*[@class]"):
            classes = el.attrib["class"].split(",")
            for clazz in classes:
                # If we already have this class in the classmap
                if clazz in self.classmap:
                    # Grab the old
                    clazzset = self.classmap[clazz]
                    clazzset.add(el)
                else:
                    self.classmap[clazz]={el}


    def handle_management_function_set(self, elem):
        ret = "<table class='mfun-table'>\n"
        defaultVal = attr(elem,"default")
        if defaultVal == "":
            defaultVal="O"
            
        ret+= "<tr><th>Management Function</th>"
        for col in elem.findall( 'cc:manager', ns):
            ret += "<th>"
            ret += self.handle_contents(col, True)
            ret += "</th>"
        ret+= "</tr>\n"

        # Step through the rows
        for row in elem.findall( 'cc:management-function', ns):
            val={}
            # Build a dictionary where the key is 'ref' and
            # it maps to 'M', 'O', or '-'.
            for man in row.findall( 'cc:M', ns):
                val[man.attrib['ref']]='M'
            for opt in row.findall( 'cc:O', ns):
                val[man.attrib['ref']]='O'
            for das in row.findall( 'cc:_', ns):
                val[man.attrib['ref']]='-'
            # Now we convert this to the expected columns
            ret += "<tr>\n"
            # First column is the management function text
            ret += "<td>"+self.handle_contents( row.find( 'cc:text', ns), True) + "</td>"
            # And step through every other column
            for col in elem.findall( 'cc:manager', ns):
                ret += "<td>"
                colId = col.attrib["id"]
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
        if attr(node,"exclusive")=="yes":
            ret+=" onlyone"
        ret+="' data-rindex='"+ str(self.selectables_index) +"'>"

        self.selectables_index+=1
        rindex=0
        for child in node.findall("cc:selectable", ns):
            contents = self.handle_contents(child,True)
            contentCtr+=len(contents)
            chk = "<input type='checkbox'"
            onChange=""
            classes=""
            if attr(child,"exclusive") == "yes":
                onChange+="chooseMe(this);"
            id=attr(child,"id")
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
        if node.find( cc("base-pp") ) != None :
            ret = ""
        
        elif node.tag == cc("selectables"):
            return self.handle_selectables(node)

        elif node.tag == cc("refinement"):
            ret = "<span class='refinement'>"
            ret += self.handle_contents(node, True)
            ret += "</span>"
            return ret

        elif node.tag == cc("assignable"):
            ret = "<textarea onchange='update();' class='assignment val' rows='1' placeholder='"
            ret += ' '.join(self.handle_contents(node, True).split())
            ret +="'></textarea>"
            return ret

        elif node.tag == cc("abbr") or node.tag == cc("linkref"):
            if show_text:
                return attr(node,"linkend")

        elif node.tag == cc("management-function-set"):
            ret=self.handle_management_function_set(node)
            return ret

        elif node.tag == cc("section"):
            idAttr=node.attrib["id"]
            ret =""
            if "SFRs" == idAttr or "SARs" == idAttr:
                ret+="<h2>"+node.attrib["title"]+"</h2>\n"
            ret += self.handle_contents(node, False)
            return ret

        elif node.tag == cc("ctr-ref") and show_text:
            refid=node.attrib['refid']
            ret="<a onclick='showTarget(\"cc-"+refid+"\")' href=\"#cc-"+refid+"\" class=\"cc-"+refid+"-ref\">"
            target=self.root.find(".//*[@id='"+refid+"']")
            # What is prefix for?
            prefix=target.attrib["ctr-type"]+" "
            if "pre" in target.attrib:
                prefix=target.attrib["pre"]
            ret+="<span class=\"counter\">"+refid+"</span>"
            ret+="</a>"
            return ret
            
            
        elif node.tag == cc("ctr") and show_text:
            ctrtype=node.attrib["ctr-type"]
            prefix=ctrtype+" "
            if "pre" in node.attrib:
                prefix=node.attrib["pre"]
            idAttr=node.attrib["id"]
            ret="<span class='ctr' data-myid='"+idAttr+"+data-counter-type='ct-"
            ret+=ctrtype+"' id='cc-"+idAttr+"'>\n"
            ret+=prefix
            ret+="<span class='counter'>"+idAttr+"</span>"
            ret+=self.handle_contents(node, True)
            ret+="</span>"
            return ret
        
        # elif node.tag == cc("f-element") or node.tag == cc("a-element"):
        #     # Requirements are handled in the title section
        #     return self.handle_contents( node.find( 'cc:title', ns), True)

        elif node.tag == cc("f-component") or node.tag == cc("a-component"):
            status= attr(node,"status")
            ret=""
            id=node.attrib["id"]
            tooltip=""
            if status == "optional" or status == "objective":
                ret+="<div class='tooltipped'>"
                ret+="<input type='checkbox' onchange='modifyClass(this.nextSibling, \"disabled\", !this.checked)'></input>"
                tooltip="<span class='tooltiptext'>"+status+"</span>"

            ret+= "<span id='"+id+"'"
            # ret = "<div onfocusin='handleEnter(this)' id='"+id+"'"
            # The only direct descendants are possible should be the children
            node.findall( 'cc:selection-depends', ns)
            ret+=" class='component"
            if status!="":
                ret+=" disabled"
            ret+="'>"
            #<a href='#"+id+"'>
            ret+="<span class='f-comp-status'></span><a onclick='toggle(this); return false;' href='#"+id+"' class='f-comp-title'>"+id.upper()+" &mdash; "+ node.attrib["name"]+"</a>"
            ret+=tooltip
            ret+="\n<div class='reqgroup'>\n"
            ret+=self.handle_contents(node, False)
            ret+="\n</div></span></div><br/>"
            return ret
        elif node.tag == cc("title"):
            self.selectables_index=0
            req_id = self.up(node).attrib['id']
            com_id = self.up(self.up(node)).attrib['id']
            slaves = self.up(self.up(node)).findall( 'cc:selection-depends', ns)
            ret=""
            ret+="<div id='"+ req_id +"' class='requirement'>"
            ret+="<div class='f-el-title'>"+req_id.upper()+"</div>"
            ret+="<div class='words'>"
            ret+=self.handle_contents(node, True)
            ret+="</div>\n"
            ret+="</div>\n"
            return ret
        else:
            return self.handle_contents(node, show_text)
        return ""


    def handle_node(self, node, show_text):           
        if node.tag.startswith(cc("")):
            return self.handle_cc_node(node, show_text)
        # If we're not showing things OR it's a strike, just leave.
        elif not show_text or node.tag == htm("strike"):
            return ""
        elif node.tag == htm("br"):
            return "<br/>"
        elif node.tag.startswith(htm("")):
            # Just remove the HTML prefix and recur.
            tag = re.sub(r'{.*}', '', node.tag)
            ret = "<"+tag
            for key in node.attrib:
                ret+=" " + key + "='" + escape(node.attrib[key]) +"'"
            ret += ">"
            ret += self.handle_contents(node, True)
            ret += "</"+tag+">"
            return ret
        else:
            warnings.warn("Just dropped something")

    def handle_contents(self, node, show_text):
        ret=""
        if show_text:
            if node.text:
                ret = escape(node.text)
            for child in node:
                ret+=self.handle_node(child, show_text)
                if child.tail:
                    ret+=child.tail
        else:
            for child in node:
                ret+=self.handle_node(child, show_text)
        return ret

    def makeSelectionMap(self):
        """
        Makes a dictionary that maps the master requirement ID
        to an array of slave component IDs
        """
        for element in self.root.findall( 'cc:selection-depends', ns):
            # req=element.attrib["req"]
            selIds=element.attrib["ids"]
            slaveId=self.up(element).attrib["id"]
            for selId in selIds.split(','):
                reqs=[]
                if selId in self.selMap:
                    reqs =self.selMap[selId]
                reqs.append(slaveId)
                self.selMap[selId]=reqs


if __name__ == "__main__":
    if len(sys.argv) < 5:
        #        0       1          2          3                 4
        print("Usage: <js-file> <css-file> <xsl-file> <protection-profile>[::<output-file>] [<module-1> [<module-2> ... ]]")
        sys.exit(0)

    jsfile=sys.argv[1]
    cssfile=sys.argv[2]
    xslfile=sys.argv[3]
    # Split on double colon
    out=sys.argv[4].split('::')


    infile=out[0]
    outfile=""
    if len(out) < 2:
        outfile=infile.rsplit('.',1)[0]+"-worksheet.html"
    else:
        outfile=out[1]

    # Parse the PP and make state from it

    state=State(ET.parse(infile).getroot())

    state.makeSelectionMap()

    with open(jsfile, "r") as in_handle:
        js = in_handle.read()

    with open(cssfile, "r") as in_handle:
        css = in_handle.read()

    with open(infile, "rb") as in_handle:
        inb64 = base64.b64encode(in_handle.read()).decode('ascii')

    with open(xslfile, "rb") as in_handle:
        xslb64 = base64.b64encode(in_handle.read()).decode('ascii')


    for modctr in range(5, len(sys.argv)):
        print("Module: " + sys.argv[modctr])

    form =  "<html xmlns='http://www.w3.org/1999/xhtml'>\n"
    form += "   <head>\n"
    form += "      <meta charset='utf-8'></meta>\n"
    form += "      <title>"+state.root.attrib["name"]+"</title>\n"
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

    form +=  "      <h1>Worksheet for the " + state.root.attrib["name"] + "</h1>\n"
    form +=  """
<div class='warning-pane'>
   <noscript><h2 class="warning">This page requires JavaScript.</h2></noscript>
    <h2 class="warning" id='url-warning' style="display: none;">
    Most browsers do not store cookies from local pages (i.e, 'file:///...').
    When you close this page, all data will most likely be lost.</h2>
</div>
    """

    form += state.handle_contents(state.root, False)
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

