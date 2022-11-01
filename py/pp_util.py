import sys

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

def get_attr_or(node, attr, default="", post=lambda x:x):
    if attr in node.attrib:
        return post(node.attrib[attr])
    return default

def is_attr(node, attr, val):
    if attr not in node.attrib:
        return False
    return node.attrib[attr] == val

def make_wrappable(text):
#    return text.replace("_", "_|")
    return text.replace("_", "_\u200b")

def NoneStr(text):
    if text is None:
        return ""
    return text

def flatten(el):
    ret = NoneStr(el.text)
    for subel in el:
        ret += flatten(subel)
        ret += NoneStr(subel.tail)
    return " ".join(ret.split())
        
def ccver():
    return "Version 3.1, Revision 5"
