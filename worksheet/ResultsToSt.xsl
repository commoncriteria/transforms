<?xml version="1.0" encoding="utf-8"?>
<!--
    Stylesheet for Protection Profile Schema
    Based on original work by Dennis Orth
    Subsequent modifications in support of US NIAP
-->

<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:cc="https://niap-ccevs.org/cc/v1"
  xmlns="http://www.w3.org/1999/xhtml"
  xmlns:htm="http://www.w3.org/1999/xhtml"
  version="1.0">

  <!-- very important, for special characters and umlauts iso8859-1-->
  <xsl:output method="html" encoding="UTF-8" indent="yes"/>


  <xsl:template match="/cc:PP">
  <html xmlns="http://www.w3.org/1999/xhtml">
    <head>
      <xsl:element name="title"><xsl:value-of select="//cc:PPTitle"/></xsl:element>
    </head>
    <body>
      <xsl:apply-templates select="//cc:section[@id='SFRs']"/>
      <xsl:apply-templates select="//cc:section[@id='SARs']"/>
    </body>
  </html>
  </xsl:template>

  <xsl:template match="cc:f-component[@disabled='yes']"/>
  <xsl:template match="cc:a-component[@disabled='yes']"/>


  <xsl:template match="cc:f-component|cc:a-component">
    <h4><xsl:value-of select="@id"/></h4>
  </xsl:template>

  <xsl:template match="cc:section">
    This section specifies the <xsl:value-of select="@id"/> for the TOE.
    <xsl:apply-templates />
  </xsl:template>



  
  <!-- Consume all comments -->
  <xsl:template match="comment()"/>

  <!-- Consume all processing-instructions -->
  <xsl:template match="processing-instruction()"/>

  
</xsl:stylesheet>
