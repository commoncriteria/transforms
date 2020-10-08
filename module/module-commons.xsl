<?xml version="1.0" encoding="utf-8"?>

<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:cc="https://niap-ccevs.org/cc/v1"
  xmlns="http://www.w3.org/1999/xhtml"
  xmlns:htm="http://www.w3.org/1999/xhtml"
  version="1.0">

  <xsl:template match="cc:base-pp" mode="short">
    <xsl:value-of select="@short"/><xsl:choose>
       <xsl:when test="cc:cPP">c</xsl:when>
       <xsl:otherwise><xsl:text> </xsl:text></xsl:otherwise>
    </xsl:choose>PP</xsl:template>

  <xsl:template match="cc:base-pp" mode="expanded">
    <xsl:if test="cc:cPP">Collaborative<xsl:text> </xsl:text></xsl:if>
    <xsl:value-of select="@name"/> Protection Profile
  </xsl:template>
</xsl:stylesheet>
