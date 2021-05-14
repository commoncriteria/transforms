<?xml version="1.0" encoding="utf-8"?>
<!--
    Stylesheet for Protection Profile Schema
    Based on original work by Dennis Orth
    Subsequent modifications in support of US NIAP

    FILE: pp2html.xsl
    This is the entry point for Protection Profiles.
    It is also used as a library for modules (but not for the SD or the
    simplified and table forms). 
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
  <xsl:import href="use-case.xsl"/>
  <xsl:import href="audit.xsl"/>

 
  <!-- ############### -->
  <!--  PARAMETERS     -->
  <!-- ############### -->
  <xsl:param name="appendicize" select="''"/>
  <xsl:param name="release" select="''"/>
  <xsl:param name="work-dir" select="'../../output'"/>

  <!-- ############### -->
  <!--  CONSTANTS      -->
  <!-- ############### -->
  <!-- In PPs th addressed-by element is at position 1, but in Modules its in position 2.-->
  <xsl:variable name="addressedByCol"><xsl:choose>
    <xsl:when test="/cc:Module">2</xsl:when>
    <xsl:otherwise>1</xsl:otherwise>
  </xsl:choose></xsl:variable>

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
        <xsl:call-template name="body-begin"/>
        <xsl:apply-templates select="cc:*"/>
      </body>
    </html>
  </xsl:template>

  <!-- ############### -->
  <!--                 -->
  <!-- ############### -->
  <xsl:template match="cc:PP|cc:Package">
    <xsl:apply-templates select="cc:section|sec:*"/>
    <!-- this handles the first appendices -->
    <xsl:call-template name="first-appendix"/>
    <xsl:if test="$appendicize='on'">
      <xsl:call-template name="app-reqs">
         <xsl:with-param name="type" select="'sel-based'"/>
         <xsl:with-param name="level" select="'A'"/>
         <xsl:with-param name="sublevel" select="'2'"/>
      </xsl:call-template>
    </xsl:if>
    <!-- This line means, match the first, which will handle adding the prolog and then handle all the ext-comp-defs-->
    <xsl:apply-templates select="//cc:ext-comp-def[not(preceding::cc:ext-comp-def or ancestor::cc:ext-comp-def)]" mode="app"/>
    <xsl:apply-templates select="cc:appendix[not(cc:bibliography)]"/>
    <xsl:apply-templates select="//cc:rule[not(preceding::cc:rule or ancestor::cc:rule)]"/>
<!--    <xsl:call-template name="rules-appendix"/>  -->
    <xsl:call-template name="use-case-appendix"/>  
    <xsl:call-template name="acronyms"/>
    <xsl:call-template name="bibliography"/>
  </xsl:template>
  
  <xsl:template match="//cc:rule[not(preceding::cc:rule or ancestor::cc:rule)]">
