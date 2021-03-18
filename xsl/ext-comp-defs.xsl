<?xsml version="!.0" encoding="utf-8"?>
<!--

FILE: ext-comp-defs.xsl

Contains transforms for extended component definitions

-->

<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
     xmlns="http://w3.org/1999/xhthml"
     xmlns:cc="https://niap-ccevs.org/cc/v1"
     version="1.0">

  <xsl:import href="debug.xsl"/>
<!-- ####################### -->
  <xsl:template name="ext-comp-defs">
    <h1 id="ext-comp-defs" class="indexable" data-level="A">Extended Component Definitions</h1>
	This appendix contains the definitions for all extended requirements specified in the PP-Module.

    <h2 id="ext-comp-defs-bg" class="indexable" data-level="2">Extended Components Table</h2>

	All extended components specified in the PP are listed in this table:

<table>
	<caption><b><xsl:call-template name="ctr-xsl">
          <xsl:with-param name="ctr-type">Table</xsl:with-param>
          <xsl:with-param name="id" select="t-ext-comp_map"/>
	 </xsl:call-template>: Extended Component Definitions</b></caption>
  <tr>
    <th>Functional Class</th><th>Functional Components</th> </tr>
<!-- section is compatible with the new section styles b/c the new section style is not allowed to 
     for sections that directly contain f-components and a-components -->
<xsl:call-template name="RecursiveGrouping"><xsl:with-param name="list" select="//cc:section[cc:ext-comp-def]"/></xsl:call-template>
</table>
    <h2 id="ext-comp-defs-bg" class="indexable" data-level="2">Extended Component Definitions</h2>
    <xsl:for-each select="//cc:ext-comp-def">
      <xsl:variable name="famId"><xsl:value-of select="translate(@fam-id,$upper,$lower)"/></xsl:variable>
      <h3><xsl:value-of select="@fam-id"/> <xsl:text> </xsl:text>
          <xsl:value-of select="@title"/> </h3>
      <xsl:choose>
        <xsl:when test="cc:fam-behavior">
          <h3>Family Behavior</h3>
          <div> <xsl:apply-templates select="cc:fam-behavior"/> </div>
          <!-- Select all f-components that are not new and not a modified-sfr -->
          <xsl:variable name="dcount"
            select="count(//cc:f-component[starts-with(@cc-id, $famId) and not(@notnew)][not(ancestor::cc:modified-sfrs) and (cc:comp-lev)])"/>
<!--
          <xsl:element name="svg" namespace="http://www.w3.org/2000/svg">
              <xsl:attribute name="style">
                <xsl:value-of select="concat('max-height:', 20*$dcount+10,'px ;')"/>
              </xsl:attribute>
-->
          <svg xmlns="http://www.w3.org/2000/svg" style="{concat('max-height: ', 20*$dcount+10, 'px;')}">
              <xsl:call-template name="drawbox">
                <xsl:with-param name="ybase" select="20*floor($dcount div 2)"/>
                <xsl:with-param name="boxtext" select="@fam-id"/>
              </xsl:call-template>
              <xsl:for-each select="//cc:f-component[starts-with(@cc-id, $famId)and not(@notnew)][not(ancestor::cc:modified-sfrs) and (cc:comp-lev)]">
                <xsl:variable name="box_text"><!--
                  --><xsl:value-of select="translate(@cc-id,$lower,$upper)"/><!--
                  --><xsl:if test="@iteration">/<xsl:value-of select="@iteration"/></xsl:if></xsl:variable>
                <xsl:call-template name="drawbox">
                  <xsl:with-param name="ybase" select="( position() - 1)* 20"/>
                  <xsl:with-param name="boxtext" select="$box_text"/>
                  <xsl:with-param name="xbase" select="230"/>
                  <xsl:with-param name="ymid" select="20*floor($dcount div 2)"/>
                </xsl:call-template>
              </xsl:for-each>
          </svg>
<!--          </xsl:element> -->
        </xsl:when>
        <xsl:otherwise>
          <xsl:apply-templates select="cc:mod-def"/>
        </xsl:otherwise>
      </xsl:choose>
      <xsl:for-each select="//cc:f-component[starts-with(@cc-id, $famId) and not(@notnew)][not(ancestor::cc:modified-sfrs) and (cc:comp-lev)]">
         <xsl:variable name="upId"><xsl:apply-templates select="." mode="getId"/></xsl:variable>
         <h3>Component Leveling</h3>
         <p><xsl:value-of select="$upId"/>,
             <xsl:value-of select="@name"/>,
             <xsl:apply-templates select="cc:comp-lev" mode="reveal"/>
         </p>
         <h3>Management: <xsl:value-of select="$upId"/></h3>
         <p><xsl:if test="not(cc:management)">There are no management functions foreseen.</xsl:if>
            <xsl:apply-templates select="cc:management" mode="reveal"/>
         </p>

         <h3>Audit: <xsl:value-of select="$upId"/></h3>
         <p><xsl:if test="not(cc:audit)">There are no audit events foreseen.</xsl:if>
            <xsl:apply-templates select="cc:audit" mode="reveal"/>
         </p>
         <h3><xsl:value-of select="$upId"/> <xsl:text> </xsl:text><xsl:value-of select="@name"/>
         </h3>
         <p>Hierarchical to: <xsl:if test="not(cc:heirarchical-to)">No other components.</xsl:if>
            <xsl:apply-templates select="cc:heirarchical-to" mode="reveal"/>
         </p>
         <p>Dependencies to: <xsl:if test="not(cc:dependencies)">No dependencies.</xsl:if>
            <xsl:apply-templates select="cc:dependencies" mode="reveal"/>
         </p>

         <xsl:for-each select="cc:f-element">
            <xsl:variable name="reqid"><xsl:apply-templates select="." mode="getId"/></xsl:variable>
            <h3> <xsl:value-of select="translate($reqid, $lower,$upper)"/> </h3><br/>
                 <xsl:choose>
                    <xsl:when test="cc:ext-comp-def-title">
                       <xsl:apply-templates select="cc:ext-comp-def-title/cc:title"/>
                    </xsl:when>
                    <xsl:when test="document('SFRs.xml')//cc:sfr[@cc-id=$reqid]">
                       <xsl:apply-templates select="document('SFRs.xml')//cc:sfr[@cc-id=$reqid]/cc:title"/>
                    </xsl:when>
                    <xsl:otherwise>
                       <xsl:if test="cc:title//@id"><xsl:message>
                          WARNING: Since <xsl:value-of select="$reqid"/> has an 'id' attribute in a descendant node in the title, you probably need to define an alternative 'ext-comp-def-title'.
                       </xsl:message></xsl:if>
                       <xsl:apply-templates select="cc:title"/>
                    </xsl:otherwise>
                </xsl:choose>
         </xsl:for-each>
      </xsl:for-each>
    </xsl:for-each>
  </xsl:template>

