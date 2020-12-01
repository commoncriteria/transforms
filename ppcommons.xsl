<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:cc="https://niap-ccevs.org/cc/v1" xmlns:htm="http://www.w3.org/1999/xhtml">

  <!--##############################################
           Includes
      ##############################################-->
  <xsl:include href="js-content.xsl"/>
  <xsl:include href="css-content.xsl"/>

  <!--##############################################
           Parameters
      ##############################################-->
  <!-- Variable for selecting how much debugging we want -->
  <xsl:param name="debug" select="'v'"/>
  <xsl:param name="release" select="'draft'"/>
  <!--##############################################
           Constants
      ##############################################-->
  <!-- #Adds 3 non-breaking spaces -->
  <xsl:variable name="space3">&#160;&#160;&#160;</xsl:variable>

  <xsl:variable name="lower" select="'abcdefghijklmnopqrstuvwxyz'"/>
  <xsl:variable name="upper" select="'ABCDEFGHIJKLMNOPQRSTUVWXYZ'"/>

  <xsl:variable name="title"><xsl:choose>
      <xsl:when test="//cc:PPTitle"><xsl:value-of select="//cc:PPTitle"/></xsl:when>
      <xsl:otherwise>PP-Module for <xsl:value-of select="/cc:*/@target-products"/></xsl:otherwise>
  </xsl:choose></xsl:variable>

  <!-- ############################################################
           Gets the ID for the f-component or f-element
       ############################################################-->
  <xsl:template match="cc:f-component|cc:f-element|cc:f-component-decl" mode="getId">
    <xsl:variable name="iter"><xsl:choose>
      <xsl:when test="name()='f-component'"><xsl:value-of select="@iteration"/></xsl:when>
      <xsl:when test="name()='f-component-decl'"><xsl:value-of select="@iteration"/></xsl:when>
      <xsl:otherwise><xsl:value-of select="../@iteration"/></xsl:otherwise>
    </xsl:choose></xsl:variable>
    <xsl:variable name="baseID"><xsl:choose>
      <xsl:when test="name()='f-component'"><xsl:value-of select="@cc-id"/></xsl:when>
      <xsl:when test="name()='f-component-decl'"><xsl:value-of select="@cc-id"/></xsl:when>
      <xsl:otherwise><xsl:value-of select="../@cc-id"/></xsl:otherwise>
    </xsl:choose></xsl:variable>
    <xsl:value-of select="translate($baseID, $lower, $upper)"/>
    <xsl:if test="name()='f-element'">.<xsl:value-of select="count(preceding-sibling::cc:f-element)+1"/></xsl:if>
    <xsl:if test="not($iter='')">/<xsl:value-of select="$iter"/></xsl:if>
  </xsl:template>

  <!-- ############################################################
           Gets the ID for the a-component or a-element
       ############################################################-->
  <xsl:template match="cc:a-component|cc:a-element" mode="getId">
    <xsl:variable name="baseID"><xsl:choose>
      <xsl:when test="name()='a-component'"><xsl:value-of select="@cc-id"/></xsl:when>
      <xsl:otherwise><xsl:value-of select="../@cc-id"/></xsl:otherwise>
    </xsl:choose></xsl:variable>
    <xsl:value-of select="translate($baseID, $lower, $upper)"/>
    <xsl:if test="name()='a-element'">.<xsl:value-of select="count(preceding-sibling::cc:a-element)+1"/><xsl:value-of select="@type"/></xsl:if>
  </xsl:template>


 
  <!-- ############### -->
  <!--                 -->
  <!-- ############### -->
  <xsl:template match="cc:tech-terms">
    <xsl:param name="num" select="2"/>

    <h2 id='glossary' class='indexable' data-level='{$num}'>Terms</h2>
