def handle_section_boilerplate(name, node):
    if "boilerplate" in node.attrib and node.attrib["boilerplate"]=="no":
        return
    if name=="Conformance Claims":
        return """
    <dl>
        <dt>Conformance Statement</dt>
        <dd><xsl:choose><xsl:when test="//cc:Module">
          <p>This PP-Module inherits exact conformance as required from the specified
          Base-PP and as defined in the CC and CEM addenda for Exact Conformance, Selection-based
          SFRs, and Optional SFRs (dated May 2017).</p>
          <p>The following PPs and PP-Modules are allowed to be specified in a 
            PP-Configuration with this PP-Module. <ul>
            <xsl:for-each select="//cc:base-pp">
              <li><xsl:apply-templates select="." mode="make_xref"/></li>
            </xsl:for-each>
          </ul>
          </p>
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