<!-- ####################### -->
<!-- ####################### -->
 <xsl:template name="RecursiveGrouping">
  <xsl:param name="list"/>

  <!-- Selecting the first author name as group identifier and the group itself-->
  <xsl:variable name="group-identifier" select="$list[1]/@title"/>
  <xsl:variable name="group" select="$list[@title=$group-identifier]"/>

  <!-- Do some work for the group -->
  <tr> <td><xsl:value-of select="$group-identifier"/></td>
       <td>
         <xsl:for-each select="//cc:section[@title=$group-identifier]/cc:ext-comp-def"><xsl:sort select="@fam-id"/>
           <xsl:value-of select="translate(@fam-id,lower,upper)"/><xsl:text> </xsl:text><xsl:value-of select="@title"/><br/>
         </xsl:for-each>
       </td>
  </tr>

    <!-- If there are other groups left, calls itself -->
    <xsl:if test="count($list)>count($group)">
      <xsl:call-template name="RecursiveGrouping">
        <xsl:with-param name="list" select="$list[not(@title=$group-identifier)]"/>
      </xsl:call-template>
    </xsl:if>
 </xsl:template>

<!-- ####################### -->
<!-- ####################### -->
  <xsl:template match="cc:consistency-rationale//cc:_">
    <xsl:param name="base"/>
    <xsl:if test="$base=''">
      <xsl:message>Unable to figure out the base name for the '_' wildcard at:
      <xsl:call-template name="genPath"/>
      This usually happens when an '_' element is buried in html. It must be right under
      consistency-rationale (sorry).
     </xsl:message>
    </xsl:if>
    <xsl:value-of select="$base"/>
  </xsl:template>

  <xsl:template name="drawbox">
    <xsl:param name="ybase"/>
    <xsl:param name="boxtext"/>
    <xsl:param name="xbase">0</xsl:param>
    <xsl:param name="ymid"/>
    <xsl:element name="text">
      <xsl:attribute name="x"><xsl:value-of select="$xbase + 4"/></xsl:attribute>
      <xsl:attribute name="fill">black</xsl:attribute>
      <xsl:attribute name="font-size">11</xsl:attribute>
      <xsl:attribute name="y"><xsl:value-of select="$ybase + 22"/></xsl:attribute>
      <xsl:value-of select="$boxtext"/>
    </xsl:element>
    <xsl:element name="rect">
      <xsl:attribute name="x"><xsl:value-of select="$xbase + 2"/></xsl:attribute>
      <xsl:attribute name="y"><xsl:value-of select="$ybase + 11"/></xsl:attribute>
      <xsl:attribute name="width">120</xsl:attribute>
      <xsl:attribute name="height">16</xsl:attribute>
      <xsl:attribute name="fill">none</xsl:attribute>
      <xsl:attribute name="stroke">black</xsl:attribute>
    </xsl:element>
    <xsl:if test="$xbase>0">
      <xsl:element name="line">
        <xsl:attribute name="x1">122</xsl:attribute> <!-- 2 more than the width above -->
        <xsl:attribute name="y1"><xsl:value-of select="$ymid + 17"/></xsl:attribute>
        <xsl:attribute name="x2"><xsl:value-of select="$xbase + 1"/></xsl:attribute>
        <xsl:attribute name="y2"><xsl:value-of select="$ybase + 17"/></xsl:attribute>
        <xsl:attribute name="stroke">black</xsl:attribute>
      </xsl:element>
    </xsl:if>

  </xsl:template>

  <!-- Hide this when we stumble on it -->
  <xsl:template match="cc:ext-comp-def|cc:ext-comp-def-title"/>
  <xsl:template match="cc:consistency-rationale|cc:comp-lev|cc:management|cc:audit|cc:heirarchical-to|cc:dependencies"/>
  <xsl:template match="cc:ext-comp-extra-pat"/>

  <xsl:template match="cc:*" mode="reveal">
     <xsl:apply-templates/>
  </xsl:template>



</xsl:stylesheet>

