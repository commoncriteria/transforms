import sys

def log(msg):
    sys.stderr.write(msg)
    sys.stderr.write("\n")

def make_attr_safe(attr):
    ret = attr.replace('&', '&amp;')
    return ret.replace('"', '&quot;')

def localtag(tag):
    return  tag.split("}")[1]

def get_attr_or(node, attr, default="", prefix="", suffix=""):
    if attr in node.attrib:
        return prefix+node.attrib[attr]
    return default

def is_attr(node, attr, val):
    if attr not in node.attrib:
        return False
    return node.attrib[attr] == val

