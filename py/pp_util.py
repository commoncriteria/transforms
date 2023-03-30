
import sys
from lxml.builder import ElementMaker



HTM_E=ElementMaker(namespace=None,
                   nsmap={None: "http://www.w3.org/1999/xhtml"})

def debug_node(node):
    """ 
    Converts a node into a debug string.

    :param node: The node to convert.
    :returns A string value of the node.
    """
    tag =node.tag
    ret = "<"+tag+""
    for attr in node.attrib:
        ret += " " + attr + "='"+node.attrib[attr]+"'"
    ret += ">"+NoneStr(node.text)
    for child in node:
        ret += debug_node(child)
        ret += NoneStr(child.tail)
    return ret+"</"+tag+">"
        

def get_HTM_E():
    """ 
    Gets the HTML element creator

    :returns The HTML element creator.
    """
    return HTM_E

def adopt(parent, child):
    """
    Appends a child to a parent

    :param parent:
    :param  child:
    :returns 
    """
    parent.append(child)
    return child

def append_text(node, text):
    """
    Appends text to a node, after
    all the children.
    :param node:
    :param  text:
    :returns
    """
    if text == None:
        return
    if len(node)==0:
        if node.text == None:
            node.text = text
        else:
            node.text += text
    else:
        if node[-1].tail == None:
            node[-1].tail = text
        else:
            node[-1].tail += text

    
def get_meaningful_ancestor(root, refid):
    """
    :param root:
    :param  refid:
    :returns 
    """
    ret = root.xpath(".//cc:f-element[.//@id='"+refid+"']|.//cc:choice[.//@id='"+refid+"']|.//cc:feature[.//@id='"+refid+"']", namespaces=NS)
    if len(ret) != 1:
        raise Exception("Should only be one thing")
    return ret[0]



NS = {'cc': "https://niap-ccevs.org/cc/v1",
      'sec': "https://niap-ccevs.org/cc/v1/section",
      'htm': "http://www.w3.org/1999/xhtml"}

def log(msg):
    """
    :param msg:
    :returns 
    """
    sys.stderr.write(msg)
    sys.stderr.write("\n")

def make_attr_safe(attr):
    """
    :param attr:
    :returns 
    """
    ret = attr.replace('&', '&amp;')
    return ret.replace('"', '&quot;')

def localtag(tag):
    """
    :param tag:
    :returns 
    """
    return  tag.split("}")[-1]

def get_attr_or(node, attr, default=""):
    """
    :
    :param node:
    :param  attr:
    :param  default="":
    :returns 
    """
    if attr in node.attrib:
        return node.attrib[attr]
    return default

def maybe_add_attr(attrs, node, attr, default=None):
    """
    If the attribute exists in the nodes attributes,
    add it to the attrs dictionary.
    If not and default is not None, add the default
    to the attrs dictionary.

    :param attrs:
    :param  node:
    :param  attr:
    :param  default=None:
    """
    if attr in node.attrib:
        attrs[attr]=node.attrib[attr]
    elif default is not None:
        attrs[attr]=default

def is_attr(node, attr, val):
    """
    :param node:
    :param  attr:
    :param  val:
    :returns 
    """
    if attr not in node.attrib:
        return False
    return node.attrib[attr] == val

def make_wrappable(text):
    """
    :param text:
    :returns 
    """
#    return text.replace("_", "_|")
    return text.replace("_", "_\u200b")

def NoneStr(text):
    """
    :param text:
    :returns 
    """
    if text is None:
        return ""
    return text

def flatten(el):
    """
    :param el:
    :returns 
    """
    ret = NoneStr(el.text)
    for subel in el:
        ret += flatten(subel)
        ret += NoneStr(subel.tail)
    return " ".join(ret.split())
        
def ccver():
    """
    :returns 
    """
    return "Version 3.1, Revision 5"

def add_js(parent):
    """
    :param parent:
    :returns 
    """
    E=ElementMaker()
    parent.append( E.script(
        {"src":"https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.1/MathJax.js?config=TeX-AMS-MML_HTMLorMML",
         "type":"text/javascript"})
    )
    parent.append(E.script({"type":"text/x-mathjax-config"},
                           """MathJax.Hub.Config({
                    extensions: ["tex2jax.js"],
                    jax: ["input/TeX", "output/HTML-CSS"],
                    showMathMenu: false,
                    tex2jax: {
                      inlineMath: [ ['$','$'], ["\\\\(","\\\\)"] ],
                      displayMath: [ ['$$','$$'], ["\\\\[","\\\\]"] ],
                      processEscapes: true
                    },
                    styles: {
        
                        ".MathJax_Display": {
                        "text-align": "left !important",
                        margin:       "0em 0em !important"
                    }}
                    });"""))
    parent.append(
        E.script({"type":"text/javascript"},
"""// Called on page load to parse URL parameters and perform actions on them.
        function init(){
            if(getQueryVariable("expand") == "on"){
              expand();
            }
	    if (getQueryVariable("hide_eas")=="on"){
		hide_eas()
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
        const AMPERSAND=String.fromCharCode(38);


      function hide_eas(){
	  console.log("Hello")
	  els = document.getElementsByClassName("activity_pane");
          var aa;
	  for(aa=0; aa!=els.length; aa++){
	      console.log("AA is " + aa)
	      els[aa].style.display="none";
	  }
        }
        
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
"""))
    return 
