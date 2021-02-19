<xsl:stylesheet version="1.0"
   xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
   xmlns:cc="https://niap-ccevs.org/cc/v1"
   xmlns:sec="https://niap-ccevs.org/cc/v1/section"
   xmlns:htm="http://www.w3.org/1999/xhtml">


  <!-- ############### -->
  <!-- This files defines how to make cross-references to different items. -->
  <!-- ############### -->
  <!-- ############### -->
  <!--                 -->
  <!-- ############### -->
  <xsl:template match="cc:selectable" mode="make_xref">
    <xsl:variable name="r-id"><xsl:apply-templates select="." mode="getId"/></xsl:variable>

    <a href="#{$r-id}">
      <xsl:choose>
        <xsl:when test="cc:readable"><xsl:apply-templates select="cc:readable"/></xsl:when>

<!--- We want snips in our selectable, but not snips that are descendants of subselectabls -->
        <xsl:when test=".//cc:snip">
          <xsl:apply-templates select="descendant::cc:snip[1]"/>...
          </xsl:when> 
        <xsl:otherwise><xsl:apply-templates/></xsl:otherwise>
      </xsl:choose>
    </a>
  </xsl:template>

  
  <!-- ############### -->
  <!--                 -->
  <!-- ############### -->
  <xsl:template name="make-readable-index">
    <xsl:param name="index"/>
    <xsl:variable name="lastchar" select="substring($index, string-length($index))"/>
    <xsl:variable name="last2char" select="substring($index, string-length($index)-1)"/>
    <xsl:value-of select="$index"/>
    <sup><xsl:choose>
      <xsl:when test="$last2char='11' or $last2char='12' or $last2char='13'">th</xsl:when>
      <xsl:when test="$lastchar='1'">st</xsl:when>
      <xsl:when test="$lastchar='2'">nd</xsl:when>
      <xsl:when test="$lastchar='3'">rd</xsl:when>
      <xsl:otherwise>th</xsl:otherwise>
    </xsl:choose></sup>
  </xsl:template> 


  <!-- ############### -->
  <!--                 -->
  <!-- ############### -->
  <xsl:template match="cc:f-element//cc:assignable" mode="make_xref">
    <a href="#{@id}">
<!--  This won't compile:  <xsl:variable name="index">
      <xsl:number count="ancestor::cc:f-element//cc:assignable" level="any"/>
    </xsl:variable>, so I'm using the following inefficient hack -->
     <xsl:call-template name="make-readable-index">
      <xsl:with-param name="index"><xsl:for-each select="ancestor::cc:f-element//cc:assignable">
        <xsl:if test="current()/@id=./@id"><xsl:value-of select="position()"/></xsl:if></xsl:for-each>
      </xsl:with-param></xsl:call-template>
    assignment</a>
  </xsl:template>

  <!-- ############### -->
  <!--                 -->
  <!-- ############### -->
  <xsl:template match="cc:management-function//cc:assignable" mode="make_xref">
    <a href="#{@id}">
<!--TODO: This seems really inefficient.-->
      <xsl:variable name="index"><xsl:for-each select="ancestor::cc:management-function//cc:assignable">
        <xsl:if test="current()/@id=./@id"><xsl:value-of select="position()"/></xsl:if></xsl:for-each>
      </xsl:variable>
      <xsl:variable name="lastchar" select="substring($index, string-length($index))"/>
      <xsl:variable name="last2char" select="substring($index, string-length($index)-1)"/>
      <xsl:value-of select="$index"/>
      <sup><xsl:choose>
	<xsl:when test="$last2char='11' or $last2char='12' or $last2char='13'">th</xsl:when>
	<xsl:when test="$lastchar='1'">st</xsl:when>
	<xsl:when test="$lastchar='2'">nd</xsl:when>
	<xsl:when test="$lastchar='3'">rd</xsl:when>
        <xsl:otherwise>th</xsl:otherwise>
      </xsl:choose></sup>
    assignment</a>
 </xsl:template>
 
  <!-- ############### -->
  <!--                 -->
  <!-- ############### -->
   <xsl:template match="cc:section" mode="make_xref">
    <xsl:param name="format" select="''"/>
    <a href="#{@id}" class="dynref">Section </a>
  </xsl:template>

  <xsl:template match="sec:*" mode="make_xref">
    <xsl:param name="format" select="''"/>
    <a href="#{local-name()}" class="dynref">Section </a>
  </xsl:template>
  <!-- ############### -->
  <!--                 -->
  <xsl:template match="cc:appendix" mode="make_xref">
    <a href="#{@id}" class="dynref"></a>
  </xsl:template>
 
  <xsl:template match="cc:bibliography/cc:entry" mode="make_xref">
     <a href="#{@id}">[<xsl:apply-templates select="cc:tag"/>]</a>
  </xsl:template>


  <xsl:template match="cc:*" mode="make_xref">
    <xsl:message>Unable to make an xref for <xsl:value-of select="name()"/></xsl:message>
  </xsl:template>
  <!-- ############### -->
  <!--                 -->
  <xsl:template match="cc:ctr|cc:figure|cc:equation" mode="make_xref">
    <xsl:param name="eprefix"/> <!-- explicit prefix -->
    <xsl:param name="has-eprefix"/>

    <xsl:call-template name="make_ctr_ref">
      <xsl:with-param name="prefix"><xsl:choose>
        <xsl:when test="$has-eprefix='y'"><xsl:value-of select="$eprefix"/></xsl:when>
        <xsl:when test="local-name()='equation'">Eq. </xsl:when>
        <xsl:otherwise><xsl:apply-templates select="." mode="getPre"/></xsl:otherwise>
      </xsl:choose></xsl:with-param>
      <xsl:with-param name="id" select="@id"/>
    </xsl:call-template>
  </xsl:template>


  <!-- ############### -->
  <!--                 -->
  <!-- ############### -->
  <xsl:template name="make_ctr_ref">
    <xsl:param name="id"/>
    <xsl:param name="prefix"/>
    <a onclick="showTarget('{$id}')" href="#{$id}" class="{$id}-ref" >
      <xsl:value-of select="$prefix"/> <span class="counter"><xsl:value-of select="$id"/></span>
    </a>
  </xsl:template>

  <!-- ############### -->
  <!--                 -->
  <!-- ############### -->
  <!-- Making a references is the same as getting they ID for these structures. -->
  <xsl:template match="cc:f-component-decl|cc:f-component|cc:f-element" mode="make_xref">
     <xsl:apply-templates mode="getId" select="."/>
  </xsl:template>

  <!-- ############### -->
  <!--                 -->
  <!-- ############### -->
  <xsl:template match="cc:management-function" name="management-function" mode="make_xref">
     <xsl:param name="nolink"  select="@nolink"     />
     <xsl:param name="prefix"  select="'Function #'"/>
     <xsl:param name="index"   select="count(preceding::cc:management-function)+1"/>
     <xsl:choose>
       <xsl:when test="$nolink='y'">
         <xsl:value-of select="concat($prefix, $index)"/>
       </xsl:when>
       <xsl:otherwise>
        <a href="#{@id}"><xsl:value-of select="concat($prefix, $index)"/></a>
       </xsl:otherwise>
     </xsl:choose>
  </xsl:template>

</xsl:stylesheet>
