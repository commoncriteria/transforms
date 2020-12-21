<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:cc="https://niap-ccevs.org/cc/v1"
  xmlns="http://www.w3.org/1999/xhtml"
  xmlns:htm="http://www.w3.org/1999/xhtml"
  version="1.0">

<!--
    Stylesheet library for Protection Profile Schema
    Handles use-cases.
-->

  <!-- ############### -->
  <!--                 -->
  <!-- ############### -->
  <xsl:template match="cc:usecases">
    <dl>
      <xsl:for-each select="cc:usecase">
        <dt> [USE CASE <xsl:value-of select="position()"/>] <xsl:value-of select="@title"/> </dt>
        <dd>
          <xsl:apply-templates select="cc:description"/>
          <xsl:if test="cc:config"><p>
            For a the list of appropriate selections and acceptable assignment 
            values for this configuration, see <a href="#appendix-{@id}" class="dynref"></a>.
          </p></xsl:if>
        </dd>
      </xsl:for-each>
    </dl>
  </xsl:template>

  <!-- ############### -->
  <!--                 -->
  <!-- ############### -->
  <xsl:template name="use-case-appendix">
    <xsl:if test="//cc:usecase/cc:config">
      <h1 id="use-case-appendix" class="indexable" data-level="A">Use Case Templates</h1>
      <xsl:for-each select="//cc:usecase[cc:config]">
        <h2 id="appendix-{@id}" class="indexable" data-level="2">
          <xsl:value-of select="@title"/>
       </h2>
       <xsl:for-each select="cc:config">
          <xsl:call-template name="use-case-and"/>
       </xsl:for-each>
      </xsl:for-each>
    </xsl:if>
  </xsl:template>


  <!-- ############### -->
  <!--                 -->
  <!-- ############### -->
  <xsl:template match="cc:and" mode="use-case" name="use-case-and">
    <xsl:apply-templates mode="use-case"/>
  </xsl:template>

  <!-- ############### -->
  <!--                 -->
  <!-- ############### -->
   <xsl:template match="cc:or" mode="use-case">
    <table class="uc_table_or" style="border: 1px solid black">
      <tr> <td style="white-space: nowrap;" rowspan="{count(cc:*)+1}">OR</td><td style="display:none"></td></tr>
      <xsl:for-each select="cc:*">
        <tr><td style="width: 99%"><xsl:apply-templates select="." mode="use-case"/></td></tr>
      </xsl:for-each>
    </table>
  </xsl:template>
 

  <!-- ############### -->
  <!--                 -->
  <!-- ############### -->
  <xsl:template match="cc:*[@id]" mode="handle-ancestors">
    <xsl:param name="prev-id"/> 
    <xsl:message>Prev-id is <xsl:value-of select="$prev-id"/></xsl:message>
    <xsl:if test="ancestor::cc:f-component[@status='optional' or @status='objective'] and not(ancestor::cc:f-component//@id=$prev-id)">
      Include <xsl:apply-templates select="ancestor::cc:f-component" mode="make_xref"/> in ST.<br/>
    </xsl:if>


    <xsl:if test="ancestor::cc:f-element and not(ancestor::cc:f-element//@id=$prev-id)">
      From <xsl:apply-templates select="ancestor::cc:f-element" mode="make_xref"/>:<br/>
    </xsl:if>
    <xsl:if test="ancestor::cc:managment-function and not(ancestor::cc:management-function//@id=$prev-id)">
      From <xsl:apply-templates select="ancestor::cc:management-function" mode="make_xref"/>:<br/>
    </xsl:if>


    <xsl:for-each select="ancestor-or-self::cc:selectable">
      <xsl:if test="not(.//@id=$prev-id)">
        &#160;&#160;* select <xsl:apply-templates select="." mode="make_xref"/><br/>
      </xsl:if>
    </xsl:for-each>
  </xsl:template>

  <!-- ############### -->
  <!--                 -->
  <!-- ############### -->
  <xsl:template name="get-prev-id">
    <xsl:choose>
      <xsl:when test="preceding-sibling::cc:*[1]/cc:ref-id">
        <xsl:value-of select="preceding-sibling::cc:*[1]/cc:ref-id"/>
      </xsl:when>
      <xsl:otherwise><xsl:value-of select="preceding-sibling::cc:*[1]"/></xsl:otherwise>
    </xsl:choose>
  </xsl:template>
  <!-- ############### -->
  <!--                 -->
  <!-- ############### -->
  <xsl:template match="cc:guidance" mode="use-case">
    <xsl:variable name="ref-id" select="cc:ref-id[1]/text()"/>
    <xsl:choose>
      <xsl:when test="//cc:assignable/@id=$ref-id">
        <xsl:apply-templates select="//cc:*[@id=$ref-id]" mode="handle-ancestors">
          <xsl:with-param name="prev-id"><xsl:call-template name="get-prev-id"/></xsl:with-param>
        </xsl:apply-templates>
        &#160;&#160;* for <xsl:apply-templates select="//cc:assignable[@id=$ref-id]" mode="make_xref"/>, 
       <xsl:apply-templates/><br/>
      </xsl:when>
    </xsl:choose>
  </xsl:template>

 <!-- ############### -->
  <!--                 -->
  <!-- ############### -->
  <xsl:template match="cc:ref-id" mode="use-case">
    <xsl:variable name="ref-id" select="text()"/>
      <xsl:choose>
        <xsl:when test="//cc:selectable[@id=$ref-id]">
          <xsl:apply-templates select="//cc:*[@id=$ref-id]" mode="handle-ancestors">
            <xsl:with-param name="prev-id"><xsl:call-template name="get-prev-id"/></xsl:with-param>
          </xsl:apply-templates>
        </xsl:when>
        <xsl:when test="//cc:f-component[@id=$ref-id]">
          Include <xsl:apply-templates select="//cc:*[@id=$ref-id]" mode="make_xref"/> in the ST <br/>
        </xsl:when>
        <xsl:when test="//cc:management-function[@id=$ref-id]">
          <xsl:apply-templates select="//cc:*[@id=$ref-id]" mode="handle-ancestors">
            <xsl:with-param name="prev-id"><xsl:call-template name="get-prev-id"/></xsl:with-param>
          </xsl:apply-templates>
          Include
          <xsl:apply-templates select="//cc:management-function[@id=$ref-id]" mode="make_xref"/>
          in the ST<br/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:message> Failed to find <xsl:value-of select="$ref-id"/> in <xsl:call-template name="genPath"/></xsl:message>
        </xsl:otherwise>
      </xsl:choose>
  </xsl:template> 
</xsl:stylesheet>


