<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:cc="https://niap-ccevs.org/cc/v1" xmlns:htm="http://www.w3.org/1999/xhtml">


  <!-- ############### -->
  <!-- This files defines how to make cross-references to different items. -->
  <!-- ############### -->
 
  <!-- ############### -->
  <!--                 -->
  <!-- ############### -->
   <xsl:template match="cc:chapter|cc:section|cc:subsection" mode="make_xref">
    <a href="#{@id}" class="dynref">Section </a>
  </xsl:template>

  <!-- ############### -->
  <!--                 -->
  <xsl:template match="cc:appendix" mode="make_xref">
    <a href="#{@id}" class="dynref"></a>
  </xsl:template>

   
  <!-- ############### -->
  <!--                 -->
  <xsl:template match="cc:figure" mode="make_xref">
    <a onclick="showTarget('figure-{@id}')" href="#figure-{@id}" class="figure-{@id}-ref">
      <xsl:apply-templates select="." mode="getPre"/>
      <span class="counter"><xsl:value-of select="@id"/></span>
    </a>
  </xsl:template>

  <!-- ############### -->
  <!--                 -->
  <xsl:template match="cc:ctr" mode="make_xref">
    <xsl:param name="prefix"><xsl:apply-templates select="." mode="getPre"/></xsl:param>
    <xsl:message> HERE </xsl:message>
    <a onclick="showTarget('cc-{@id}')" href="#cc-{@id}" class="cc-{@id}-ref" >
      <!-- should only run through once, but this is how we're changing contexts -->
      <xsl:apply-templates/><xsl:value-of select="$prefix"/> <span class="counter"><xsl:value-of select="id"/></span>
    </a>
  </xsl:template>


  <!-- ############### -->
  <!--                 -->
  <!-- ############### -->
   <xsl:template match="cc:f-element" mode="make_xref">
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
