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
         <xsl:apply-templates mode="use-case"/>
       </xsl:for-each>
      </xsl:for-each>
    </xsl:if>
  </xsl:template>


  <!-- ############### -->
  <!--                 -->
  <!-- ############### -->
  <xsl:template match="cc:and" mode="use-case">
    <xsl:apply-templates mode="use-case"/>
<!--
    <table class="uc_table_and" style="border: 1px solid black"><tr>
      <td> <xsl:apply-templates mode="use-case"/> </td>
    </tr></table>-->
  </xsl:template>

  <!-- ############### -->
  <!--                 -->
  <!-- ############### -->
   <xsl:template match="cc:or" mode="use-case">
    <table class="uc_table_or" style="border: 1px solid black">
      <tr> <td rowspan="{count(cc:*)+1}">OR</td><td style="display:none"></td></tr>
      <xsl:for-each select="cc:*">
        <tr><td><xsl:apply-templates select="." mode="use-case"/></td></tr>
      </xsl:for-each>
      
    </table>
  </xsl:template>
 
  <!-- ############### -->
  <!--                 -->
  <!-- ############### -->
<!--  <xsl:template match="cc:all-or-none" mode="use-case">
    <tr>
      <td>These selections must be selected (or not selected) <br/>
          as a group in their entirety</td>
      <td>
        <xsl:for-each select="cc:ref-id">
          <xsl:variable name="id" select="text()"/>
          From <xsl:apply-templates select="//cc:f-element[.//cc:selectable/@id=$id]" mode="make_xref"/>
          choose <xsl:apply-templates select="//cc:selectable[@id=$id]"/><br/>
        </xsl:for-each>
      </td>
    </tr>
  </xsl:template>
-->
  <!-- ############### -->
  <!--                 -->
  <!-- ############### -->
  <xsl:template match="cc:same-req" mode="use-case">
     <xsl:variable name="first" select="cc:ref-id[1]/text()"/>
     <tr>  
       <td><xsl:apply-templates select="//cc:f-element[.//cc:selectable/@id=$first]" mode="make_xref"/></td>
       <td>
         <xsl:for-each select="cc:*">
          <xsl:choose>
           <xsl:when test="name()='ref-id'">
             <xsl:variable name="ref-id" select="text()"/>
             Choose 
             <xsl:apply-templates select="//cc:selectable[@id=$ref-id]"/>
           </xsl:when>
           <xsl:when test="name()='not'">
              Choose a selection other than
              <ul> <xsl:for-each select="cc:ref-id">
                <xsl:variable name="ref-id" select="text()"/>
                <li><xsl:apply-templates select="//cc:selectable[@id=$ref-id]"/></li>
              </xsl:for-each></ul>
           </xsl:when>
          </xsl:choose>
           <br/>
         </xsl:for-each>
       </td>
     </tr>
  </xsl:template>


  <!-- ############### -->
  <!--                 -->
  <!-- ############### -->
  <xsl:template match="cc:*[@id]" mode="handle-ancestors">
    <xsl:param name="prev-id"/> 
    <xsl:message>Prev-id is <xsl:value-of select="$prev-id"/></xsl:message>
    <xsl:if test="ancestor::cc:f-component[@status='optional' or @status='objective']">
      Include <xsl:apply-templates select="ancestor::cc:f-component" mode="make_xref"/> in ST. <br/>
    </xsl:if>
    <xsl:if test="not(ancestor::cc:f-element//@id=$prev-id)">
      From <xsl:apply-templates select="ancestor::cc:f-element" mode="make_xref"/><br/>
    </xsl:if>
   
    <xsl:for-each select="ancestor-or-self::cc:selectable">
      select <xsl:apply-templates select="." mode="make_xref"/> <br/>
    </xsl:for-each>
  </xsl:template>

  <!-- ############### -->
  <!--                 -->
  <!-- ############### -->
 <xsl:template match="cc:guidance" mode="use-case">
   <xsl:variable name="ref-id" select="cc:ref-id[1]/text()"/>
   <xsl:choose>
     <xsl:when test="//cc:assignable/@id=$ref-id">
       <xsl:apply-templates select="//cc:*[@id=$ref-id]" mode="handle-ancestors"/>
        For <xsl:apply-templates select="$ref-id" mode="make_xref"/>, <xsl:apply-templates/> <br/>
     </xsl:when>
   </xsl:choose>
 </xsl:template>

  <!-- ############### -->
  <!--                 -->
  <!-- ############### -->
  <!--
  <xsl:template match="cc:free-text" mode="use-case">
      <tr>
        <td><xsl:apply-templates select="cc:obj"/></td>
        <td><xsl:apply-templates select="cc:act"/></td>
      </tr>
  </xsl:template>  
-->
 <!-- ############### -->
  <!--                 -->
  <!-- ############### -->
  <xsl:template match="cc:ref-id" mode="use-case">
    <xsl:variable name="ref-id" select="text()"/>
      <xsl:choose>
        <xsl:when test="//cc:selectable[@id=$ref-id]">
          <xsl:apply-templates select="//cc:*[@id=$ref-id]" mode="handle-ancestors">
             <xsl:with-param name="prev-id" select="preceding-sibling::cc:*[1]"/>
          </xsl:apply-templates>
<!--
          <xsl:apply-templates select="//cc:f-element[.//cc:selectable/@id=$ref-id]" mode="make_xref"/>:  
              <xsl:apply-templates select="//cc:management-function[.//@id=$ref-id]" mode="make_xref"/></td>
          <td>
             <xsl:if test="//cc:f-component[@status='optional' and .//@id=$ref-id] or //cc:f-component[@status='objective' and .//@id=$ref-id]"> Include in the ST </xsl:if> 
  
             <xsl:if test="parent::cc:not">DO NOT </xsl:if>
          Select
          <span class='quote'><xsl:apply-templates select="//cc:selectable[@id=$ref-id]"/></span></td>
-->
        </xsl:when>
        <xsl:when test="//cc:f-component[@id=$ref-id]">
          Include <xsl:apply-templates select="//cc:*[@id=$ref-id]" mode="make_xref"/> in the ST <br/>
        </xsl:when>
        <xsl:when test="//cc:management-function[@id=$ref-id]">
          Include 
          <xsl:apply-templates select="//cc:f-element[.//@id=$ref-id]" mode="make_xref"/>:
          <xsl:apply-templates select="//cc:management-function[@id=$ref-id]" mode="make_xref"/>
          in the ST<br/> 
        </xsl:when>
        <xsl:otherwise>
          <xsl:message> Failed to find <xsl:value-of select="$ref-id"/> in <xsl:call-template name="genPath"/></xsl:message>
        </xsl:otherwise>
      </xsl:choose>
 </xsl:template> 
</xsl:stylesheet>


