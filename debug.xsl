<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<!--#####################################
    This file is where debug templates 
	should go.
    #####################################-->


<!--#####################################
    This template should construct a path
	for the node it is applied to.
	It was copied from 
    https://stackoverflow.com/questions/953197/how-do-you-output-the-current-element-path-in-xslt
    #####################################-->
  <xsl:template name="genPath">
    <xsl:param name="prevPath"/>
    <xsl:variable name="currPath" select="concat('/',name(),'[',
      count(preceding-sibling::*[name() = name(current())])+1,']','|',substring(text(),0,10),'|',$prevPath)"/>
    <xsl:for-each select="parent::*">
      <xsl:call-template name="genPath">
        <xsl:with-param name="prevPath" select="$currPath"/>
      </xsl:call-template>
    </xsl:for-each>
    <xsl:if test="not(parent::*)">
      <xsl:value-of select="$currPath"/>      
    </xsl:if>
  </xsl:template>

</xsl:stylesheet>
