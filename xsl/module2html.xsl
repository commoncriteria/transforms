<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:cc="https://niap-ccevs.org/cc/v1"
  xmlns:sec="https://niap-ccevs.org/cc/v1/section"
  xmlns="http://www.w3.org/1999/xhtml"
  xmlns:htm="http://www.w3.org/1999/xhtml"
  version="1.0">

  <!-- ################################################## -->
  <!--                   Imports                          -->
  <!-- ################################################## -->
  <xsl:import href="pp2html.xsl"/>
  <xsl:import href="module-commons.xsl"/>


  <xsl:output method="xml" encoding="UTF-8"/>

  <!-- Directory where the base PPs currently reside (with apthe names 0.xml, 1.xml,...)-->
  <xsl:param name="basesdir"/>

  <!-- Value on whether this is the formal release build -->
  <xsl:param name="release" select="final"/>

  <xsl:variable name="doctype" select="mod"/>
  <!-- ################################################## -->
  <!--                   Templates Section                -->
  <!-- ################################################## -->
  <xsl:template match="cc:Module">
    <xsl:apply-templates select="//*[@title='Introduction']|sec:Introduction"/>
    <xsl:apply-templates select="//*[@title='Conformance Claims']|sec:Conformance_Claims"/>
    <xsl:apply-templates select="//*[@title='Security Problem Description']|sec:Security_Problem_Description"/>
    <xsl:apply-templates select="//*[@title='Security Objectives']|sec:Security_Objectives"/>
    <xsl:apply-templates select="//*[@title='Security Requirements']|sec:Security_Requirements"/>
    <xsl:call-template name="mod-obj-req-map"/>
    <xsl:call-template name="consistency-rationale"/>
    <xsl:call-template name="opt-sfrs"/>
    <xsl:call-template name="sel-sfrs"/>
    <xsl:call-template name="ext-comp-defs"/>
    <xsl:apply-templates select="//cc:appendix"/>
    <xsl:apply-templates select="//cc:bibliography"/>
    <xsl:call-template name="acronyms"/>
  </xsl:template>

  
 <!-- ############### -->
