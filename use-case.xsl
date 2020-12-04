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
        <dt> [USE CASE <xsl:value-of select="position()"/>] <xsl:value-of select="@title"/> 
        </dt>
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
         <table>
	   <xsl:apply-templates mode="use-case"/>
         </table>
       </xsl:for-each>
      </xsl:for-each>
    </xsl:if>
  </xsl:template>

  <!-- ############### -->
  <!--                 -->
  <!-- ############### -->
  <xsl:template match="cc:all-or-none" mode="use-case">
    <tr>
      <td>These selections must be selected (or not selected) <br/>
          as a group in their entirety</td>
      <td>
        <xsl:for-each select="cc:ref-id">
          <xsl:variable name="id" select="text()"/>
          From <xsl:apply-templates select="//cc:f-element[.//cc:selectable/@id=$id]" mode="getId"/>
          choose <xsl:apply-templates select="//cc:selectable[@id=$id]"/><br/>
        </xsl:for-each>
      </td>
    </tr>
  </xsl:template>

  <!-- ############### -->
  <!--                 -->
  <!-- ############### -->
  <xsl:template match="cc:same-req" mode="use-case">
     <xsl:variable name="first" select="cc:ref-id[1]/text()"/>
     <tr>  
       <td><xsl:apply-templates select="//cc:f-element[.//cc:selectable/@id=$first]" mode="getId"/></td>
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
 <xsl:template match="cc:assign-hint" mode="use-case">
   <xsl:variable name="ref-id" select="cc:ref-id[1]/text()"/>
   <xsl:choose><xsl:when test="parent::cc:config">
     <tr>  
       <td><xsl:apply-templates select="//cc:f-element[.//cc:assignable/@id=$ref-id]" mode="getId"/>:
              <xsl:apply-templates select="//cc:management-function[.//@id=$ref-id]" mode="getId"/></td>
       <td>Include in ST. <xsl:apply-templates/></td>
     </tr>
   </xsl:when></xsl:choose>
 </xsl:template>

  <!-- ############### -->
  <!--                 -->
  <!-- ############### -->
  <xsl:template match="cc:free-text" mode="use-case">
      <tr>
        <td><xsl:apply-templates select="cc:obj"/></td>
        <td><xsl:apply-templates select="cc:act"/></td>
      </tr>
  </xsl:template>  


 <!-- ############### -->
  <!--                 -->
  <!-- ############### -->
  <xsl:template match="cc:ref-id" mode="use-case">
    <xsl:variable name="ref-id" select="text()"/>
    <tr>
      <xsl:choose>
        <xsl:when test="//cc:selectable[@id=$ref-id]">
          <td><xsl:apply-templates select="//cc:f-element[.//cc:selectable/@id=$ref-id]" mode="getId"/>:  
              <xsl:apply-templates select="//cc:management-function[.//@id=$ref-id]" mode="getId"/></td>
          <td>
             <xsl:if test="//cc:f-component[@status='optional' and .//@id=$ref-id] or //cc:f-component[@status='objective' and .//@id=$ref-id]"> Include in the ST </xsl:if> 
  
             <xsl:if test="parent::cc:not">DO NOT </xsl:if>
          Select
          <span class='quote'><xsl:apply-templates select="//cc:selectable[@id=$ref-id]"/></span></td>
        </xsl:when>
        <xsl:when test="//cc:f-component[@id=$ref-id]">
          <td><xsl:apply-templates select="//cc:*[@id=$ref-id]" mode="getId"/></td>
          <td>Include in the ST</td>
        </xsl:when>
        <xsl:when test="//cc:management-function[@id=$ref-id]">
          <td><xsl:apply-templates select="//cc:f-element[.//cc:management-function/@id=$ref-id]" mode="getId"/>:
              <xsl:apply-templates select="//cc:management-function[@id=$ref-id]" mode="getId"/></td>
          <td>Include in the ST</td> 
        </xsl:when>
        <xsl:otherwise>
          <xsl:message> Failed to find <xsl:value-of select="$ref-id"/> in <xsl:call-template name="genPath"/></xsl:message>
        </xsl:otherwise>
      </xsl:choose>
    </tr>
 </xsl:template> 
</xsl:stylesheet>


