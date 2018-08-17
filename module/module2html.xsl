<?xml version="1.0" encoding="utf-8"?>

<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:cc="https://niap-ccevs.org/cc/v1"
  xmlns="http://www.w3.org/1999/xhtml"
  xmlns:htm="http://www.w3.org/1999/xhtml"
  version="1.0">

  <xsl:import href="../pp2html.xsl"/>

  <xsl:output method="xml" encoding="UTF-8"/>

  <xsl:param name="tmpdir"/>
  
<!-- ################################################## -->
<!--                   MODULE Section                   -->
<!-- ################################################## -->
  <xsl:template match="/cc:Module//cc:chapter[@title='Security Requirements']">
    <h1 id="{@id}" class="indexable" data-level="1"><xsl:value-of select="@title"/></h1>
    <xsl:call-template name="secrectext"/>
    <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="/cc:Module//cc:*[@title='Consistency Rationale']">
    <h1 id="{@id}" class="indexable" data-level="1"><xsl:value-of select="@title"/></h1>
    <xsl:for-each select="//cc:base-pp">
      <xsl:variable name="base" select="."/>

      <h2 id="conrat-{@short}" class="indexable" data-level="2">
	<xsl:value-of select="@name"/> Protection Profile
      </h2>
      <h3 id="contoe-{@short}" class="indexable" data-level="3">
	Consistency of TOE Type
      </h3>

      <xsl:apply-templates select="./cc:con-toe"/>
      <h3 id="consecprob-{@short}" class="indexable" data-level="3">
	Consistency of Security Problem Definition
      </h3>
      The threats defined by this PP-Module (see section 3.1) supplement those defined in the
      <xsl:value-of select="@short"/> PP as follows:
      <xsl:apply-templates select="./cc:con-sec-prob"/>
      <table><tr><th>PP-Module Threat</th><th>Consistency Rationale</th></tr>
      <xsl:for-each select="//cc:threat">
	<xsl:variable name="tid" select="@id"/>
	<tr>
	  <td><xsl:value-of select="@id"/></td>
	  <td><xsl:choose>
	    <xsl:when test="$base/cc:threat-mod[@id=$tid]">
	      <xsl:apply-templates select="$base/cc:threat-mod[@id=$tid]"/>
	    </xsl:when>
	    <xsl:otherwise>
	      <!-- Can only go one element deep here -->
	      <xsl:apply-templates select="cc:consistency-rationale/node()">
		<xsl:with-param name="base" select="$base/@short"/>
	      </xsl:apply-templates>
	    </xsl:otherwise>
	  </xsl:choose></td>
	</tr>
      </xsl:for-each>
      </table>


      <h3 id="conobj-{@short}" class="indexable" data-level="3">
	Consistency of Objectives
      </h3>
      <xsl:apply-templates select="./cc:con-obj"/>
      <h3 id="conreq-{@short}" class="indexable" data-level="3">
	Consistency of Requirements
      </h3>
      <xsl:apply-templates select="./cc:con-req"/>
    </xsl:for-each>
  </xsl:template>


  <!-- ################################################## -->
  <xsl:template match="cc:base-pp">
    <h2 id="{@short}" class="indexable" data-level="2">
      <xsl:value-of select="@short"/> 
      PP Security Functional Requirements Direction
    </h2>
In a PP-Configuration the includes  <xsl:value-of select="@name"/> PP, the TOE is expected to rely on some of the security functions implemented by the <xsl:value-of select="@product"/> as a whole and evaluated against the Base-PP.
The following sections describe any modifications that the ST author must make to the SFRs
defined in the Base-PP in addition to what is mandated by section 5.4.

    <xsl:element name="h2">
      <xsl:attribute name="id">unmodsfr-<xsl:value-of select="../cc:base/@short"></xsl:value-of></xsl:attribute>
      <xsl:attribute name="class">indexable</xsl:attribute>
      <xsl:attribute name="data-level">3</xsl:attribute>
      Unmodified SFRs
    </xsl:element>
The SFRs listed in this section are defined in the <xsl:value-of select="../cc:base/@short"/> PP and are relevant to the secure operation of the
TOE. 
When testing the TOE, it is necessary to ensure these SFRs are tested specifically in
conjunction with the <xsl:value-of select="//cc:Module/@name"/> portion of the TOE.
The ST author may complete all selections and assignments in these SFRs without any
additional restrictions.
<ul>
    <!-- 
	 https is apparently not supported by xsltproc and http is not supported by github (where these files are resident).
	 I.E the following does not work
    <xsl:for-each select="document('https://raw.githubusercontent.com/commoncriteria/application/76f9cb4fadb616087626e1bd589a74a3679ced06/input/application.xml')//:f-component"> 
	 Solution: Pre-processes the document and wget the bases and save them to a temporary directory with the filename being the index of the base.
    -->
    <xsl:variable name="redefsec" select="."/>
    <xsl:for-each select="document(concat($tmpdir,count(preceding-sibling::*),'.xml'))//cc:f-component">
      <xsl:variable name="baseid" select="@id"/>
      <xsl:if test="not($redefsec//cc:f-component[@id=$baseid])">
	<li><xsl:value-of select="translate(@id,$lower,$upper)"/></li>
      </xsl:if>
    </xsl:for-each>
</ul>
    <xsl:element name="h2">
      <xsl:attribute name="id">modsfr-<xsl:value-of select="../cc:base/@short"></xsl:value-of></xsl:attribute>
      <xsl:attribute name="class">indexable</xsl:attribute>
      <xsl:attribute name="data-level">3</xsl:attribute>
      Modified SFRs
    </xsl:element>
    <xsl:choose><xsl:when test="cc:modified-sfrs">
      The SFRs listed in this section are defined in the <xsl:value-of select="../cc:base-pp/@name"/> Protection Profile and relevant to the secure operation of the TOE.
    <xsl:apply-templates select="cc:modified-sfrs"/>
    </xsl:when>
    <xsl:otherwise>
      This module does not modify any SFRs defined by the <xsl:value-of select="../cc:base-pp/@name"/> Protection Profile.
    </xsl:otherwise>
    </xsl:choose>

    <xsl:element name="h2">
      <xsl:attribute name="id">addsfr-<xsl:value-of select="../cc:base/@short"></xsl:value-of></xsl:attribute>
      <xsl:attribute name="class">indexable</xsl:attribute>
      <xsl:attribute name="data-level">3</xsl:attribute>
      Additional SFRs
    </xsl:element>
    <xsl:choose><xsl:when test="cc:additional-sfrs">
      This section defines additional SFRs that must be added to the TOE boundary in order to implement the functionality in any PP-Configuration where the <xsl:value-of select="../cc:base-pp/@name"/> Protection Profile is claimed as the Base-PP.
      <xsl:apply-templates select="cc:additional-sfrs"/>
    </xsl:when>
    <xsl:otherwise>
This module does not define any additional SFRs for any PP-Configuration where the <xsl:value-of select="../cc:base-pp/@name"/> Protection Profile is claimed as the Base-PP.
    </xsl:otherwise>
    </xsl:choose>
  </xsl:template>


  <xsl:template match="cc:con-sec-problem">
    <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="cc:base-name">
    <xsl:param name="base"/>
    <xsl:value-of select="$base"/>
  </xsl:template>


  <!--
      Eat all assurance activities
  -->
  <xsl:template match="cc:aactivity"/>
  <xsl:template name="opt_text"/>
</xsl:stylesheet>
