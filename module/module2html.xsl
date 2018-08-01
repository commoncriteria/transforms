<?xml version="1.0" encoding="utf-8"?>

<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:cc="https://niap-ccevs.org/cc/v1"
  xmlns="http://www.w3.org/1999/xhtml"
  xmlns:htm="http://www.w3.org/1999/xhtml"
  version="1.0">

  <xsl:import href="../pp2html.xsl"/>

  <xsl:output method="xml" encoding="UTF-8"/>



<!-- Redefine to remove all the things currently done by the Python post process script -->
<xsl:template name="init_js">
<xsl:text disable-output-escaping="yes">// &lt;![CDATA[
// Called on page load to parse URL parameters and perform actions on them.
function init(){
}
// ]]&gt;</xsl:text>
</xsl:template>




  <xsl:template match="cc:base-pp">
    <xsl:value-of select="/cc:*/@name"/> products are expected to rely on some of the security functions implemented by the application as a whole and evaluated against the Base-PP.
    The following sections describe any modifications that the ST author must make to the SFRs
    defined in the Base-PP in addition to what is mandated by section 5.4.
    <xsl:apply-templates/>
  </xsl:template>

  <xsl:template name='cc:modified-sfrs'>
    <h2>Modified SFRS</h2>
    <xsl:if test="modified-sfr">
      The SFRs listed in this section are defined in the <xsl:value-of select="../cc:base-pp/@name"/> and relevant to the secure operation of the email client.
    </xsl:if>
    <xsl:if test="not(modified-sfr)">
      This module does not modify any SFRs defined by the <xsl:value-of select="../cc:base-pp/@name"/>.
    </xsl:if>
  </xsl:template>
  <xsl:template name='cc:additional-sfrs'>

  </xsl:template>


  <!--
      Eat all assurance activities
  -->
  <xsl:template match="cc:aactivity"/>
  <xsl:template name="opt_text"/>
</xsl:stylesheet>