<!--   Overwrites template from pp2html.xsl -->
<!--            -->
   <xsl:template match="cc:threat|cc:assumption|cc:OSP" mode="get-representation">
      <xsl:value-of select="@name"/>
      <xsl:if test="cc:from"> (from <xsl:value-of select="cc:from/@base"/>)</xsl:if>
   </xsl:template>


  <xsl:template name="mod-obj-req-map">
    <h2 id="obj-req-map" class="indexable" data-level="2">TOE Security Functional Requirements Rationale</h2>
    <xsl:call-template name="obj-req-map"/>
  </xsl:template> 

  <xsl:template match="/cc:Module//*[@title='Security Requirements']|/cc:Module//sec:Security_Requirements">
    <xsl:variable name="title"><xsl:if test="not(@title)"><xsl:value-of select="local-name()"/></xsl:if><xsl:value-of select="@title"/></xsl:variable>

    <h1 id="{@id}" class="indexable" data-level="1"><xsl:value-of select="$title"/></h1>
    <xsl:call-template name="secrectext"/>
   <xsl:apply-templates select="cc:base-pp"/>
    <xsl:call-template name="man-sfrs"/>
  </xsl:template>

  <xsl:template name="consistency-rationale">
    <h1 id="mod-conrat" class="indexable" data-level="1">Consistency Rationale</h1>

    <xsl:for-each select="//cc:base-pp">
      <xsl:variable name="base" select="."/>

      <h2 id="conrat-{@short}" class="indexable" data-level="2">
	<xsl:apply-templates select="." mode="expanded"/>
      </h2>

      <!-- #################### -->
      <h3 id="contoe-{@short}" class="indexable" data-level="3">
	Consistency of TOE Type
      </h3>
      <xsl:apply-templates select="./cc:con-toe"/>

      <!-- #################### -->
      <h3 id="consecprob-{@short}" class="indexable" data-level="3">
	Consistency of Security Problem Definition
      </h3>
      The threats, assumptions, and OSPs defined by this PP-Module (see section 3.1) supplement those defined in the
      <xsl:apply-templates mode="short" select="."/> as follows:
      <xsl:apply-templates select="./cc:con-sec-prob"/>
      <table><tr><th>PP-Module Threat, Assumption, OSP</th><th>Consistency Rationale</th></tr>
      <xsl:for-each select="//cc:threat[cc:description]|//cc:assumption[cc:description]|//cc:OSP[cc:description]">
	<xsl:call-template name="consistency-row">
	  <xsl:with-param name="base" select="$base"/>
	  <xsl:with-param name="orig" select="."/>
	</xsl:call-template>
      </xsl:for-each>
      </table>

      <!-- #################### -->
      <h3 id="conobj-{@short}" class="indexable" data-level="3">
	Consistency of Objectives
      </h3>
      <p>
      <xsl:apply-templates select="./cc:con-obj"/>
      <xsl:if test="//cc:SO[cc:description]">
	  The objectives for the TOEs are consistent with the <xsl:apply-templates mode="short" select="."/> based on the following rationale:
      <table><tr><th>PP-Module TOE Objective</th><th>Consistency Rationale</th></tr>
      <xsl:for-each select="//cc:SO[cc:description]">
	<xsl:call-template name="consistency-row">
	  <xsl:with-param name="base" select="$base"/>
	  <xsl:with-param name="orig" select="."/>
	</xsl:call-template>
      </xsl:for-each>
      </table>
      </xsl:if>
      </p>

      <p>
      <xsl:apply-templates select="./cc:con-op-en"/>
      <xsl:if test="//cc:SOE">
	  The objectives for the TOE's Operational Environment are consistent with the <xsl:apply-templates mode="short" select="."/> based on the following rationale:
      <table><tr><th>PP-Module Operational Environment Objective</th><th>Consistency Rationale</th></tr>
      <xsl:for-each select="//cc:SOE">
	<xsl:call-template name="consistency-row">
	  <xsl:with-param name="base" select="$base"/>
	  <xsl:with-param name="orig" select="."/>
	</xsl:call-template>
      </xsl:for-each>
      </table>
      </xsl:if>
      </p>

      <h3 id="conreq-{@short}" class="indexable" data-level="3">
	Consistency of Requirements
      </h3>
      <xsl:apply-templates select="./cc:con-req"/>
      This PP-Module identifies several SFRs from the
      <xsl:apply-templates mode="short" select="."/> that are needed to support
      <xsl:value-of select="/cc:Module/@target-products"/> functionality.
      This is considered to be consistent because the functionality provided by the
      <xsl:apply-templates mode="short" select="."/> is being used for its intended purpose.
      <xsl:choose>
        <xsl:when test='$base//cc:modified-sfrs//cc:f-element'>
          The PP-Module also identifies a number of modified SFRs from the
          <xsl:apply-templates mode="short" select="."/>
          <xsl:if test='$base//cc:additional-sfrs//cc:f-element'>
            as well as new SFRs 
          </xsl:if>
          that are used entirely to provide functionality for
          <xsl:value-of select="/cc:Module/@target-products"/>.
        </xsl:when>
        <xsl:when test='$base//cc:additional-sfrs//cc:f-element'>
            The PP-Module identifies new SFRs that are used entirely to provide
            functionality for <xsl:value-of select="/cc:Module/@target-products"/>.
        </xsl:when>
        <xsl:otherwise/>
      </xsl:choose>
          The rationale for why this does not conflict with the claims
      defined by the
      <xsl:apply-templates mode="short" select="."/> are as follows:
      <table>
	<tr><th>PP-Module Requirement</th><th>Consistency Rationale</th></tr>
	<tr> <th colspan="2"> Modified SFRs</th></tr>
	<xsl:call-template name="req-con-rat-sec">
	  <xsl:with-param name="f-comps" select="$base/cc:modified-sfrs//cc:f-component"/>
	  <xsl:with-param name="short" select="$base/@short"/>
	  <xsl:with-param name="none-msg">
	    This PP-Module does not modify any requirements when the
	    <xsl:apply-templates mode="short" select="."/> is the base.
	  </xsl:with-param>
	</xsl:call-template>

  <xsl:if test="$base/cc:additional-sfrs//cc:f-component">
  	<tr>
	    <th colspan="2"> Additional SFRs</th>
	  </tr>
	  <xsl:call-template name="req-con-rat-sec">
	    <xsl:with-param name="f-comps" select="$base/cc:additional-sfrs//cc:f-component"/>
	    <xsl:with-param name="short" select="$base/@short"/>
	    <xsl:with-param name="none-msg">
	      This PP-Module does not add any requirements when the
	      <xsl:apply-templates mode="short" select="."/> is the base.
	    </xsl:with-param>
	  </xsl:call-template>
	</xsl:if>

	<tr>
	  <th colspan="2"> Mandatory SFRs</th>
	  <xsl:call-template name="req-con-rat-sec">
	    <xsl:with-param name="f-comps" select="//cc:man-sfrs//cc:f-component"/>
	    <xsl:with-param name="short" select="$base/@short"/>
	    <xsl:with-param name="none-msg">
	      This PP-Module does not define any Mandatory requirements.
	    </xsl:with-param>
	  </xsl:call-template>
	</tr>
	<tr>
	  <th colspan="2"> Optional SFRs</th>
	  <xsl:call-template name="req-con-rat-sec">
	    <xsl:with-param name="f-comps" select="//cc:opt-sfrs//cc:f-component"/>
	    <xsl:with-param name="short" select="$base/@short"/>
	    <xsl:with-param name="none-msg">
	      This PP-Module does not define any Optional requirements.
	    </xsl:with-param>
	  </xsl:call-template>
	</tr>
	<tr>
	  <th colspan="2"> Selection-based SFRs</th>
	  <xsl:call-template name="req-con-rat-sec">
	    <xsl:with-param name="f-comps" select="//cc:sel-sfrs//cc:f-component"/>
	    <xsl:with-param name="short" select="$base/@short"/>
	    <xsl:with-param name="none-msg">
	      This PP-Module does not define any Selection-based requirements.
	    </xsl:with-param>
	  </xsl:call-template>
	</tr>
	<tr>
	  <th colspan="2"> Objective SFRs</th>
	  <xsl:call-template name="req-con-rat-sec">
	    <xsl:with-param name="f-comps" select="//cc:obj-sfrs//cc:f-component"/>
	    <xsl:with-param name="short" select="$base/@short"/>
	    <xsl:with-param name="none-msg">
	      This PP-Module does not define any Objective requirements.
	    </xsl:with-param>
	  </xsl:call-template>
	</tr>
	<tr>
	  <th colspan="2"> Implementation-Dependent SFRs</th>
	  <xsl:call-template name="req-con-rat-sec">
	    <xsl:with-param name="f-comps" select="//cc:impl-dep-sfrs//cc:f-component"/>
	    <xsl:with-param name="short" select="$base/@short"/>
	    <xsl:with-param name="none-msg">
	      This PP-Module does not define any Implementation-Dependent requirements.
	    </xsl:with-param>
	  </xsl:call-template>
	</tr>


      </table>
    </xsl:for-each> <!-- End base iteration -->
  </xsl:template>

