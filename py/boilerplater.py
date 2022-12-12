NS = {'cc': "https://niap-ccevs.org/cc/v1",
      'sec': "https://niap-ccevs.org/cc/v1/section",
      'htm': "http://www.w3.org/1999/xhtml"}

def handle_section_boilerplate(name, node, root):
    if "boilerplate" in node.attrib and node.attrib["boilerplate"]=="no":
        return
    ret=""
    if name=="Conformance Claims":
        ret="""
    <dl>
        <dt>Conformance Statement</dt>
        <dd>
"""

    if root.find("//cc:Module"):
        ret="""
          <p>This PP-Module inherits exact conformance as required from the specified
          Base-PP and as defined in the CC and CEM addenda for Exact Conformance, Selection-based
          SFRs, and Optional SFRs (dated May 2017).</p>
          <p>The following PPs and PP-Modules are allowed to be specified in a 
            PP-Configuration with this PP-Module. <ul>
"""
        
        for base in root.findall("//cc:base-pp", NS):
            ret+="<li>"+make_xref(<xsl:apply-templates select="." mode="make_xref"/>+"</li>"
            ret+="</ul>\n</p>"

            </xsl:when><xsl:otherwise>
	  <htm:p>
            An ST must claim exact conformance to this <xsl:call-template name="doctype-short"/>, 
            as defined in the CC and CEM addenda for Exact Conformance, Selection-based SFRs, and 
            Optional SFRs (dated May 2017).
	  </htm:p>
          <xsl:if test="/cc:PP//cc:module">
	    <htm:p>
              The following PP-Modules are allowed to be specified in a PP-Configuration with this PP.
              <htm:ul>
		<xsl:for-each select="/cc:PP//cc:module">
                  <htm:li><xsl:apply-templates select="." mode="make_xref"/></htm:li>
		</xsl:for-each>
              </htm:ul>
	  </htm:p>
        
"""
