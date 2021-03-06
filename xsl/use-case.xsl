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
      <tr> <td class="or_cell" rowspan="{count(cc:*)+1}">OR</td><td style="display:none"></td></tr>
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
    <xsl:param name="not"/>

    <xsl:variable name="sclass">uc_sel<xsl:if test="ancestor::cc:management-function"> uc_mf</xsl:if></xsl:variable>
     
    <xsl:if test="ancestor::cc:f-component[@status='optional' or @status='objective'] and not(ancestor::cc:f-component//@id=$prev-id)">
      <div class="uc_inc_fcomp">
      Include <xsl:apply-templates select="ancestor::cc:f-component" mode="make_xref"/> in ST.</div>
    </xsl:if>

    <xsl:if test="ancestor::cc:f-element and not(ancestor::cc:f-element//@id=$prev-id)">
      <div class="uc_from_fel">
      From <xsl:apply-templates select="ancestor::cc:f-element" mode="make_xref"/>:</div>
    </xsl:if>
    <xsl:if test="ancestor::cc:management-function and not(ancestor::cc:management-function//@id=$prev-id)">
      <xsl:choose>
        <xsl:when test="ancestor::cc:management-function/cc:M">
          <div class="uc_mf">From <xsl:apply-templates select="ancestor::cc:management-function" mode="make_xref"/>:</div>
        </xsl:when>
        <xsl:otherwise>
          <div class="uc_mf">Include <xsl:apply-templates select="ancestor::cc:management-function" mode="make_xref"/>
          in the ST and :</div>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:if>
    <xsl:choose>
      <xsl:when test="$not='1'">
         <xsl:for-each select="ancestor::cc:selectable">
          <xsl:if test="not(.//@id=$prev-id)">
            <div class="{$sclass}">* select <xsl:apply-templates select="." mode="make_xref"/></div>
          </xsl:if>
        </xsl:for-each>
      </xsl:when>
      <xsl:otherwise>
        <xsl:for-each select="ancestor-or-self::cc:selectable">
          <xsl:if test="not(.//@id=$prev-id)">
            <div class="{$sclass}">* select <xsl:apply-templates select="." mode="make_xref"/></div>
          </xsl:if>
        </xsl:for-each>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <!-- ############### -->
  <!--                 -->
  <!-- ############### -->
  <xsl:template name="get-prev-id">
    <xsl:if test="not(parent::cc:or)">
      <xsl:value-of select="preceding-sibling::cc:*[1]/descendant-or-self::cc:ref-id"/>
    </xsl:if>
  </xsl:template>
  <!-- ############### -->
  <!--                 -->
  <!-- ############### -->
  <xsl:template match="cc:guidance" mode="use-case">
    <xsl:variable name="ref-id" select="cc:ref-id[1]/text()"/>
    <xsl:variable name="sclass">uc_guide<xsl:if test="//cc:management-function//@id=$ref-id"> uc_mf</xsl:if></xsl:variable>
    <xsl:choose>
      <xsl:when test="//cc:assignable/@id=$ref-id">
        <xsl:apply-templates select="//cc:*[@id=$ref-id]" mode="handle-ancestors">
          <xsl:with-param name="prev-id"><xsl:call-template name="get-prev-id"/></xsl:with-param>
        </xsl:apply-templates>
 	<div class="{$sclass}">* for the <xsl:apply-templates select="//cc:assignable[@id=$ref-id]" mode="make_xref"/>, 
       <xsl:apply-templates/></div>
      </xsl:when>
    </xsl:choose>
  </xsl:template>

   <!-- ############### --> 
  <!--                 -->
  <!-- ############### -->
  <xsl:template match="cc:not[cc:ref-id/text()=//cc:threat/@id]" mode="use-case">
    <xsl:for-each select="cc:ref-id[text() = //cc:threat/@id]">
      <xsl:variable name="theid" select="text()"/>
      <xsl:apply-templates mode="make_xref" select="//cc:*[@id=$theid]"/> does not apply in this use case.
    </xsl:for-each>
  </xsl:template>
  

  <!-- ############### -->
  <!--                 -->
  <!-- ############### -->
  <xsl:template match="cc:not" mode="use-case">
    <xsl:variable name="ref-id" select="cc:ref-id[1]/text()"/>
    <xsl:apply-templates select="//cc:*[@id=$ref-id]" mode="handle-ancestors">
       <xsl:with-param name="prev-id"><xsl:call-template name="get-prev-id"/></xsl:with-param>
       <xsl:with-param name="not" select="'1'"/>
    </xsl:apply-templates>
    <div class="uc_not">Choose something other than: 
      <xsl:for-each select="cc:ref-id">
        <xsl:variable name="ref" select="text()"/>
        <div class="uc_not_sel">* <xsl:apply-templates select="//cc:selectable[@id=$ref]" mode="make_xref"/></div>
      </xsl:for-each>
    </div>
  </xsl:template>


  <!-- ############### -->
  <!--                 -->
  <!-- ############### -->
  <xsl:template match="cc:doc" mode="use-case">
    <xsl:variable name="docpath"><xsl:value-of select="concat($work-dir,'/',@ref)"/>.xml</xsl:variable>
    <xsl:variable name="docurl"><xsl:value-of select="//cc:*[@id=current()/@ref]/cc:url/text()"/></xsl:variable>
    <xsl:variable name="name"><xsl:value-of select="document($docpath)//cc:PPTitle"/><xsl:if test="not(document($docpath)//cc:PPTitle)">PP-Module for <xsl:value-of select="document($docpath)/cc:Module/@name"/></xsl:if></xsl:variable>
   
    <div class="uc_inc_pkg"> From the <a href="{$docurl}"><xsl:value-of select="$name"/></a>: </div>
    <xsl:for-each select="cc:ref-id">
      <xsl:call-template name="handle-ref-ext"> 
        <xsl:with-param name="ref-id" select="text()"/>
        <xsl:with-param name="root" select="document($docpath)/cc:*"/>
      </xsl:call-template>
    </xsl:for-each>
  </xsl:template>

  <!-- ############### -->
  <!--                 -->
  <!-- ############### -->
  <xsl:template name="handle-ref-ext">
    <xsl:param name="ref-id"/>
    <xsl:param name="root"/>

    <xsl:choose>
      <xsl:when test="$root//cc:selectable[@id=$ref-id]">
        <xsl:apply-templates select="$root//cc:*[@id=$ref-id]" mode="handle-ancestors">
          <xsl:with-param name="prev-id"><xsl:call-template name="get-prev-id"/></xsl:with-param>
        </xsl:apply-templates>
      </xsl:when>
      <xsl:when test="$root//cc:f-component[@id=$ref-id]">
        <div class="uc_inc_fcomp">Include <xsl:apply-templates select="$root//cc:*[@id=$ref-id]" mode="make_xref"/> in the ST </div>
      </xsl:when>
      <xsl:when test="$root//cc:management-function//@id=$ref-id">
        <xsl:apply-templates select="$root//cc:*[@id=$ref-id]" mode="handle-ancestors">
          <xsl:with-param name="prev-id"><xsl:call-template name="get-prev-id"/></xsl:with-param>
        </xsl:apply-templates>
        <div class="uc_mf">Include
        <xsl:apply-templates select="$root//cc:management-function[@id=$ref-id]" mode="make_xref"/>
        in the ST</div>
      </xsl:when>
      <xsl:otherwise>
        <xsl:message> Failed to find <xsl:value-of select="$ref-id"/> in <xsl:call-template name="genPath"/></xsl:message>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template> 
  
  <!-- ############### -->
  <!--                 -->
  <!-- ############### -->
