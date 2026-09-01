<?xml version="1.0" encoding="utf-8"?>

<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:cc="https://niap-ccevs.org/cc/v1"
  xmlns="http://www.w3.org/1999/xhtml"
  xmlns:htm="http://www.w3.org/1999/xhtml"
  version="1.0">
  


  <xsl:param name="work-dir" select="'../../output'"/>
  
  
  
  <!-- ################################################## --> 
<!--                                                    -->
<!-- ################################################## --> 
<xsl:template match="cc:base-pp" mode="make_xref">
	<xsl:variable name="bid" select="./@ref"/>
    <xsl:apply-templates select="//cc:cc-doc-ref[@id=$bid]" mode="make_xref"/>
  </xsl:template>


<!-- ################################################## --> 
<!--                                                    -->
<!-- ################################################## --> 
 <xsl:template match="cc:base-pp" mode="short">
	<xsl:variable name="bid" select="@ref"/>
	<xsl:apply-templates select="//cc:cc-doc-ref[@id=$bid]" mode="short"/>
  </xsl:template>


<!-- ################################################## --> 
<!--                                                    -->
<!-- ################################################## --> 
  <xsl:template match="cc:base-pp" mode="expanded">
	<xsl:variable name="bid" select="@ref"/>
	<xsl:apply-templates select="//cc:cc-doc-ref[@id=$bid]" mode="expanded"/>
  </xsl:template>


<!-- ################################################## --> 
<!--                                                    -->
<!-- ################################################## --> 
<!--  <xsl:template match="cc:base-pp[@name]" mode="short">
    <xsl:value-of select="@short"/><xsl:choose>
       <xsl:when test="cc:cPP">c</xsl:when>
       <xsl:otherwise><xsl:text> </xsl:text></xsl:otherwise>
    </xsl:choose>PP</xsl:template>
--->
<!-- ################################################## --> 
<!--                                                    -->
<!-- ################################################## --> 
<!--
  <xsl:template match="cc:base-pp[@name]" mode="expanded">
    <xsl:if test="cc:cPP">Collaborative<xsl:text> </xsl:text></xsl:if>
    Protection Profile for<xsl:text> </xsl:text>
    <xsl:choose>
       <xsl:when test="@plural"><xsl:value-of select="@plural"/></xsl:when>
       <xsl:otherwise><xsl:value-of select="@name"/></xsl:otherwise>
    </xsl:choose>
  </xsl:template>
--->
<!-- ################################################## --> 
<!--                                                    -->
<!-- ################################################## --> 
  <xsl:template match="htm:*[./cc:depends/@*=//cc:base-pp/@ref]">
    <div class="dependent"> The following content should be included if:
      <xsl:for-each select="cc:depends/@*">
	     <xsl:apply-template select="//cc:base-pp[@ref=current()]" mode="short"/>
<!--         <xsl:value-of select="//cc:base-pp[@ref=current()]/@name"/>   -->
      </xsl:for-each>
      is a base PP:
      <div name="base-dependent">
        <xsl:call-template name="handle-html"/>
      </div>
    </div>
  </xsl:template>

  <xsl:template match="cc:mod-sars">
    <xsl:apply-templates/>
  </xsl:template>

  
</xsl:stylesheet>