<!-- ############################################ -->
<!-- # Requirement Consistency Rational Section # -->
<!-- ############################################ -->
  <xsl:template name="req-con-rat-sec">
    <xsl:param name="f-comps"/>
    <xsl:param name="short"/>
    <xsl:param name="verb"/>
    <xsl:param name="none-msg"/>
    <xsl:choose>
      <xsl:when test="$f-comps">
      	<xsl:for-each select="$f-comps"><tr>
<!-- TODO: Theres probably more to do here. -->
          <td><xsl:apply-templates mode="getId" select="."/></td>
          <td> <xsl:choose>
            <xsl:when test="@iteration and //cc:base-pp[@short=$short]//cc:con-mod[@ref=current()/@cc-id and @iteration=current()/@iteration]">
              <xsl:apply-templates select="//cc:base-pp[@short=$short]//cc:con-mod[@ref=current()/@cc-id and @iteration=current()/@iteration]"/>
            </xsl:when>
            <xsl:when test="not(@iteration) and //cc:base-pp[@short=$short]//cc:con-mod[@ref=current()/@cc-id and not(@iteration)]">
              <xsl:apply-templates select="//cc:base-pp[@short=$short]//cc:con-mod[@ref=current()/@cc-id and not(@iteration)]"/>
            </xsl:when>
            <xsl:otherwise>
              <xsl:apply-templates select="cc:consistency-rationale/node()">
                <xsl:with-param name="base" select="$short"/>
              </xsl:apply-templates>
            </xsl:otherwise>
            </xsl:choose></td>
         </tr></xsl:for-each>
      </xsl:when>
      <xsl:otherwise>
        <tr><td colspan="2" style="text-align:center">
          <xsl:value-of select="$none-msg"/>
        </td></tr>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>