<!--  <xsl:template match="cc:ref-id" mode="use-case">
    <xsl:call-template name="handle-ref">
      <xsl:with-param name="ref-id" select="text()"/>
    </xsl:call-template>
  </xsl:template>  -->

  
 <xsl:template match="cc:ref-id" mode="use-case">
   <xsl:variable name="ref-id-txt" select="text()"/>
    <xsl:choose>
      <xsl:when test="//cc:selectable[@id=$ref-id-txt]">
        <xsl:apply-templates select="//cc:*[@id=$ref-id-txt]" mode="handle-ancestors">
          <xsl:with-param name="prev-id"><xsl:call-template name="get-prev-id"/></xsl:with-param>
        </xsl:apply-templates>
      </xsl:when>
      <xsl:when test="//cc:f-component[@id=$ref-id-txt]">
        <div class="uc_inc_fcomp">Include <xsl:apply-templates select="//cc:*[@id=$ref-id-txt]" mode="make_xref"/> in the ST </div>
      </xsl:when>
      <xsl:when test="//cc:management-function//@id=$ref-id-txt">
        <xsl:apply-templates select="//cc:*[@id=$ref-id-txt]" mode="handle-ancestors">
          <xsl:with-param name="prev-id"><xsl:call-template name="get-prev-id"/></xsl:with-param>
        </xsl:apply-templates>
        <div class="uc_mf">Include
        <xsl:apply-templates select="//cc:management-function[@id=$ref-id-txt]" mode="make_xref"/>
        in the ST</div>
      </xsl:when>
      <xsl:otherwise>
        <xsl:message> Failed to find <xsl:value-of select="$ref-id-txt"/> in <xsl:call-template name="genPath"/> (use case or rule)</xsl:message>
        <xsl:if test="./@alt">
          <b><i><xsl:value-of select="./@alt"/></i></b>
        </xsl:if>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>
 
  
  
  <!-- ############### -->
  <!--                 -->
  <!-- ############### -->
  <xsl:template name="handle-ref">
    <xsl:param name="ref-id" select="text()"/>
    <xsl:choose>
      <xsl:when test="//cc:selectable[@id=$ref-id]">
        <xsl:apply-templates select="//cc:*[@id=$ref-id]" mode="handle-ancestors">
          <xsl:with-param name="prev-id"><xsl:call-template name="get-prev-id"/></xsl:with-param>
        </xsl:apply-templates>
      </xsl:when>
      <xsl:when test="//cc:f-component[@id=$ref-id]">
        <div class="uc_inc_fcomp">Include <xsl:apply-templates select="//cc:*[@id=$ref-id]" mode="make_xref"/> in the ST </div>
      </xsl:when>
      <xsl:when test="//cc:management-function//@id=$ref-id">
        <xsl:apply-templates select="//cc:*[@id=$ref-id]" mode="handle-ancestors">
          <xsl:with-param name="prev-id"><xsl:call-template name="get-prev-id"/></xsl:with-param>
        </xsl:apply-templates>
        <div class="uc_mf">Include
        <xsl:apply-templates select="//cc:management-function[@id=$ref-id]" mode="make_xref"/>
        in the ST</div>
      </xsl:when>
      <xsl:otherwise>
        <xsl:message> Failed to find <xsl:value-of select="$ref-id"/> in <xsl:call-template name="genPath"/></xsl:message>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template> 
</xsl:stylesheet>


