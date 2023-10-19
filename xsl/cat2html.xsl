<?xml version="1.0" encoding="utf-8"?>
<!--
    Stylesheet for SFR Catalog Schema
    Based on original work by Dennis Orth
    Subsequent modifications in support of US NIAP

    FILE: cat2html.xsl
    This is the entry point for SFR Catalogs.
-->

<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:cc="https://niap-ccevs.org/cc/v1"
  xmlns:sec="https://niap-ccevs.org/cc/v1/section"
  xmlns="http://www.w3.org/1999/xhtml"
  xmlns:htm="http://www.w3.org/1999/xhtml"
  version="1.0">

  <!-- ############### -->
  <!--     INCLUDES     -->
  <!-- ############### -->
  <xsl:import href="ext-comp-defs.xsl"/>
  <xsl:import href="ppcommons.xsl"/>
  <xsl:import href="boilerplates.xsl"/>
  <xsl:import href="debug.xsl"/>
  <xsl:import href="audit.xsl"/>

 
  <!-- ############### -->
  <!--  PARAMETERS     -->
  <!-- ############### -->
  <xsl:param name="appendicize" select="''"/>
  <xsl:param name="release" select="''"/>
  <xsl:param name="work-dir" select="'../../output'"/>


  <!-- ############### -->
  <!--  SETTINGS       -->
  <!-- ############### -->
  <!-- very important, for special characters and umlauts iso8859-1-->
  <xsl:output method="xml" encoding="UTF-8"/>

 <!-- ############### -->
  <!--  TEMPLATES      -->
  <!-- ############### -->

  <!-- ############### -->
  <xsl:template match="/">
    <xsl:call-template name="sanity-checks"/>
    <!-- Start with !doctype preamble for valid (X)HTML document. -->
    <xsl:text disable-output-escaping='yes'>&lt;!DOCTYPE html&gt;&#xa;</xsl:text>
    <html xmlns="http://www.w3.org/1999/xhtml">
      <xsl:call-template name="head"/>
      <body onLoad="init()">
        <xsl:call-template name="cat-body-begin"/>
        <xsl:apply-templates select="cc:*"/>
      </body>
    </html>
  </xsl:template>

<!-- ############### -->
  <!--                 -->
  <!-- ############### -->
  <xsl:template name="cat-body-begin">

<!--
    <xsl:if test="//cc:comment">
      <div id="commmentbox-">
	<xsl:for-each select="//cc:comment">
	  <xsl:variable name="id"><xsl:apply-templates select="." mode="getId"/></xsl:variable>
	  <a href="#{$id}">Comment: <xsl:value-of select="$id"/></a><br/>
	</xsl:for-each>
      </div>
    </xsl:if>
-->      
    
	<!-- Title Page -->
    <h1 class="title" style="page-break-before:auto;"><xsl:value-of select="//cc:CatReference/cc:CatTitle"/></h1>
    <noscript>
		<h1 style="text-align:center; border-style: dashed; border-width: medium; border-color: red;"
          >This page is best viewed with JavaScript enabled!</h1>
    </noscript>
    <div class="center">
		<img style="max-width:100%;" src="images/cclogo.png" alt="CC Logo"/> <br/>
		<!-- Might think about getting rid of this and just making it part of the foreword -->
		<br/><br/>
		<p style="font-size:16px; "><b>Version: </b> <xsl:value-of select="//cc:CatReference/cc:CatVersion"/></p>
		<br/><br/>
		<p style="font-size:16px; "><b><xsl:value-of select="//cc:CatReference/cc:CatPubDate"/></b></p>
		<br/><br/>
		<p style="font-size:24px; "><b><xsl:value-of select="//cc:CatReference/cc:CatAuthor"/></b></p>
		<br/>
    </div>

	<!-- Revision History -->
    <h2 style="page-break-before:always;">Revision History</h2>
    <table>
		<tr class="header">
			<th>Version</th>
			<th>Date</th>
			<th>Comment</th>
		</tr>
		<xsl:for-each select="//cc:RevisionHistory/cc:entry">
			<tr>
				<td> <xsl:value-of select="cc:version"/> </td>
				<td> <xsl:value-of select="cc:date"/> </td>
				<td> <xsl:apply-templates select="cc:subject"/> </td>
			</tr><xsl:text>&#xa;</xsl:text>
		</xsl:for-each>
    </table>

	<!-- Table of contents: I assume this is auto-generated later. -->
    <h2>Contents</h2>
    <div class="toc" id="toc"/>
	
  </xsl:template>



	<!-- ############### -->
	<!--                 -->
	<!-- ############### -->
	<xsl:template match="cc:SFRCatalog">
		<xsl:apply-templates select="cc:section"/>
	</xsl:template>
	
	
	<!-- Terms -->
	<!-- Display terms in the intro, usually section 1.4 -->
	<xsl:template match="cc:cat-terms">
		<xsl:param name="num" select="2"/>
			<div class="no-link">
			<h2 id='glossary' class='indexable' data-level='{$num}'>Terms</h2>
			The following section lists terms used in this document.
			<table style="width: 100%">
				<xsl:for-each select="cc:term[text()]">
					<xsl:sort select="@full"/>
					<xsl:call-template name="glossary-entry"/>
				</xsl:for-each>
			</table>
		</div>
	</xsl:template>

-->
	
</xsl:stylesheet>