<!--  <xsl:template name="rules-appendix"><xsl:if test="//cc:rule">-->
     <h1 id="appendix-rules" class="indexable" data-level="A">Validation Guidelines</h1>
     	This appendix contains "rules" specified by the PP Authors that indicate whether certain selections
	  require the making of other selections in order for a Security Target to be valid. For example, selecting 
	  "HMAC-SHA-3-384" as a supported keyed-hash algorithm would require that "SHA-3-384" be selected
	  as a hash algorithm.<p/>
	  This appendix contains only such "rules" as have been defined by the PP Authors, and does not necessarily
	  represent all such dependencies in the document.<p/>
     <xsl:for-each select="//cc:rule">
       <h2 id="{@id}">
         Rule #<xsl:number count="cc:rule" level="any"/>
       </h2>
       <div>  <xsl:apply-templates select="cc:description"/></div>
       <xsl:apply-templates select="cc:if" mode="rule"/>
       <xsl:apply-templates select="cc:or" mode="rule"/>
       <xsl:apply-templates select="cc:then" mode="rule"/>
     </xsl:for-each>
  </xsl:template>

  <xsl:template match="cc:and" mode="use-case" name="use-case-and">
    <xsl:apply-templates mode="use-case"/>
  </xsl:template>

  <!-- ############### -->
  <!--                 -->
  <!-- ############### -->
   <xsl:template match="cc:or" mode="rule">
    <table class="uc_table_or" style="border: 1px solid black">
      <tr> <td class="or_cell" rowspan="{count(cc:*)+1}">OR</td><td style="display:none"></td></tr>
      <xsl:for-each select="cc:*">
        <tr><td style="width: 99%"><xsl:apply-templates select="." mode="use-case"/></td></tr>
      </xsl:for-each>
    </table>
  </xsl:template>

  <xsl:template match="cc:if" mode="rule">
    <table class="uc_table_or" style="border: 1px solid black">
      <tr> <td class="or_cell" rowspan="{count(cc:*)+1}">IF</td><td style="display:none"></td></tr>
      <xsl:for-each select="cc:*">
        <tr><td style="width: 99%"><xsl:apply-templates select="." mode="use-case"/></td></tr>
      </xsl:for-each>
    </table>
  </xsl:template>
	
  <xsl:template match="cc:then" mode="rule">
    <table class="uc_table_or" style="border: 1px solid black">
      <tr> <td class="or_cell" rowspan="{count(cc:*)+1}">THEN</td><td style="display:none"></td></tr>
      <xsl:for-each select="cc:*">
        <tr><td style="width: 99%"><xsl:apply-templates select="." mode="use-case"/></td></tr>
      </xsl:for-each>
    </table>
  </xsl:template>
	
	
  <!-- ############### -->
  <!--                 -->
  <!-- ############### -->
  <xsl:template name="bibliography">
    <h1 id="appendix-bibliography" class="indexable" data-level="A">Bibliography</h1>
    <table>
      <tr class="header"> <th>Identifier</th> <th>Title</th> </tr>
      <xsl:apply-templates mode="hook" select="."/>
      <xsl:for-each select="//cc:bibliography/cc:entry|document('boilerplates.xml')//*[@id='cc-docs']/cc:entry">
        <xsl:sort/>
        <tr>
          <td><span id="{@id}">[<xsl:value-of select="cc:tag"/>]</span></td>
          <td><xsl:apply-templates select="cc:description"/></td>
        </tr>
      </xsl:for-each>
    </table>
  </xsl:template>


  <!-- ############### -->
  <!--                 -->
  <!-- ############### -->
  <xsl:template name="make-section">
    <xsl:param name="title"/>
    <xsl:param name="id"/>
    <xsl:param name="depth" select="count(ancestor-or-self::cc:section) + count(ancestor-or-self::sec:*)+count(ancestor::cc:appendix)"/>

    <xsl:element name="h{$depth}">
      <xsl:attribute name="id"><xsl:value-of select="$id"/></xsl:attribute>
      <xsl:attribute name="class">indexable,h<xsl:value-of select="$depth"/></xsl:attribute>
      <xsl:attribute name="data-level"><xsl:value-of select="$depth"/></xsl:attribute>
      <xsl:value-of select="$title"/>
    </xsl:element>
    <xsl:apply-templates mode="hook" select="."/>
    <xsl:apply-templates />
  </xsl:template>


  <!-- ############### -->
  <!--                 -->
  <!-- ############### -->
  <xsl:template name="defs-with-notes">
    <xsl:variable name="class" select="local-name()"/>
    <dt class="{$class},defined" id="{@name}">
      <xsl:value-of select="@name"/>
    </dt>
    <dd>
      <xsl:apply-templates select="cc:description"/>
      <xsl:apply-templates select="cc:appnote"/>
    </dd>
 </xsl:template>
	
  <!-- ############### -->
  <!--                 -->
  <xsl:template match="cc:assumptions|cc:cclaims|cc:threats|cc:OSPs|cc:SOs|cc:SOEs">
    <xsl:choose> <xsl:when test="cc:*[cc:description]">
        <dl>
          <xsl:for-each select="cc:*[cc:description]">
            <xsl:call-template name="defs-with-notes"/>
          </xsl:for-each>
        </dl>
    </xsl:when><xsl:otherwise>
      This document does not define any additional <xsl:value-of select="local-name()"/>.
    </xsl:otherwise> </xsl:choose>
  </xsl:template>

  <!-- ############### -->
  <!-- Handle's the sections that appear if the optional 
       appendices appear (i.e. if this is the release version -->
  <!-- ############### -->
  <xsl:template match="cc:if-opt-app">
    <xsl:if test="$appendicize='on'">
      <xsl:apply-templates/>
    </xsl:if>
  </xsl:template>

   <!-- ############### -->
  <xsl:template match="cc:include-pkg[@short]" mode="show">
    <xsl:element name="a">
       <xsl:attribute name="href"><xsl:value-of select="@url"/></xsl:attribute>
       <xsl:value-of select="@name"/>
       <xsl:if test="@short"> (<xsl:value-of select="@short"/>)</xsl:if>
       Package, version <xsl:value-of select="@version"/>
    </xsl:element> Conformant
  </xsl:template>

  
  <!-- ############### -->
  <xsl:template match="cc:include-pkg[cc:raw-url]" mode="show">
    <xsl:variable name="path" select="concat($work-dir, '/', @id, '.xml')"/>
    <a href="{@url}">
       <xsl:value-of select="document($path)//cc:PPTitle"/>, 
       version <xsl:value-of select="document($path)//cc:PPVersion"/>
    </a> Conformant
  </xsl:template>

  <!-- ############### -->
  <!--                 -->
   <xsl:template match="cc:threat|cc:assumption|cc:OSP" mode="get-representation">
      <xsl:value-of select="@name"/>
   </xsl:template>

  <!-- ############### -->
  <!--                 -->
   <xsl:template match="cc:*[@title='Security Objectives Rationale']|sec:Security_Objectives_Rationale|sec:*[@title='Security Objectives Rationale']">
    <h2 id="{@id}" class="indexable,h2" data-level="2">Security Objectives Rationale</h2>   
    This section describes how the assumptions, threats, and organization 
    security policies map to the security objectives.
    <table>
      <caption><xsl:call-template name="ctr-xsl">
               <xsl:with-param name="ctr-type">Table</xsl:with-param>
	       <xsl:with-param name="id" select="'t-sec-obj-rat'"/>
	      </xsl:call-template>: Security Objectives Rationale</caption>
      <tr class="header">
        <td>Threat, Assumption, or OSP</td>
        <td>Security Objectives</td>
        <td>Rationale</td>
      </tr>
      <xsl:for-each 
          select="//cc:threat/cc:objective-refer | //cc:OSP/cc:objective-refer | //cc:assumption/cc:objective-refer">
        <tr>
          <xsl:if test="not(name(preceding-sibling::cc:*[1])='objective-refer')">
            <xsl:attribute name="class">major-row</xsl:attribute>
            <xsl:variable name="rowspan" select="count(../cc:objective-refer)"/>
            <td rowspan="{$rowspan}">
              <xsl:apply-templates select=".." mode="get-representation"/><br/>
            </td>
          </xsl:if>
          <td><xsl:value-of select="@ref"/></td>
          <td><xsl:apply-templates select="cc:rationale"/></td>
        </tr>
      </xsl:for-each>
    </table>
  </xsl:template>

  <!-- ############### -->
  <!--                 -->
  <xsl:template match="cc:a-component">
    <div class="comp" id="{translate(@cc-id, $lower, $upper)}">
      <h4>
        <xsl:value-of select="concat(translate(@cc-id, $lower, $upper), ' ')"/>
        <xsl:value-of select="@name"/>
      </h4>
      <xsl:apply-templates/><!-- a-elements don't output anything here -->
      <xsl:variable name="comp" select="."/>
      <xsl:for-each select="document('boilerplates.xml')//cc:empty[@id='a-group']/cc:a-stuff">
         <xsl:variable name="type" select="@type"/>
         <h4> <xsl:apply-templates/> elements: </h4>
         <xsl:apply-templates select="$comp/cc:a-element[@type=$type]" mode="a-element"/>
      </xsl:for-each> 
      <xsl:call-template name="f-comp-activities"/>
    </div>
  </xsl:template>


  <!-- ######################################## 
         This template handles f-components for PPs
         and packages when not appendisizing (i.e. NOT RELEASE)
       ######################################## -->
  <xsl:template match="cc:f-component[not(/cc:Module)]">
    <xsl:variable name="full_id"><xsl:apply-templates select="." mode="getId"/></xsl:variable>

    <div class="comp" id="{$full_id}">
      <h4><xsl:value-of select="concat($full_id, ' ', @name)"/></h4>
      <xsl:if test="@status='objective'">
        <div class="statustag">
          <i><b> This is an objective component.
          <xsl:if test="@targetdate">
            It is scheduled to be mandatory for products entering evaluation after
            <xsl:value-of select="@targetdate"/>.
          </xsl:if>
          </b></i>
        </div>
      </xsl:if>
      <xsl:if test="@status='sel-based'">
        <div class="statustag">
          <b><i>This is a selection-based component. Its inclusion depends upon selection from
          <xsl:for-each select="cc:depends/@*">
              <xsl:variable name="ref-id" select="."/>
              <xsl:choose><xsl:when test="../cc:external-doc">
                <xsl:variable name="doc_id" select="//cc:*[@id=current()/../cc:external-doc/@ref]/@id"/>
                <xsl:variable name="path" select="concat($work-dir,'/',$doc_id,'.xml')"/>
                <xsl:apply-templates mode="make_xref" select="document($path)//cc:f-element[.//@id=$ref-id]"/> from 
                <xsl:call-template name="make_xref"><xsl:with-param name="id" select="$doc_id"/></xsl:call-template>
              </xsl:when><xsl:otherwise>
                <xsl:apply-templates select="//cc:f-element[.//@id=$ref-id]" mode="getId"/>
              </xsl:otherwise></xsl:choose>
              <xsl:call-template name="commaifnotlast"/>
          </xsl:for-each>.
          </i></b>
        </div>
      </xsl:if>
      <xsl:if test="@status='feat-based'">
        <div class="statustag">
          <i><b>This is an implementation-based component.
                Its inclusion in depends on whether the TOE implements one or more of the following features:
                <ul>
                  <xsl:for-each select="cc:depends/@*">
                    <xsl:variable name="ref-id" select="text()"/>
                      <li><a href="#{@ref-id}"><xsl:value-of select="//cc:feature[@id=$ref-id]/@title"/></a></li>
                  </xsl:for-each>
                </ul>
                as described in Appendix A: Implementation-based Requirements.
        </b></i>
        </div>
      </xsl:if>
      <xsl:if test="@status='optional'">
        <div class="statustag">
          <i><b>This is an optional component. However, applied modules or packages might redefine it as mandatory.</b></i>
        </div>
      </xsl:if>
      <xsl:apply-templates/>
        <xsl:call-template name="f-comp-activities"/>
    </div>
  </xsl:template>

  <xsl:template match="/cc:Module//cc:f-component">
    <xsl:apply-templates select="." mode="appendicize-nofilter"/>
  </xsl:template>

  <!-- ############### -->
  <!--  F-components for release l      -->
  <!-- ############### -->
  <xsl:template match="cc:f-component" mode="appendicize">
  <!-- in appendicize mode, don't display objective/sel-based/optional/feat-based in main body-->
    <xsl:if test="not(@status)">
      <xsl:apply-templates select="." mode="appendicize-nofilter" />
    </xsl:if>
  </xsl:template>

  <!-- ############### -->
  <!--                 -->
  <!-- ############### -->
  <xsl:template match="cc:f-component" mode="appendicize-nofilter">
    <xsl:variable name="full_id"><xsl:apply-templates select="." mode="getId"/></xsl:variable>

    <div class="comp" id="{$full_id}">
      <h4><xsl:value-of select="concat($full_id, ' ', @name)"/></h4>

      <xsl:if test="@status='objective' and @targetdate">
        <div class="statustag">
          <i><b>
              This objective component is scheduled to be mandatory for
              products entering evaluation after
              <xsl:value-of select="@targetdate"/>.
          </b></i>
          </div>
      </xsl:if>
      <xsl:if test="@status='sel-based'">
        <div class="statustag">
          <b><i>The inclusion of this selection-based component depends upon a selection in
           <xsl:for-each select="cc:depends/@*">
              <xsl:variable name="ref-id" select="."/>
              <xsl:choose><xsl:when test="../cc:external-doc">
                <xsl:variable name="doc_id" select="//cc:*[@id=current()/../cc:external-doc/@ref]/@id"/>
                <xsl:variable name="path" select="concat($work-dir,'/',$doc_id,'.xml')"/>
                <xsl:apply-templates mode="make_xref" select="document($path)//cc:f-element[.//@id=$ref-id]"/> from 
                <xsl:call-template name="make_xref"><xsl:with-param name="id" select="$doc_id"/></xsl:call-template>
              </xsl:when><xsl:otherwise>
                <xsl:apply-templates select="//cc:f-element[.//@id=$ref-id]" mode="getId"/>
              </xsl:otherwise></xsl:choose>
              <xsl:call-template name="commaifnotlast"/>
          </xsl:for-each>.
 <!--             <xsl:for-each select="//cc:f-element[.//@id=current()/cc:depends/@*]">
                 <xsl:apply-templates mode="getId" select="."/><xsl:call-template name="commaifnotlast"/>
              </xsl:for-each>-->
            </i></b>
          </div>
      </xsl:if>
        <xsl:apply-templates/>
      <xsl:if test="not( (/cc:Module or //cc:cPP) and $release = 'final' )"><xsl:call-template name="f-comp-activities"/></xsl:if>
    </div>
  </xsl:template>


  <!--########################################-->
  <!--########################################-->
  <xsl:template match="cc:f-element" >
    <div class="element">
      <xsl:variable name="reqid"><xsl:apply-templates select="." mode="getId"/></xsl:variable>
      <div class="reqid" id="{$reqid}">
        <a href="#{$reqid}" class="abbr"><xsl:value-of select="$reqid"/></a>
      </div>
      <div class="reqdesc">
        <xsl:apply-templates select="cc:title"/>
        <xsl:apply-templates select="cc:note"/>
        <xsl:if test="//cc:rule[.//cc:ref-id/text()=current()//@id]">
          Validation Guidelines:<br/>
<!--          <p/>Selections in this requirement involve the following rule(s):<br/> -->
          <xsl:apply-templates select="//cc:rule[.//cc:ref-id/text()=current()//@id]" mode="use-case"/>
	</xsl:if>
      </div>
    </div>
  </xsl:template>
  <!--########################################-->
  <!--########################################-->
  <xsl:template match="cc:rule" mode="use-case">
	  <p/><b><a href="#{@id}">Rule #<xsl:number count="cc:rule" level="any"/></a></b>
	  <xsl:choose> <xsl:when test="cc:description">:
      <xsl:apply-templates select="cc:description"/><br/>
<!--      <div class="activity_pane hide"> <div class="activity_pane_header">
      <a onclick="toggle(this);return false;" href="#">
        <span class="activity_pane_label">Rule Definition </span>
        <span class="toggler"/>
      </a>
    </div>
    <div class="activity_pane_body">
      <i> <xsl:apply-templates select="cc:or" mode="use-case"/> </i>
    </div> </div>-->
      </xsl:when> <xsl:otherwise>
    <!--    <xsl:apply-templates mode="use-case"/> -->
      </xsl:otherwise> </xsl:choose>
  </xsl:template>

 <!-- ############### -->
  <!--                 -->
  <!-- ############### -->
   <xsl:template match="cc:a-element" mode="a-element">
    <div class="element">
      <xsl:variable name="type"><xsl:value-of select="@type"/></xsl:variable>
      <xsl:variable name="reqid"><xsl:apply-templates select="." mode="getId"/></xsl:variable>
      <div class="reqid" id="{$reqid}">
        <a href="#{$reqid}" class="abbr">
          <xsl:value-of select="$reqid"/>
        </a>
      </div>
      <div class="reqdesc">
        <xsl:apply-templates select="cc:title"/>
        <xsl:apply-templates select="cc:note"/>
      </div>
    </div>
  </xsl:template>


  <!-- ############### -->
  <!--                 -->
  <xsl:template match="cc:foreword">
    <div class="foreword">
      <h1 style="text-align: center">Foreword</h1>
      <xsl:apply-templates/>
    </div>
  </xsl:template>


  <!-- ############### -->
  <!--                 -->
  <xsl:template match="cc:title">
    <xsl:apply-templates/>
  </xsl:template>


  <!-- ############### -->
  <!--                 -->
  <!-- ############### -->
  <xsl:template match="cc:note/cc:aactivity">
    Evaluation Activity Note:<br/>
    <xsl:apply-templates/>
  </xsl:template> 


  <!-- ############### -->
  <!--                 -->
  <!-- ############### -->
  <xsl:template match="cc:management-function/cc:aactivity">
    <b><xsl:apply-templates select=".." mode="getId"/>
       <xsl:for-each select="cc:also">
         <xsl:variable name="ref-id" select="@ref-id"/>
         /<xsl:apply-templates select="//cc:management-function[$ref-id=@id]" mode="getId"/></xsl:for-each>
       <xsl:if test="not(../cc:M)"> [CONDITIONAL] </xsl:if>
    </b><br/>
    <xsl:apply-templates/>
  </xsl:template>
 

  <!-- ############### -->
  <!-- These items are just consumed without output when processed by 'apply-templates' in default mode.      -->
  <xsl:template match="cc:appendix[@title='Optional Requirements']"/>
  <xsl:template match="cc:appendix[@title='Selection-Based Requirements']"/>
  <xsl:template match="cc:appendix[@title='Objective Requirements']"/>
  <xsl:template match="cc:a-element"/>
  <xsl:template match="cc:ext-comp-def|cc:ext-comp-def-title"/>
  <xsl:template match="cc:consistency-rationale|cc:comp-lev|cc:management|cc:audit|cc:heirarchical-to|cc:dependencies"/>
  <xsl:template match="cc:ext-comp-extra-pat"/>
 
 <!-- ############### -->
  <!--                 -->
  <!-- Note: In the worksheet branch the ref-id of a depends tag is an attribute, but at some point that changed to a tag in the master.
       Of course, nobody tells me this so it took a while to debug.   -->
  <!-- TODO: Check the logic behind the ref-id: it only supports one ref-id right now.-->
    <xsl:template name="handle-features">
       <xsl:for-each select="//cc:implements/cc:feature">
          <xsl:variable name="fid"><xsl:value-of select="@id"/></xsl:variable>
          <xsl:variable name="oneIfApp">0<xsl:if test="$appendicize='on'">1</xsl:if></xsl:variable>
          <xsl:variable name="level" select="2+$oneIfApp"/>

          <h3 class="indexable" data-level="{$level}" id="{@id}"><xsl:value-of select="@title"/></h3>
          <xsl:apply-templates select="cc:description"/>
  	  <!-- First just output the name of the SFR associated with each feature.  -->
          <p>
	  If this is implemented by the TOE, the following requirements must be included in the ST:
            <ul> <xsl:for-each select="//cc:f-component[cc:depends/@*=$fid]"> 
	       <li><b><xsl:apply-templates select="." mode="getId"/></b></li>
	    </xsl:for-each></ul>
          </p>
          
	  <!-- Then each SFR in full. Note if an SFR is invoked by two features it will be listed twice. -->  
          <xsl:if test="$appendicize='on'">
             <xsl:for-each select="//cc:f-component/cc:depends[@*=$fid]/../..">
                <h3 id="{@id}-impl" class="indexable" data-level="{$level+1}"><xsl:value-of select="@title" /></h3>
                <xsl:apply-templates select="cc:f-component[cc:depends/@*=$fid]" mode="appendicize-nofilter"/>
             </xsl:for-each>
          </xsl:if>
        </xsl:for-each>
    </xsl:template>


  <!-- ############### -->
  <!--                 -->
  <!-- Edited to add references for these generated audit tables:
    - strictly optional = "at-optional"
    - objective = "at-objective"
    - sel based = "at-sel-based"
    - impl-dep = "at-impl-dep"  -->
    <xsl:template name="first-appendix">
        <xsl:choose>
            <xsl:when test="$appendicize='on'">
                <xsl:call-template name="opt_appendix"/>
                <xsl:call-template name="app-reqs">
                    <xsl:with-param name="type" select="'optional'"/>
                </xsl:call-template>

                <xsl:call-template name="app-reqs">
                    <xsl:with-param name="type" select="'objective'"/>
                </xsl:call-template>
            
                <xsl:call-template name="app-reqs">
                    <xsl:with-param name="type" select="'feat-based'"/>
                </xsl:call-template>
            </xsl:when>
            <xsl:otherwise>
                <h1 id="impl-reqs" class="indexable" data-level="A">Implementation-Dependent Requirements</h1>
                Implementation-Dependent Requirements <xsl:call-template name="imple_text"/>
                <xsl:call-template name="handle-features"/>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>

  <!-- ############### -->
  <!--   Appendix Requirements               -->
  <!-- ############### -->
  <xsl:template name="app-reqs">
    <xsl:param name="type"/>
    <xsl:param name="level" select="2"/>
    <xsl:param name="sublevel" select="3"/>
    
 <!--   <xsl:choose><xsl:when test="//cc:hide-empty-req-appendices"/><xsl:otherwise>-->
    <xsl:variable name="levelname"><xsl:choose>
      <xsl:when test="$level='A'">h1</xsl:when>
      <xsl:otherwise>h2</xsl:otherwise>
    </xsl:choose></xsl:variable>
    <xsl:variable name="nicename" select="document('boilerplates.xml')//cc:*[@tp=$type]/@nice"/>
 
    <xsl:element name="{$levelname}">
       <xsl:attribute name="id"><xsl:value-of select="concat($type,'-reqs')"/></xsl:attribute>
       <xsl:attribute name="class">indexable</xsl:attribute>
       <xsl:attribute name="data-level"><xsl:value-of select="$level"/></xsl:attribute>
       <xsl:value-of select="$nicename"/>  Requirements
    </xsl:element>
    <xsl:apply-templates select="document('boilerplates.xml')//cc:*[@tp=$type]/cc:description"/>
    <xsl:choose>
      <xsl:when test="count(//cc:f-component[@status=$type])=0">
         <p>This <xsl:call-template name="doctype-short"/> does not define any 
            <xsl:value-of select="$nicename"/> requirements.</p>
      </xsl:when>
      <xsl:otherwise> 
         <xsl:if test="//cc:pp-preferences/cc:audit-events-in-sfrs">
           <xsl:element name="h{$sublevel}">
              <xsl:attribute name="id"><xsl:value-of select="concat($type,'-reqs-audit')"/></xsl:attribute>
              <xsl:attribute name="class">indexable</xsl:attribute>
              <xsl:attribute name="data-level"><xsl:value-of select="$sublevel"/></xsl:attribute>
              Auditable Events for <xsl:value-of select="$nicename"/>  Requirements
           </xsl:element>
           
            <xsl:if test="/cc:Package">
              <xsl:apply-templates select="document('boilerplates.xml')//cc:*[@tp=$type]/cc:audit-table-explainer"/>
            </xsl:if>
			    
           <xsl:call-template name="audit-table">
                <xsl:with-param name="thistable" select="$type"/>
           </xsl:call-template> 
        </xsl:if>
        <xsl:choose>
          <xsl:when test="$type='feat-based'"><xsl:call-template name="handle-features"/></xsl:when>
          <xsl:otherwise> 
            <xsl:for-each select="//*[cc:f-component/@status = $type]">
              <xsl:element name="h{$sublevel}">
                <xsl:attribute name="id"><xsl:value-of select="concat(@id,'-obj')"/></xsl:attribute>
                <xsl:attribute name="class">indexable</xsl:attribute>
                <xsl:attribute name="data-level"><xsl:value-of select="$sublevel"/></xsl:attribute>
                <xsl:value-of select="@title"/>
              </xsl:element>
     <!--         <h3 id="{@id}-obj" class="indexable" data-level="3"><xsl:value-of select="@title" /></h3 -->
              <xsl:apply-templates select="cc:f-component[@status=$type]" mode="appendicize-nofilter"/>
            </xsl:for-each>
          </xsl:otherwise>
        </xsl:choose>
     </xsl:otherwise>
   </xsl:choose>
   <!-- </xsl:otherwise></xsl:choose> -->
 </xsl:template> 

 <!-- ############### -->
  <!--                 -->

  <xsl:template match="cc:appendix">
    <h1 id="{@id}" class="indexable" data-level="A"><xsl:value-of select="@title"/></h1> 
      <!-- insert SFRs for "special" appendices, if @id is one of the "special" ones-->
    <xsl:apply-templates select="." mode="hook"/>
    <xsl:apply-templates/>
  </xsl:template> 

  <!-- ######################### -->
  <!-- ######################### -->
  <xsl:template match="cc:section[cc:f-component]">
    <xsl:param name="lmod" select="'0'"/>

    <xsl:call-template name="section-with-fcomp">
      <xsl:with-param name="title" select="@title"/>
      <xsl:with-param name="id" select="@id"/>
      <xsl:with-param name="lmod" select="$lmod"/>
    </xsl:call-template>
  </xsl:template>

  <xsl:template match="sec:*[cc:f-component and @title]">
    <xsl:param name="lmod" select="'0'"/>

     <xsl:call-template name="section-with-fcomp">
      <xsl:with-param name="title" select="@title"/>
      <xsl:with-param name="id" select="local-name()"/>
      <xsl:with-param name="lmod" select="$lmod"/>
    </xsl:call-template>
  </xsl:template>
 
  <xsl:template match="sec:*[cc:f-component and not(@title)]">
    <xsl:param name="lmod" select="'0'"/>

    <xsl:call-template name="section-with-fcomp">
      <xsl:with-param name="title" select="translate(local-name(),'_',' ')"/>
      <xsl:with-param name="id" select="local-name()"/>
      <xsl:with-param name="lmod" select="$lmod"/>
    </xsl:call-template>
  </xsl:template>

  <xsl:template name="section-with-fcomp">
    <xsl:param name="title"/>
    <xsl:param name="id"/> 
    <xsl:param name="lmod"/>
  
    <!-- the "if" statement is to not display  headers when there are no
    subordinate mandatory components to display in the main body (when in "appendicize" mode) -->
    <xsl:if test="$appendicize!='on' or .//cc:f-component[not(@status)]">
      <h3 id="{$id}" class="indexable" data-level="{$lmod+count(ancestor::*)}">
        <xsl:value-of select="$title" />
      </h3>
      <xsl:apply-templates mode="hook" select="."/>
      <xsl:if test="$appendicize = 'on'">
        <xsl:apply-templates mode="appendicize" />
      </xsl:if>
      <xsl:if test="$appendicize != 'on'">
        <xsl:apply-templates />
      </xsl:if>
    </xsl:if>
  </xsl:template>


  <!-- ######################### -->
  <!-- ######################### -->
  <xsl:template match="cc:*[@id='obj_map']" mode="hook" name="obj-req-map">
    <p>The following rationale provides justification for each security objective for the TOE, 
    showing that the SFRs are suitable to meet and achieve the security objectives:<br/>
      <table>
        <caption><xsl:call-template name="ctr-xsl">
               <xsl:with-param name="ctr-type">Table</xsl:with-param>
	       <xsl:with-param name="id" select="'t-obj_map'"/>
		</xsl:call-template>: SFR Rationale</caption>
        <tr><th>OBJECTIVE</th><th>ADDRESSED BY</th><th>RATIONALE</th></tr>
        <xsl:for-each select="//cc:SO/cc:addressed-by">
          <tr>
           <xsl:if test="count(preceding-sibling::cc:*)=$addressedByCol">
             <xsl:attribute name="class">major-row</xsl:attribute>
             <xsl:variable name="rowspan" select="count(../cc:addressed-by)"/>
             <td rowspan="{$rowspan}">
               <xsl:value-of select="../@name"/><br/>
             </td>
           </xsl:if>
           <td><xsl:apply-templates/></td>
           <td><xsl:apply-templates select="following-sibling::cc:rationale[1]"/></td>
          </tr> 
        </xsl:for-each>
      </table>
    </p>
  </xsl:template>

 
  <!-- ############### -->
  <!--                 -->
  <xsl:template match="cc:ctr">
    <xsl:variable name="ctrtype"><xsl:choose>
        <xsl:when test="@ctr-type"><xsl:value-of select="@ctr-type"/></xsl:when>
        <xsl:otherwise><xsl:value-of select="@pre"/></xsl:otherwise></xsl:choose>
    </xsl:variable>

    <span class="ctr" data-myid="{@id}" data-counter-type="ct-{$ctrtype}" id="{@id}">
      <xsl:apply-templates select="." mode="getPre"/><xsl:text> </xsl:text>
      <span class="counter"><xsl:value-of select="@id"/></span>
      <xsl:apply-templates/>
    </span>
  </xsl:template>

  <!-- ############### -->
  <!--                 -->
  <!-- ############### -->
  <xsl:template name="ctr-xsl">
      <xsl:param name="ctr-type"/>
      <xsl:param name="id"/>

    <xsl:if test="$id=''">
      <xsl:message terminate="yes">Detected that a ctr's _id_ attribute is empty</xsl:message>
    </xsl:if>
    <span class="ctr" data-myid="{$id}" data-counter-type="ct-{$ctr-type}" id="{$id}">
<!--      <xsl:apply-templates select="." mode="getPre"/> -->
      <xsl:value-of select="$ctr-type"/><xsl:text> </xsl:text>
      <span  class="counter"><xsl:value-of select="$id"/></span>
<!--      <xsl:apply-templates/>-->
    </span>
  </xsl:template>
	
  <!-- ############### -->
  <!--                 -->
  <xsl:template match="cc:figure">
    <div class="figure" id="figure-{@id}">
      <img id="{@id}" src="{@entity}" width="{@width}" height="{@height}"/>
      <br/>
      <xsl:call-template name="make_ctr">
        <xsl:with-param name="id" select="@id"/>
        <xsl:with-param name="type" select="'ct-figure'"/>
        <xsl:with-param name="prefix"><xsl:apply-templates select="." mode="getPre"/></xsl:with-param>
      </xsl:call-template>:
      <xsl:value-of select="@title"/>
    </div>
  </xsl:template>


  <xsl:template name="make_ctr">
    <xsl:param name="id"/>
    <xsl:param name="type"/>
    <xsl:param name="prefix"/>

    <span class="ctr" data-myid="{$id}" data-counter-type="{$type}">
        <xsl:value-of select="$prefix"/> 
        <span class="counter"><xsl:value-of select="$id"/></span>
      </span>
  </xsl:template>



  <!-- ############### -->
  <!--                 -->
  <xsl:template match="cc:equation">
    <table><tr>
      <td id="{@id}">$$<xsl:apply-templates/>$$</td>
      <td style="vertical-align: middle; padding-left: 100px"><!--
          -->(<xsl:call-template name="make_ctr">
          <xsl:with-param name="id" select="@id"/>
          <xsl:with-param name="type" select="'equation'"/>
          <xsl:with-param name="prefix" select="''"/>
        </xsl:call-template>)</td>
    </tr></table>
  </xsl:template>


  <!-- ############### -->
  <!--                 -->
  <!-- <xsl:template match="cc:figure|cc:ctr" mode="getPre" name="getPre"> -->
  <xsl:template match="cc:figure|cc:ctr" mode="getPre" >
     <xsl:choose>
      <xsl:when test="@pre"><xsl:value-of select="@pre"/></xsl:when>
      <xsl:when test="local-name()='figure'"><xsl:text>Figure </xsl:text></xsl:when>
      <xsl:when test="@ctr-type"><xsl:value-of select="@ctr-type"/></xsl:when>
      <xsl:otherwise>Table </xsl:otherwise>
    </xsl:choose>
  </xsl:template>


  <!-- ############### -->
  <xsl:template match="cc:TSS|cc:Guidance|cc:KMD|cc:Tests">
    <div class="eacategory"><xsl:value-of select="local-name()"/></div>
    <xsl:apply-templates/>
  </xsl:template>

  <!-- ############### -->
  <xsl:template match="cc:management-function//cc:_">
    <xsl:choose>
      <xsl:when test="ancestor::cc:management-function[@id][1]/cc:also">
        Functions 
        <xsl:for-each select="ancestor::cc:*[@id][1]/cc:also">
          <xsl:variable name="ref" select="@ref-id"/>
          <xsl:apply-templates mode="getId" select="//cc:management-function[@ref=@ref-id]"/>,
        </xsl:for-each>
      </xsl:when>
      <xsl:otherwise>
        <xsl:apply-templates select="ancestor::cc:management-function[@id][1]" mode="getId"/> 
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

   <!-- ############## -->
  <xsl:template match="//sec:*[@title='Security Functional Requirements']">
    <xsl:call-template name="sfr"><xsl:with-param name="id" select="local-name()"/></xsl:call-template>
  </xsl:template>

  <xsl:template match="//cc:*[@title='Security Functional Requirements']">
    <xsl:call-template name="sfr"/>
  </xsl:template>

   <xsl:template match="/sec:Security_Functional_Requirements">
    <xsl:call-template name="sfr"><xsl:with-param name="id" select="Security_Functional_Requirements"/></xsl:call-template>
   </xsl:template>
  
  <xsl:template name="sfr">
     <xsl:param name="id" select="@id"/>
     <h2 id="{$id}" class="indexable" data-level="2">Security Functional Requirements</h2>
    <xsl:if test="/cc:*/@boilerplates='yes' and not(@boilerplate='no')">
       The Security Functional Requirements included in this section
       are derived from Part 2 of the Common Criteria for Information
       Technology Security Evaluation, <xsl:call-template name="verrev"/>,
       with additional extended functional components.
     </xsl:if>
     <xsl:apply-templates/>
     <xsl:if test="/cc:PP">
       <h3 id="obj-req-map" class="indexable" data-level="3">TOE Security Functional Requirements Rationale</h3>
       <xsl:call-template name="obj-req-map"/>
     </xsl:if>
  </xsl:template>

	
</xsl:stylesheet>


