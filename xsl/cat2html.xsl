<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:cc="https://niap-ccevs.org/cc/v1"
  xmlns:sec="https://niap-ccevs.org/cc/v1/section"
  xmlns="http://www.w3.org/1999/xhtml"
  xmlns:htm="http://www.w3.org/1999/xhtml"
  version="1.0">

  <!-- ################################################## -->
  <!--                   Imports                          -->
  <!-- ################################################## -->
  <xsl:import href="pp2html.xsl"/>

  <xsl:output method="xml" encoding="UTF-8"/>

  <!-- Directory where the base PPs currently reside (with apthe names 0.xml, 1.xml,...)-->
  <xsl:param name="basesdir"/>

  <!-- Value on whether this is the formal release build -->
  <xsl:param name="release" select="final"/>

  <!-- ################################################## -->
  <!--                   Templates Section                -->
  <!-- ################################################## -->
  <!-- ############### -->
  <!--   Top Module    -->
  <!-- ############### -->
  <xsl:template match="cc:SFRCatalog">
<!--    <xsl:apply-templates select="//*[@title='Introduction']|sec:Introduction"/>   -->
<!--    <xsl:apply-templates select="//*[@title='Conformance Claims']|sec:Conformance_Claims"/>  -->
<!--    <xsl:apply-templates select="//*[@title='Security Problem Definition']|sec:Security_Problem_Definition"/>  -->
<!--    <xsl:apply-templates select="//*[@title='Security Objectives']|sec:Security_Objectives"/>  -->
<!--    <xsl:apply-templates select="//*[@title='Security Requirements']|sec:Security_Requirements"/>   -->
    <xsl:apply-templates select="//*[@title='Security Functional Requirements']|sec:Security_Functional_Requirements"/>
<!--    <xsl:call-template name="mod-obj-req-map"/>   -->
    <!-- <xsl:call-template name="sars"/> -->
<!--    <xsl:call-template name="acronyms"/>  -->
<!--    <xsl:call-template name="bibliography"/>   -->
  </xsl:template>





</xsl:stylesheet>