<!-- ############################################ -->
<!-- #            Base-pp Template              # -->
<!-- ############################################ -->
  <xsl:template match="cc:base-pp">
    <h2 id="{@short}" class="indexable" data-level="2">
      <xsl:apply-templates mode="short" select="."/>
       Security Functional Requirements Direction
    </h2>
    <xsl:if test="not(cc:sec-func-req-dir)">
      In a PP-Configuration that includes <xsl:apply-templates mode="short" select="."/>,
      the TOE is expected to rely on some of the security functions implemented by the <xsl:value-of select="@product"/>
      as a whole and evaluated against the  <xsl:apply-templates mode="short" select="."/>.
      The following sections describe any modifications that the ST author must make to the SFRs
      defined in the <xsl:apply-templates mode="short" select="."/> in addition to what is mandated by <a class="dynref" href="#man-sfrs">Section </a>.
    </xsl:if>
    <xsl:apply-templates select="cc:sec-func-req-dir"/>


    <xsl:element name="h2">
      <xsl:attribute name="id">modsfr-<xsl:value-of select="@short"></xsl:value-of></xsl:attribute>
      <xsl:attribute name="class">indexable</xsl:attribute>
      <xsl:attribute name="data-level">3</xsl:attribute>
      Modified SFRs
    </xsl:element>
    <xsl:choose><xsl:when test="cc:modified-sfrs//cc:f-component">
      The SFRs listed in this section are defined in the <xsl:apply-templates mode="short" select="."/> and relevant to the secure operation of the TOE.
    <xsl:apply-templates select="cc:modified-sfrs"/>
    </xsl:when>
    <xsl:otherwise>
      This PP-Module does not modify any SFRs defined by the <xsl:apply-templates mode="short" select="."/>.
    </xsl:otherwise>
    </xsl:choose>
    <!--
	 If we have only one base PP, we should hide this section (so says NIAP).
	 In that case there shouldn't be any additional-sfrs (but for some
	 reason we're allowing it).
    -->
    <xsl:if test="count(//cc:base-pp)>1 or cc:additional-sfrs//cc:f-component" >
    <xsl:element name="h2">
      <xsl:attribute name="id">addsfr-<xsl:value-of select="@short"></xsl:value-of></xsl:attribute>
      <xsl:attribute name="class">indexable</xsl:attribute>
      <xsl:attribute name="data-level">3</xsl:attribute>
      Additional SFRs
    </xsl:element>
    <xsl:choose><xsl:when test="cc:additional-sfrs//cc:f-component">
      This section defines additional SFRs that must be added to the TOE boundary in order to implement the functionality in any PP-Configuration where the <xsl:apply-templates mode="short" select="."/> is claimed as the Base-PP.
      <xsl:apply-templates select="cc:additional-sfrs"/>
    </xsl:when>
    <xsl:otherwise>
This PP-Module does not define any additional SFRs for any PP-Configuration where the <xsl:apply-templates mode="short" select="."/> is claimed as the Base-PP.
    </xsl:otherwise>
    </xsl:choose>
    </xsl:if>
  </xsl:template>

  <xsl:template match="cc:con-sec-problem">
    <xsl:apply-templates/>
  </xsl:template>



  <xsl:template name="consistency-row">
    <xsl:param name="base"/>
    <xsl:param name="orig"/>
	<tr>
	  <td><xsl:value-of select="$orig/@name"/></td>
	  <!-- if the base section has a con-mod equal to the id -->
	  <td><xsl:choose>
	    <xsl:when test="$base/cc:con-mod[@ref=$orig/@name]">
	      <xsl:apply-templates select="$base/cc:con-mod[@ref=$orig/@name]"/>
	    </xsl:when>
	    <xsl:otherwise>
	      <!-- Can only go one element deep here -->
	      <xsl:apply-templates select="cc:consistency-rationale/node()">
		<xsl:with-param name="base" select="$base/@short"/>
	      </xsl:apply-templates>
	    </xsl:otherwise>
	  </xsl:choose></td>
	</tr>
  </xsl:template>

  <xsl:template match="cc:bibliography">
    <h1 id="bibliography" class="indexable" data-level="A">Bibliography</h1>
    <table>
      <tr class="header">
        <th>Identifier</th>
        <th>Title</th>
      </tr>
      <xsl:apply-templates mode="hook" select="."/>
      <xsl:for-each select="cc:entry">
        <tr>
          <td>
            <xsl:element name="span">
              <xsl:attribute name="id">
                <xsl:value-of select="@id"/>
              </xsl:attribute> [<xsl:value-of select="cc:tag"/>] </xsl:element>
          </td>
          <td>
            <xsl:apply-templates select="cc:description"/>
          </td>
        </tr>
      </xsl:for-each>
    </table>

  </xsl:template>

  <xsl:template name="man-sfrs">
    <h2 id="man-sfrs" class="indexable" data-level="2">TOE Security Functional Requirements</h2>
    <xsl:choose>
      <xsl:when test="//cc:man-sfrs/cc:description">
         <xsl:apply-templates select="//cc:man-sfrs/cc:*"/>
      </xsl:when>
      <xsl:when test="//cc:man-sfrs//cc:f-component">
	The following section describes the SFRs that must be satisfied by any TOE that claims conformance to this PP-Module.
	These SFRs must be claimed regardless of which PP-Configuration is used to define the TOE.
        <xsl:apply-templates select="//cc:man-sfrs/cc:*"/>
      </xsl:when>
      <xsl:otherwise>
	This PP-Module does not define any mandatory SFRs.
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template name="opt-sfrs">
    <h1 id="opt-sfrs" class="indexable" data-level="A">Optional SFRs</h1>
    <h2 id="strictly-optional-sfrs" class="indexable" data-level="2">Strictly Optional Requirements</h2>
    <xsl:choose>
      <xsl:when test="//cc:opt-sfrs//cc:f-component">
        <xsl:apply-templates select="//cc:opt-sfrs//cc:f-component"/>
      </xsl:when>
      <xsl:otherwise>
	<p>
	  This PP-Module does not define any Optional SFRs.
	</p>
      </xsl:otherwise>
    </xsl:choose>
    <h2 id="objective-sfrs" class="indexable" data-level="2">Objective Requirements</h2>
    <xsl:choose>
      <xsl:when test="//cc:obj-sfrs//cc:f-component">
        <xsl:apply-templates select="//cc:obj-sfrs//cc:f-component"/>
      </xsl:when>
      <xsl:otherwise>
	<p>
	  This PP-Module does not define any Objective SFRs.
	</p>
      </xsl:otherwise>
    </xsl:choose>
    <h2 id="impl-dep-sfrs" class="indexable" data-level="2">Implementation-Dependent Requirements</h2>
    <xsl:choose>
      <xsl:when test="//cc:impl-dep-sfrs//cc:f-component">
        <xsl:apply-templates select="//cc:impl-dep-sfrs//cc:f-component"/>
      </xsl:when>
      <xsl:otherwise>
	<p>
	  This PP-Module does not define any Implementation-Dependent SFRs.
	</p>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template name="sel-sfrs">
    <h1 id="sel-sfrs" class="indexable" data-level="A">Selection-based SFRs</h1>