The following sections list Common Criteria and technology terms used in this document.
    <h3 id="cc-terms" class="indexable" data-level="{$num+1}">Common Criteria Terms</h3>
    <table>
      <xsl:for-each select="document('boilerplates.xml')//cc:cc-terms/cc:term[text()]">
        <xsl:sort select="@full"/>
        <xsl:call-template name="glossary-entry"/>
      </xsl:for-each>
    </table>
    <h3 id="tech-terms" class="indexable" data-level="{$num+1}">Technical Terms</h3>
    <table>
      <xsl:for-each select="cc:term[text()]">
        <xsl:sort select="@full"/>
        <xsl:call-template name="glossary-entry"/>
      </xsl:for-each>
    </table>
  </xsl:template>

  <!-- ############### -->
  <!--                 -->
  <!-- ############### -->
  <xsl:template name="glossary-entry">
      <tr>
        <xsl:variable name="term_id"><xsl:value-of select="translate(@full,' ','_')"/></xsl:variable>
        <td><div id="{$term_id}">
            <xsl:choose>
                <xsl:when test="@abbr"><xsl:value-of select="@full"/> (<xsl:value-of select="@abbr"/>)</xsl:when>
                <xsl:otherwise><xsl:value-of select="@full"/></xsl:otherwise>
            </xsl:choose>
        </div></td>
        <td><xsl:apply-templates/></td>
      </tr>
  </xsl:template>


  <!-- ############### -->
  <!--                 -->
  <!-- ############### -->
  <xsl:template match="cc:linkref">
    <xsl:variable name="linkend" select="@linkend"/>
    <xsl:if test="not(//*[@id=$linkend])">
      <xsl:message> Broken linked element at <xsl:value-of select="$linkend"/></xsl:message>
    </xsl:if>
    <xsl:choose>
      <xsl:when test="//cc:f-element[@id=$linkend]|//cc:a-element[@id=$linkend]">
          <xsl:variable name="id"><xsl:apply-templates select="//cc:*[@id=$linkend]" mode="getId"/></xsl:variable>
          <a class="linkref" href="#{$id}"><xsl:value-of select="concat(text(),$id)"/></a>
      </xsl:when>
      <xsl:otherwise><a class="linkref" href="#{$linkend}"><xsl:value-of select="text()"/><xsl:value-of select="$linkend"/></a></xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <!-- ############### -->
  <!--                 -->
  <!-- ############### -->
  <xsl:template match="cc:testlist">
    <ul>
      <xsl:apply-templates/>
    </ul>
  </xsl:template>

  <!-- ############### -->
  <!--                 -->
  <!-- ############### -->
  <xsl:template match="cc:test">
    <li>
      <b>Test <xsl:for-each select="ancestor::cc:test"><xsl:value-of
            select="count(preceding-sibling::cc:test) + 1"/>.</xsl:for-each><xsl:value-of
          select="count(preceding-sibling::cc:test) + 1"/>: </b>
      <xsl:apply-templates/>
    </li>
  </xsl:template>
  
  <!-- ############### -->
  <!--                 -->
<!-- ############### -->
<xsl:template match="cc:test-obj">
<div class="test-obj"><b>Objective:</b> <xsl:apply-templates/> </div>
  </xsl:template>
  
  <!-- ############### -->
  <!--                 -->
  <!-- ############### -->
  <xsl:template match="cc:evidence">
    <div class="evidence"><b>Evidence:</b> <xsl:apply-templates/> </div>
  </xsl:template>

   <!-- ############### -->
  <!--                 -->
  <!-- ############### -->
  <xsl:template name="references">
    <h1 id="biblio" class="indexable" data-level="A">References</h1>
    <table>
      <tr class='header'><th>Identifier</th><th>Title</th></tr>
      <xsl:apply-templates select="//cc:bibliography"/>
    </table>
  </xsl:template>

  <!-- ############### -->
  <!--                 -->
  <!-- ############### -->
  <xsl:template match="cc:componentsneeded">
    <table>
      <tr class='header'><th>Component</th><th>Explanation</th></tr>
      <xsl:apply-templates select="//cc:componentneeded"/>
    </table>
  </xsl:template>

  <!-- ############### -->
  <!--                 -->
  <!-- ############### -->
  <xsl:template match="cc:componentneeded">
    <tr>
        <td><xsl:apply-templates select="cc:componentid"/></td>
        <td><xsl:apply-templates select="cc:notes"/></td>
    </tr>
  </xsl:template>

  <!-- ############### -->
  <!--                 -->
  <!-- ############### -->
  <xsl:template match="cc:cc-entry">
