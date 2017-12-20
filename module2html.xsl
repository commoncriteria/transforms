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

  <xsl:import href="pp2html.xsl"/>

  <!--
      Eat all assurance activities
      We might just move these totally off to the SDs.
  -->
  <xsl:template match="cc:aactivity"/>
  <xsl:template name="opt_text"/>
</xsl:stylesheet>