<!-- This paragraph is not needed since the reader should know all of it from the base-PP: so says NIAP.
      As indicated in the introduction to this PP-Module, the baseline requirements (those that must be
    performed by the TOE or its underlying platform) are contained in the body of this PP-Module.
    There are additional requirements based on selections in the body of the PP-Module:
    if certain selections are made, then additional requirements below will need to be included.<br/><br/>
 -->
    <xsl:choose>
      <xsl:when test="//cc:sel-sfrs//cc:f-component">
        <xsl:apply-templates select="//cc:sel-sfrs//cc:f-component"/>
      </xsl:when>
      <xsl:otherwise>
	<p>
	  This PP-Module does not define any selection-based SFRs.
	</p>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template name="obj-sfrs">
    <h1 id="obj-sfrs" class="indexable" data-level="A">Objective SFRs</h1>
    This section is reserved for requirements that are not currently prescribed by this PP-Module
    but are expected to be included in future versions of the PP-Module.
    Vendors planning on having evaluations performed against future products are encouraged
    to plan for these objective requirements to be met. <br/><br/>
    <xsl:choose>
      <xsl:when test="//cc:obj-sfrs//cc:f-component">
        <xsl:apply-templates select="//cc:obj-sfrs//cc:f-component"/>
      </xsl:when>
      <xsl:otherwise>
	<p>
	  This PP-Module does not define any objective SFRs.
	</p>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

<xsl:template name="impl-dep-sfrs">
    <h1 id="impl-dep-sfrs" class="indexable" data-level="A">Implementation-Dependent SFRs</h1>
    This section contains requirements that depend on the TOE implementing certain product features or use cases.
	<br/><br/>
    <xsl:choose>
      <xsl:when test="//cc:impl-dep-sfrs//cc:f-component">
        <xsl:apply-templates select="//cc:impl-dep-sfrs//cc:f-component"/>
      </xsl:when>
      <xsl:otherwise>
	<p>
	  This PP-Module does not define any Implementaion-Dependent SFRs.
	</p>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>



  <!--
      Eat all assurance activities
  -->
  <xsl:template match="cc:aactivity">
    <xsl:if test="not($release='final')">
      <div class="activity_pane hide">
	<div class="activity_pane_header">
	  <a onclick="toggle(this);return false;" href="#">
            <span class="activity_pane_label"> Evaluation Activity </span>
            <span class="toggler"/>
	  </a>
	</div>
	<div class="activity_pane_body">
	  <i>
            <xsl:apply-templates/>
	  </i>
	</div>
      </div>
    </xsl:if>
  </xsl:template>







</xsl:stylesheet>