<tr><td><span id='bibCC'> [CC] </span></td><td>Common Criteria for Information Technology Security Evaluation - <ul>
            <li><a href='http://www.commoncriteriaportal.org/files/ccfiles/CCPART1V3.1R5.pdf'>Part
                1: Introduction and General Model</a>, CCMB-2017-04-001, Version 3.1 Revision 5,
              April 2017.</li>
            <li><a href='http://www.commoncriteriaportal.org/files/ccfiles/CCPART2V3.1R5.pdf'>Part
                2: Security Functional Components</a>, CCMB-2017-04-002, Version 3.1 Revision 5,
              April 2017.</li>
            <li><a href='http://www.commoncriteriaportal.org/files/ccfiles/CCPART3V3.1R5.pdf'>Part
                3: Security Assurance Components</a>, CCMB-2017-04-003, Version 3.1 Revision 5,
              April 2017.</li>
          </ul></td></tr>
  </xsl:template>


  <!-- ############### -->
  <!--                 -->
  <!-- ############### -->
  <xsl:template match="cc:steplist">
    <ul>
      <xsl:apply-templates/>
    </ul>
  </xsl:template>

  <!-- Steps in a steplist -->
  <xsl:template match="cc:step">
    <li>
      <b>Step <xsl:for-each select="ancestor::cc:step"><xsl:value-of
            select="count(preceding-sibling::cc:step) + 1"/>.</xsl:for-each><xsl:value-of
          select="count(preceding-sibling::cc:step) + 1"/>: </b>
      <xsl:apply-templates/>
    </li>
  </xsl:template>

  <!-- Overloaded abbr here-->
  <xsl:template match="cc:abbr[@linkend]">
    <xsl:variable name="target" select="@linkend"/>
    <xsl:variable name="full" select="//cc:term[$target=@abbr]/@full|document('boilerplates.xml')//cc:cc-terms/cc:term[$target=@abbr]/@full"/>    
    <xsl:choose>
      <xsl:when test="//cc:term[$target=@abbr]/@full|document('boilerplates.xml')//cc:cc-terms/cc:term[$target=@abbr]/@full">
	<a class="abbr" href="#abbr_{@linkend}">
	  <abbr title="{$full}"><xsl:value-of select="@linkend"/></abbr>
	</a>
      </xsl:when>
      <xsl:otherwise>
	<xsl:message>Failed to find the abbreviation: <xsl:value-of select="@linkend"/> </xsl:message>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <!-- ############### -->
  <!--                 -->
  <!-- ############### -->
  <xsl:template match="cc:choice//cc:selectables">
    <xsl:for-each select="cc:selectable"><xsl:choose>
	     <xsl:when test="position() = 1"><xsl:apply-templates/></xsl:when>
         <xsl:when test="position() = last()"> or <xsl:apply-templates/></xsl:when>
         <xsl:otherwise>, <xsl:apply-templates/></xsl:otherwise>
    </xsl:choose></xsl:for-each>
  </xsl:template>

  <!-- -->
  <!-- Selectables template -->
  <!-- -->
  <xsl:template match="cc:selectables">[<b>selection</b>
    <xsl:if test="@exclusive">, choose one of</xsl:if><xsl:text>: </xsl:text>
    <!-- Selections are always 'atleastone -->
<!--    <xsl:if test="@atleastone">, at least one of</xsl:if>:  -->
    <xsl:choose>
    <xsl:when test="@linebreak='yes'">
    <ul>
    <xsl:for-each select="cc:selectable"><li><i><xsl:apply-templates/></i><xsl:call-template name="commaifnotlast"/></li></xsl:for-each>
    <!-- <p style="margin-left: 40px;"><i><xsl:apply-templates/></i><xsl:call-template name="commaifnotlast"/></p> -->
    </ul>
    </xsl:when>
    <xsl:when test="@linebreak='no'"><xsl:for-each select="cc:selectable"><i><xsl:apply-templates/></i><xsl:call-template name="commaifnotlast"/></xsl:for-each></xsl:when>
    <!-- If the selection has a nested selection -->
    <xsl:when test=".//cc:selectables"><ul><xsl:for-each select="cc:selectable"><li><i><xsl:apply-templates/></i><xsl:call-template name="commaifnotlast"/></li></xsl:for-each></ul></xsl:when>
   <xsl:otherwise><xsl:for-each select="cc:selectable"><i><xsl:apply-templates/></i><xsl:call-template name="commaifnotlast"/></xsl:for-each></xsl:otherwise>
  </xsl:choose>]</xsl:template>

  <!--
      Delineates a list with commas
  -->
  <xsl:template name="commaifnotlast"><xsl:if test="position() != last()"><xsl:text>, </xsl:text></xsl:if></xsl:template>

  <!-- ############### -->
  <!--                 -->
  <!-- ############### -->
  <xsl:template match="cc:assignable">[<b>assignment</b>: <span class="assignable-content"><xsl:apply-templates/></span>]</xsl:template>

  <!-- ############### -->
  <!--                 -->
  <!-- ############### -->
  <xsl:template match="cc:refinement"><span class="refinement"><xsl:apply-templates/></span></xsl:template>

  <!-- ############### -->
  <!--                 -->
  <!-- ############### -->
  <xsl:template match="cc:note">
    <div class="appnote">
      <span class="note-header"><xsl:choose>
        <xsl:when test="@role='application'">Application</xsl:when>
        <xsl:when test="@role='developer'">Developer</xsl:when>
        <xsl:otherwise><xsl:value-of select="@role"/></xsl:otherwise>
      </xsl:choose> Note: </span>
      <span class="note">
        <xsl:apply-templates/>
      </span>
    </div>
  </xsl:template>


  <!-- ############### -->
  <!--                 -->
  <!-- ############### -->
  <xsl:template match="cc:management-function-set">
    <table class="mfs" style="width: 100%;">
      <tr class="header">
        <td>#</td>
        <td>Management Function</td>
        <xsl:apply-templates select="./cc:manager"/>
      </tr>
      <xsl:apply-templates select="./cc:management-function"/>
    </table>
  </xsl:template>


  <!-- ############### -->
  <!--                 -->
  <!-- ############### -->
  <xsl:template match="cc:manager">
    <td> <xsl:apply-templates/> </td>
  </xsl:template>

  <!-- ############### -->
  <!--                 -->
  <!-- ############### -->
  <xsl:template match="cc:management-function">
    <tr id="{@id}">
      <td>
        <xsl:value-of select="count(preceding::cc:management-function)+1"/>
      </td>
      <td>
        <xsl:apply-templates select="cc:text"/>
      </td>
	<xsl:variable name="manfunc" select="."/>
	<xsl:for-each select="../cc:manager">
	  <xsl:variable name="id" select="@cid"/>
	  <td>
	    <xsl:choose>
	      <!-- If we have something for that role -->
	      <xsl:when test="$manfunc/*[@ref=$id]">
		<xsl:choose>
		  <!-- And it is explicit, put it in there -->
		  <xsl:when test="$manfunc/*[@ref=$id]/node()">
		    <xsl:apply-templates select="$manfunc/*[@ref=$id]/."/>
		  </xsl:when>
		  <xsl:otherwise>
		    <xsl:call-template name="make-management-value">
		      <xsl:with-param name="type"><xsl:value-of select="name($manfunc/*[@ref=$id])"/></xsl:with-param>
		    </xsl:call-template>
		  </xsl:otherwise>
		</xsl:choose>
	      </xsl:when>
	      <xsl:otherwise>
		<xsl:call-template name="make-management-value">
		  <xsl:with-param name="type"><xsl:value-of select='../@default'/></xsl:with-param>
		</xsl:call-template>
	      </xsl:otherwise>
	    </xsl:choose>
	  </td>
	</xsl:for-each>
    </tr>
  </xsl:template>


  <!-- ############### -->
  <!--                 -->
  <!-- ############### -->
  <xsl:template name="make-management-value">
    <xsl:param name="type"/>
    <xsl:choose>
      <xsl:when test="$type='O'"><div>O<span class="tooltiptext">Optional</span></div></xsl:when>
      <xsl:when test="$type='M'"><div>M<span class="tooltiptext">Mandatory</span></div></xsl:when>
      <xsl:when test="$type='_'"><div>-<span class="tooltiptext">N/A</span></div></xsl:when>
      <xsl:otherwise><xsl:message>DONTKNOWWHATIT IS:<xsl:value-of select="$type"/></xsl:message></xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <!--
      Template that makes a tool tip. Uses javascript
  -->
  <xsl:template name="make-tool-tip">
    <xsl:param name="tip"/>
    <span class="tooltiptext"><xsl:value-of select="$tip"/></span>
  </xsl:template>

  <!-- ############### -->
  <!--                 -->
  <!-- ############### -->
  <xsl:template match="cc:bibliography/cc:entry">
    <tr>
      <xsl:variable name='id'><xsl:value-of select="@id"/></xsl:variable>
      <xsl:for-each select="cc:*">
	<td><xsl:choose><xsl:when test="not(preceding-sibling::*)"><span id="{$id}"/>[<xsl:apply-templates/>]</xsl:when><xsl:otherwise><xsl:apply-templates/></xsl:otherwise></xsl:choose></td>
      </xsl:for-each>
    </tr>
  </xsl:template>



  <!--
       Change all htm tags to tags with no namespace.
       This should help the transition from output w/ polluted
       namespace to output all in htm namespace. For right now
       this is what we have.
  -->
  <xsl:template match="htm:*[./cc:depends]">
        <div class="dependent"> The following content should be included if:
           <ul> <xsl:for-each select="cc:depends">
              <li>
              <xsl:if test="@on='selection'">
                <xsl:variable name="uid" select="cc:ref-id[1]/text()"/>
                <xsl:choose><xsl:when test="//cc:f-element[.//cc:selectable/@id=$uid]">
                <xsl:for-each select="cc:ref-id">  
                  <xsl:variable name="qtid" select="text()"/>
                  "<xsl:apply-templates select="//cc:selectable[@id=$qtid]"/>"
                </xsl:for-each>
                   is selected from 
                   <xsl:apply-templates select="//cc:f-element[.//cc:selectable/@id=$uid]" mode="getId"/>
                </xsl:when>
                <xsl:otherwise>For 
                   <xsl:for-each select="cc:ref-id">
                     <xsl:variable name="tid" select="text()"/>
                     <xsl:if test="position()!=1">/</xsl:if>
                     <xsl:apply-templates select="//cc:selectable[./@id=$tid]"/>
                   </xsl:for-each> TOEs </xsl:otherwise></xsl:choose>
              </xsl:if> 
              <xsl:if test="@on='implements'">
                the TOE implements 
                <xsl:for-each select="cc:ref-id">
                  <xsl:variable name="ref-id" select="text()"/>
                  <xsl:if test="position()!=1">, </xsl:if>
                  "<xsl:value-of select="//cc:feature[@id=$ref-id]/@title"/>"
                </xsl:for-each>
              </xsl:if>
              <!-- This is a module piece... -->
              </li>
          </xsl:for-each> </ul>
          <div class="dependent-content">
            <xsl:call-template name="handle-html"/>
          </div>        
        </div>        
  </xsl:template>

  <!-- ############### -->
  <!--                 -->
  <!-- ############### -->
  <xsl:template match="htm:*" name="handle-html">
     <xsl:element name="{local-name()}">
      <!-- Copy all the attributes -->
      <xsl:for-each select="@*">
	<xsl:copy/>
      </xsl:for-each>
      <xsl:apply-templates/>
    </xsl:element>
  </xsl:template>

  <!-- Consume all comments -->
  <xsl:template match="comment()"/>

  <!-- Consume all processing-instructions -->
  <xsl:template match="processing-instruction()"/>

  <!-- Consume all of the following -->
  <xsl:template match="cc:audit-event|cc:depends"/>
  <!--
      Recursively copy and unwrap unmatched things (elements, attributes, text)
  -->
  <xsl:template match="@*|node()"><xsl:copy><xsl:apply-templates select="@*|node()"/></xsl:copy></xsl:template>

  <!--
       By default, quietly unwrap all cc elements that are otherwise unmatched
  -->
  <xsl:template match="cc:*">
    <xsl:if test="contains($debug,'vv')">
      <xsl:message> Unmatched CC tag: <xsl:call-template name="path"/></xsl:message>
    </xsl:if>
    <xsl:apply-templates/>
  </xsl:template>


  <!--##############################################
        Template for universal sanity checks.
      ##############################################-->
  <xsl:template name="sanity-checks">
    <xsl:if test="//cc:TSS[.=''] or //cc:Guidance[.=''] or //cc:Tests[.='']">
      <xsl:message>*****************************
