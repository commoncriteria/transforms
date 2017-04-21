<?xml version="1.0" encoding="utf-8"?>
<!--
    Stylesheet for Protection Profile Schema
    Based on original work by Dennis Orth
    Subsequent modifications in support of US NIAP
-->

<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:co="http://common-criteria.rhcloud.com/ns/co"
  xmlns="http://www.w3.org/1999/xhtml"
  xmlns:htm="http://www.w3.org/1999/xhtml"
  version="1.0">

  <!-- very important, for special characters and umlauts iso8859-1-->
  <xsl:output method="html" encoding="UTF-8" indent="yes"/>

  <!-- Put all common templates into ppcommons.xsl -->
  <!-- They can be redefined/overridden  -->
  <xsl:include href="ppcommons.xsl"/>

  <xsl:template match="/co:ConfigAnnex">
    <!-- Start with !doctype preamble for valid (X)HTML document. -->
    <xsl:text disable-output-escaping='yes'>&lt;!DOCTYPE html&gt;&#xa;</xsl:text>
    <html xmlns="http://www.w3.org/1999/xhtml">
      <head>
	<xsl:element name="title">Configuration Annex to the
    <xsl:value-of select="co:ConfigAnnexReference/co:PPType"/> for
    <xsl:value-of select="co:ConfigAnnexReference/co:PPTechnology"/>
  </xsl:element>

        <script type="text/javascript">

        </script>

        <style type="text/css">
	  <xsl:call-template name="common_css"/>

          /*       { background-color: #FFFFFF; } */
          body{
              margin-left:8%;
              margin-right:8%;
              foreground:black;
          }
	  .figure{
              font-weight:bold;
	  }
          h1{
              page-break-before:always;
              text-align:left;
              font-size:200%;
              margin-top:2em;
              margin-bottom:2em;
              font-family:verdana, arial, helvetica, sans-serif;
              margin-bottom:1.0em;
          }
          h1.title{
              text-align:center;
          }
          h2{
              font-size:125%;
              border-bottom:solid 1px gray;
              margin-bottom:1.0em;
              margin-top:2em;
              margin-bottom:0.75em;
              font-family:verdana, arial, helvetica, sans-serif;
          }
          h3{
              font-size:110%;
              margin-bottom:0.25em;
              font-family:verdana, arial, helvetica, sans-serif;
          }
          h4{
              margin-left:0%;
              font-size:100%;
              margin-bottom:0.75em;
              font-family:verdana, arial, helvetica, sans-serif;
          }
          h5,
          h6{
              margin-left:6%;
              font-size:90%;
              margin-bottom:0.5em;
              font-family:verdana, arial, helvetica, sans-serif;
          }
          p{
              margin-bottom:0.6em;
              margin-top:0.2em;
          }
          pre{
              margin-bottom:0.5em;
              margin-top:0.25em;
              margin-left:3%;
              font-family:monospace;
              font-size:90%;
          }
          ul{
              margin-bottom:0.5em;
              margin-top:0.25em;
          }
          td{
              vertical-align:top;
          }
          dl{
              margin-bottom:0.5em;
              margin-top:0.25em;
          }
          dt{
              margin-top:0.7em;
              font-weight:bold;
              font-family:verdana, arial, helvetica, sans-serif;
          }

          a.linkref{
              font-family:verdana, arial, helvetica, sans-serif;
              font-size:90%;
          }

          *.simpleText{
              margin-left:10%;
          }
          *.propertyText{
              margin-left:10%;
              margin-top:0.2em;
              margin-bottom:0.2em
          }
          *.toc{
              background:#FFFFFF;
          }
          *.toc2{
              background:#FFFFFF;
          }

          div.toc{
              margin-left:8%;
              margin-bottom:4em;
              padding-bottom:0.75em;
              padding-top:1em;
              padding-left:2em;
              padding-right:2em;
          }

          h2.toc{
              border-bottom:none;
              margin-left:0%;
              margin-top:0em;
          }
          p.toc{
              margin-left:2em;
              margin-bottom:0.2em;
              margin-top:0.5em;
          }
          p.toc2{
              margin-left:5em;
              margin-bottom:0.1em;
              margin-top:0.1em;
          }
          table{
              margin:auto;
              margin-top:1em;
              border-collapse:collapse; /*border: 1px solid black;*/
          }
          td{
              text-align:left;
              padding:8px 8px;
          }
          th{
              padding:8px 8px;
          }
          tr.header{
              border-bottom:3px solid gray;
              padding:8px 8px;
              text-align:left;
              font-weight:bold; /*font-size: 90%; font-family: verdana, arial, helvetica, sans-serif; */
          }
          table tr:nth-child(2n+2){
              background-color:#F4F4F4;
          }
          div.center{
              display:block;
              margin-left:auto;
              margin-right:auto;
              text-align:center;
          }
          div.figure{
              display:block;
              margin-left:auto;
              margin-right:auto;
              text-align:center;
              margin-top:1em;
          }
          }


	</style>
      </head>
      <body onLoad="init()">

        <noscript>
          <h1
            style="text-align:center; border-style: dashed; border-width: medium; border-color: red;"
            >This page is best viewed with JavaScript enabled!</h1>
        </noscript>
          <img src="images/niaplogo.png" alt="NIAP" style="width:300;height:260"/>
          <h1>Configuration Annex</h1>
          <h1 style="nobold">to the</h1>
          <h1><xsl:value-of select="//co:ConfigAnnexReference/co:PPType"/> for
            <xsl:value-of select="//co:ConfigAnnexReference/co:PPTechnology"/>
          </h1>
          <hr/>
          <h2>Version: <xsl:value-of select="//co:ConfigAnnexReference/co:PPVersion"/></h2>
          <h2>Release: <xsl:value-of select="//co:ConfigAnnexReference/co:Release"/></h2>
          <br/>
          <h2><xsl:value-of select="//co:ConfigAnnexReference/co:PubDate"/></h2>

          <h2 style="page-break-before:always;"/>

        <!-- process each toplevel chapter -->
        <xsl:apply-templates select="//co:chapter"/>
      </body>
    </html>
  </xsl:template>

  <!-- templates for creating references -->
  <!-- Assumes element with matching @id has a @title. -->
  <xsl:template match="co:xref">
    <xsl:variable name="linkend" select="translate(@linkend,$lower,$upper)"/>
    <xsl:variable name="linkendlower" select="translate(@linkend,$upper,$lower)"/>
    <xsl:element name="a">
      <xsl:attribute name="onclick">showTarget('<xsl:value-of select="$linkend"/>')</xsl:attribute>
      <xsl:attribute name="href">
        <xsl:text>#</xsl:text>
        <xsl:value-of select="$linkend"/>
      </xsl:attribute>
      <xsl:choose>
	<xsl:when test="//*[@id=$linkendlower]/@title">
	  <xsl:value-of select="//*[@id=$linkendlower]/@title"/>
	</xsl:when>
	<xsl:when test="//*[@id=$linkendlower]/@name">
	  <xsl:value-of select="//*[@id=$linkendlower]/@name"/>
	</xsl:when>
	<xsl:when test="//*[@id=$linkendlower]/co:term">
	  <xsl:value-of select="//*[@id=$linkendlower]/co:term"/>
	</xsl:when>
	<xsl:when test="//*/co:term[text()=$linkendlower]">
	  <xsl:value-of select="//*/co:term[text()=$linkendlower]/text()"/>
	</xsl:when>
	<xsl:otherwise>
	  <xsl:message>Cant find
	  <xsl:value-of select="$linkendlower"/>
	  </xsl:message>
	</xsl:otherwise>
      </xsl:choose>
    </xsl:element>
  </xsl:template>

  <xsl:template match="co:linkref">
    <xsl:call-template name="req-refs">
      <xsl:with-param name="class">linkref</xsl:with-param>
      <xsl:with-param name="req">
        <xsl:value-of select="translate(@linkend, $upper, $lower)"/>
      </xsl:with-param>
    </xsl:call-template>
  </xsl:template>

  <xsl:template match="co:secref">
    <xsl:variable name="linkend" select="@linkend"/>
    <xsl:element name="a">
      <xsl:attribute name="href">
        <xsl:text>#</xsl:text>
        <xsl:value-of select="$linkend"/>
      </xsl:attribute> Section <xsl:apply-templates select="//co:chapter" mode="secreflookup"
          ><xsl:with-param name="linkend" select="$linkend"/></xsl:apply-templates></xsl:element>
  </xsl:template>


  <xsl:template match="co:chapter | co:section | co:subsection" mode="secreflookup">
    <xsl:param name="linkend"/>
    <xsl:param name="prefix"/>
    <!-- make the identifier a letter or number as appropriate for appendix or chapter/section -->
    <xsl:variable name="pos">
      <xsl:number/>
    </xsl:variable>
    <xsl:if test="@id=$linkend">
      <xsl:value-of select="concat($prefix,$pos)"/>
    </xsl:if>
    <xsl:if test="./co:chapter | ./co:section | ./co:subsection">
      <xsl:apply-templates mode="secreflookup"
        select="./co:chapter | ./co:section | ./co:subsection">
        <xsl:with-param name="linkend" select="$linkend"/>
        <xsl:with-param name="prefix" select="concat($prefix,$pos,'.')"/>
      </xsl:apply-templates>
    </xsl:if>
  </xsl:template>

  <xsl:template match="co:cite">
    <xsl:variable name="linkend" select="@linkend"/>
    <xsl:element name="a">
      <xsl:attribute name="href">
        <xsl:text>#</xsl:text>
        <xsl:value-of select="$linkend"/>
      </xsl:attribute>
      <xsl:text>[</xsl:text>
      <xsl:value-of select="//co:bibliography/co:entry[@id=$linkend]/co:tag"/>
      <xsl:text>]</xsl:text>
    </xsl:element>
  </xsl:template>





</xsl:stylesheet>
