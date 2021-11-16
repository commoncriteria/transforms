<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:x="http://www.w3.org/1999/XSL/Transform"
  xmlns:cc="https://niap-ccevs.org/cc/v1"
  xmlns:htm="http://www.w3.org/1999/xhtml"
  xmlns:h="http://www.w3.org/1999/xhtml"
  xmlns:sec="https://niap-ccevs.org/cc/v1/section">

   <!--##############################################
        Template for universal sanity checks.
      ##############################################-->
  <xsl:template name="sanity-checks">
    <xsl:for-each select="//cc:TSS[.='']|//cc:Guidance[.='']|//cc:KMD[.='']|//cc:Tests[.='']">
      <xsl:message>*Error: Illegal empty <xsl:value-of select="local-name()"/> element at:
        <xsl:call-template name="genPath"/>
      </xsl:message>
    </xsl:for-each>
    <xsl:for-each select="//cc:depends/@*[not(../cc:external-doc)]">
       <xsl:if test="not(//*[@id=current()])">
        <xsl:message>* Error: Detected dangling id-reference to <xsl:value-of select="current()"/> from attribute
           <xsl:value-of select="name()"/>
       <!--<xsl:message>
          Error: Detected an 'id' attribute in a 'depends' element which is not allowed.
          <xsl:call-template name="genPath"/>-->
       </xsl:message>
       </xsl:if>
    </xsl:for-each>
    <xsl:for-each select="//cc:depends/@id">
       <xsl:message>* Error: Detected an 'id' attribute in a 'depends' element which is not allowed.
          <xsl:call-template name="genPath"/>
       </xsl:message>
    </xsl:for-each>
    <xsl:for-each select="//cc:title//cc:depends[not(parent::htm:tr)]|//cc:note//cc:depends">
       <xsl:message>* Warning: Potentially illegal 'depends' element.
          <xsl:call-template name="genPath"/>
       </xsl:message>
    </xsl:for-each>
    <xsl:for-each select="//@id">
       <xsl:variable name="id" select="."/>
       <xsl:if test="count(//*[@id=$id])>1">
         <xsl:message>* Error: Detected multiple elements with an id of '<xsl:value-of select="$id"/>'.</xsl:message>
       </xsl:if>
    </xsl:for-each>
    <xsl:for-each select="//cc:ref-id[not(parent::cc:doc)]">
	<xsl:variable name="refid" select="text()"/>
        <xsl:if test="not(//cc:*[@id=$refid])">
         <xsl:message>* Error: Detected dangling ref-id to '<xsl:value-of select="$refid"/>'.</xsl:message>
        </xsl:if>
    </xsl:for-each>
    <xsl:for-each select="//@ref-id">
	<xsl:variable name="refid" select="text()"/>
        <xsl:if test="not(//cc:*[@id=$refid])">
         <xsl:message>* Error: Detected dangling ref-id to '<xsl:value-of select="$refid"/>' 
           for a <xsl:value-of select="name()"/>.
         </xsl:message>
        </xsl:if>
    </xsl:for-each>
    <xsl:for-each select="//cc:deprecated">
       <xsl:message>* Warning: Detected a deprecated tag.  <xsl:call-template name="genPath"/> </xsl:message>
    </xsl:for-each>
   </xsl:template>



  <xsl:template match="/">
    <xsl:call-template name="sanity-checks"/>
  </xsl:template>
</xsl:stylesheet>