**
** TSS, Guidance, and Tests tags no longer precede their content, but rather encapsulate it.  **
** The page at http://commoncriteria.github.io/Encapsulator.html may be helpful.              **
***************************** </xsl:message>
    </xsl:if>
    <xsl:for-each select="//@id">
       <xsl:variable name="id" select="."/>
       <xsl:if test="count(//*[@id=$id])>1">
         <xsl:message>Error: Detected multiple elements with an id of '<xsl:value-of select="$id"/>'.</xsl:message>
       </xsl:if>
    </xsl:for-each>
    <xsl:for-each select="//cc:ref-id">
	<xsl:variable name="refid" select="text()"/>
        <xsl:if test="count(//cc:*[@id=$refid])=0">
         <xsl:message>Error: Detected dangling ref-id to '<xsl:value-of select="$refid"/>'.</xsl:message>
        </xsl:if>
    </xsl:for-each>
    <xsl:for-each select="//cc:*[@ref-id]">
	<xsl:variable name="refid" select="@ref-id"/>
        <xsl:if test="count(//cc:*[@id=$refid])=0">
         <xsl:message>Error: Detected dangling ref-id to '<xsl:value-of select="$refid"/>' 
           for a <xsl:value-of select="name()"/>
           .
         </xsl:message>
        </xsl:if>
    </xsl:for-each>
   </xsl:template>


  <!--
      Templates associated with debugging follow.
  -->
  <xsl:template match="cc:inline-comment[@level='critical']">
    <xsl:if test="$release!='draft'">
      <xsl:message terminate="yes"> Must fix elements must be fixed before a release version can be
        generated: <xsl:value-of select="text()"/>
      </xsl:message>
    </xsl:if>
  </xsl:template>

  <!-- ############### -->
  <!--                 -->
  <!-- ############### -->
  <xsl:template match="cc:inline-comment">
    <xsl:choose>
      <xsl:when test="@linebreak='yes'">
        <xsl:element name="div">
          <xsl:attribute name="style">background-color: beige; color:<xsl:value-of select="@color"
            /></xsl:attribute>
          <xsl:value-of select="text()"/>
        </xsl:element>
      </xsl:when>
      <xsl:otherwise>
        <xsl:element name="span">
          <xsl:attribute name="style">background-color: beige; color:<xsl:value-of select="@color"
            /></xsl:attribute>
          <xsl:value-of select="text()"/>
        </xsl:element>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <!--#####################-->
  <!-- Debugging templates -->
  <!--#####################-->
  <xsl:template name="debug-2">
    <xsl:param name="msg"/>
    <xsl:if test="contains($debug, 'vv')">
      <xsl:message><xsl:value-of select="$msg"/></xsl:message>
    </xsl:if>
  </xsl:template>

  <!-- -->
  <xsl:template name="debug-1">
    <xsl:param name="msg"/>
    <xsl:if test="contains($debug, 'v')">
      <xsl:message><xsl:value-of select="$msg"/></xsl:message>
    </xsl:if>
  </xsl:template>

  <!-- Debugging function -->
  <xsl:template name="path">
    <xsl:for-each select="parent::*">
      <xsl:call-template name="path"/>
    </xsl:for-each>
    <xsl:value-of select="name()"/>
    <xsl:text>/</xsl:text>
  </xsl:template>

  <!-- ############### -->
  <!--                 -->
  <!-- ############### -->
  <xsl:template name="head">
      <head>
	<title><xsl:value-of select="$title"/></title>
        <xsl:call-template name="pp_js"/>
        <style type="text/css">
        <xsl:call-template name="pp_css"/>
	</style>
      </head>
  </xsl:template>


  <!-- ############### -->
  <!--                 -->
  <!-- ############### -->
  <xsl:template name="body-begin">
    <h1 class="title" style="page-break-before:auto;"><xsl:value-of select="$title"/></h1>
    <noscript>
      <h1 style="text-align:center; border-style: dashed; border-width: medium; border-color: red;"
          >This page is best viewed with JavaScript enabled!</h1>
    </noscript>
    <div class="center">
      <img src="images/niaplogo.png" alt="NIAP Logo"/> <br/>
	<!-- Might think about getting rid of this and just making it part of the foreword -->
      Version: <xsl:value-of select="//cc:ReferenceTable/cc:PPVersion"/><br/>
      <xsl:value-of select="//cc:ReferenceTable/cc:PPPubDate"/><br/>
      <b><xsl:value-of select="//cc:PPAuthor"/></b><br/>
    </div>
    <xsl:apply-templates select="//cc:foreword"/>

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
       </tr>
     </xsl:for-each>
    </table>
    <h2>Contents</h2>
    <div class="toc" id="toc"/>
  </xsl:template>

  <!-- ############### -->
  <!--            -->
  <xsl:template match="cc:no-link">
    <span class="no-link">
        <xsl:apply-templates/>
    </span>
  </xsl:template>


  <!-- ############### -->
  <!--            -->
  <xsl:template name="acronyms">
    <h1 id="acronyms" class="indexable" data-level="A">Acronyms</h1>
    <xsl:call-template name="acronym-table"/>
  </xsl:template>


  <!-- ############### -->
  <!--            -->
  <xsl:template match="cc:acronyms" name="acronym-table">
    <table>
      <tr class="header">
        <th>Acronym</th>
        <th>Meaning</th>
      </tr>
      <xsl:for-each select="//cc:tech-terms//cc:term[@abbr]|document('boilerplates.xml')//cc:cc-terms/cc:term[@abbr]">
        <xsl:sort select="@abbr"/>
        <tr>
            <td><span class="term" id="abbr_{@abbr}"><xsl:value-of select="@abbr"/></span></td>
            <td><span id="long_abbr_{@abbr}"><xsl:value-of select="@full"/></span></td>
       </tr>&#10;

      </xsl:for-each>
    </table>
  </xsl:template>

  
  <!-- ############### -->
  <!--            -->
  <xsl:template match="cc:cite">
    <xsl:variable name="linkend" select="@linkend"/>
    <a href="#{$linkend}">[<xsl:value-of select="//cc:bibliography/cc:entry[@id=$linkend]/cc:tag"/>]</a>
  </xsl:template>

</xsl:stylesheet>
