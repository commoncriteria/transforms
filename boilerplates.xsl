<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:cc="https://niap-ccevs.org/cc/v1"
  xmlns="http://www.w3.org/1999/xhtml"
  xmlns:htm="http://www.w3.org/1999/xhtml"
  version="1.0">

  <!-- Eat all hook-based cc -->
  <xsl:template match="cc:*" mode="hook"/>

  <!-- Eat all individual ones that turn off boilerplating -->
  <xsl:template match="//cc:*[@boilerplate='no']" priority="1.0" mode="hook"/>

  <xsl:template match="/cc:*[@boilerplate='yes']//cc:appendix[@title='Optional Requirements']"
		mode="hook">
    <xsl:variable name="cclsec"><xsl:value-of select="//cc:*[@title='Conformance Claims']/@id"/></xsl:variable>
    <xsl:variable name="optappid"><xsl:value-of select="//cc:*[@title='Optional Requirements']/@id"/></xsl:variable>
    <xsl:variable name="selappid"><xsl:value-of select="//cc:*[@title='Selection-Based Requirements']/@id"/></xsl:variable>
    <xsl:variable name="objappid"><xsl:value-of select="//cc:*[@title='Objective Requirements']/@id"/></xsl:variable>

    As indicated in <a href="#{$cclsec}" class="dynref">Section </a>
    the baseline requirements (those that must be performed by the TOE) are
    contained in the body of this PP. Additionally, there are three other types of requirements
    specified in
    <a href="#{$optappid}" class="dynref"></a>,
    <a href="#{$selappid}" class="dynref"></a>, and
    <a href="#{$objappid}" class="dynref"></a>.
    The first type (in this Appendix) are requirements that can be included
    in the <abbr title="Security Target">ST</abbr>,
    but are not required in order for a TOE to claim conformance to
    this PP. The second type
    (in <a href="#{$selappid}" class="dynref"></a>) are requirements based on selections
    in the body of the PP: if certain selections are made, then additional requirements in that
    appendix must be included. The third type (in
    <a href="#{$objappid}" class="dynref"></a>) are components that
    are not required in order to conform to this PP, but will be included in the baseline
    requirements in future versions of this PP, so adoption by vendors is encouraged. Note that the
    ST author is responsible for ensuring that requirements that may be associated with those in
    <a href="#{$optappid}" class="dynref"></a>,
    <a href="#{$selappid}" class="dynref"></a>, and
    <a href="#{$objappid}" class="dynref"></a>
    but are not listed (e.g., FMT-type requirements) are also included in the ST.
  </xsl:template>

  <xsl:template match="/cc:*[@boilerplate='yes']//cc:*[@title='Implicitly Satisfied Requirements']" mode="hook">    <p>
This appendix lists requirements that should be considered satisfied by products
successfully evaluated against this Protection Profile.
However, these requirements are not featured explicitly as SFRs and should not be
included in the <abbr title="Security Target">ST</abbr>.
They are not included as standalone SFRs because it would
increase the time, cost, and complexity of evaluation.
This approach is permitted
by <a href="#bibCC">[CC]</a> Part 1, <b>8.2 Dependencies between components</b>.
    </p>
    <p>
This information benefits systems engineering activities which call for inclusion of
particular security controls.  Evaluation against the Protection Profile
provides evidence that these controls are present and have been evaluated.
    </p>
</xsl:template>


  <xsl:template match="/cc:*[@boilerplate='yes']//cc:section[@title='Terms']"
		mode="hook">
    The following sections list Common Criteria and technology terms used in this document.
  </xsl:template>


  <xsl:template name="selection-based-text">
As indicated in the introduction to this PP,
the baseline requirements
(those that must be performed by the TOE or its underlying platform)
are contained in the body of this PP.
There are additional requirements based on selections in the body of the PP:
if certain selections are made, then additional requirements below must be included.
  </xsl:template>


  <!-- ############## -->
  <xsl:template  match="/cc:PP[@boilerplate='yes']//cc:chapter[@title='Conformance Claims']"
		mode="hook">
    <xsl:variable name="impsatreqid"><xsl:value-of select="//cc:*[@title='Implicitly Satisfied Requirements']/@id"/></xsl:variable>
    <dl>
        <dt>Conformance Statement</dt>
        <dd>An <abbr title="Security Target">ST</abbr> must claim exact conformance to this PP, as defined in the CC and CEM addenda for Exact Conformance, Selection-Based SFRs, and Optional SFRs (dated May 2017).</dd>
        <dt>CC Conformance Claims</dt>
        <dd>This PP is conformant to Parts 2 (extended) and 3 (conformant) of Common Criteria <xsl:call-template name="verrev"/>.</dd>
        <dt>PP Claim </dt>
        <dd>This PP does not claim conformance to any Protection Profile. </dd>
        <dt>Package Claim</dt>
        <dd>This PP is TLS Package Conformant.</dd>
     </dl>
  </xsl:template>


  <!-- ############## -->
   <xsl:template  name="verrev">Version 3.1, Revision 5</xsl:template>

   <!-- ############## -->
   <xsl:template match="/cc:*[@boilerplate='yes']//cc:*[@title='Security Functional Requirements']" mode="hook">
    The Security Functional Requirements included in this section
    are derived from Part 2 of the Common Criteria for Information
    Technology Security Evaluation, <xsl:call-template name="verrev"/>,
    with additional extended functional components.
   </xsl:template>

   <!-- ############## -->
   <xsl:template match="/cc:*[@boilerplate='yes']//cc:bibliography" mode="hook">
<tr>
  <td><span id="bibCC"> [CC] </span></td>
  <td>Common Criteria for Information Technology Security Evaluation - <ul>
  <li>
<a href="http://www.commoncriteriaportal.org/files/ccfiles/CCPART1V3.1R5.pdf">Part
                1: Introduction and General Model</a>, CCMB-2017-04-001, <xsl:call-template name="verrev"/>,
              April 2017.</li>
<li>
<a href="http://www.commoncriteriaportal.org/files/ccfiles/CCPART2V3.1R5.pdf">Part
                2: Security Functional Components</a>, CCMB-2017-04-002, <xsl:call-template name="verrev"/>,
              April 2017.</li>
<li>
<a href="http://www.commoncriteriaportal.org/files/ccfiles/CCPART3V3.1R5.pdf">Part
                3: Security Assurance Components</a>, CCMB-2017-04-003, <xsl:call-template name="verrev"/>,
              April 2017.</li>
</ul>
</td>
</tr>
  </xsl:template>


  <xsl:template match="citeCC" name="citeCC"><a href="#bibCC">[CC]</a></xsl:template>


  <!-- ############## -->
   <xsl:template match="/cc:*[@boilerplate='yes']//cc:*[@title='Security Requirements']" mode="hook" name="secrectext">
     This chapter describes the security requirements
     which have to be fulfilled by the product under evaluation. Those requirements comprise functional
     components from Part 2 and assurance components from Part 3 of <a href="#bibCC">[CC]</a>. The
     following notations are used:
     <ul>
       <li>
         <b>Refinement</b> operation (denoted by <b>bold text</b> or <strike>strikethrough
         text</strike>): is used to add details to a requirement (including replacing an assignment
         with a more restrictive selection) or to remove part of the requirement that is made irrelevant
         through the completion of another operation, and thus further restricts a requirement.
         </li>
       <li>
         <b>Selection</b> (denoted by <i>italicized text</i>): is used to select one or more options
         provided by the [CC] in stating a requirement.</li>
       <li>
         <b>Assignment</b> operation (denoted by <span class="assignable-content">italicized text</span>): is used to assign a
         specific value to an unspecified parameter, such as the length of a password. Showing the
         value in square brackets indicates assignment.</li>
       <li>
         <b>Iteration</b> operation: are identified with a number inside parentheses (e.g.
         "(1)")</li>
     </ul>
  </xsl:template>

  <xsl:template match="/cc:Module//cc:*[@title='TOE Security Functional Requirements']" mode="hook">
    <xsl:choose>
      <xsl:when test="cc:subsection[@title='TOE Security Functional Requirements']">
The following section describes the SFRs that must be satisfied by any TOE that claims conformance to this PP-Module.
These SFRs must be claimed regardless of which PP-Configuration is used to define the TOE.
      </xsl:when>
      <xsl:otherwise>
This module does not define any mandatory SFRs that apply regardless of the PP-Configuration.
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>


  <xsl:template match="/cc:Module//cc:*[@title='Assumptions']" mode="hook">
    <xsl:choose>
      <xsl:when test="cc:assumptions">
These assumptions are made on the Operational Environment in order to be able to ensure that the
security functionality specified in the PP-Module can be provided by the TOE. If the TOE is placed in an
Operational Environment that does not meet these assumptions, the TOE may no longer be able to
provide all of its security functionality.
      </xsl:when>
      <xsl:otherwise>
This module does not define any assumptions.
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="/cc:*//cc:*[@title='Security Objectives Rationale']">
    <h2 id="{@id}" class="indexable" data-level="2"><xsl:value-of select="@title"/></h2>
    This section describes how the assumptions, threats, and organization security policies map to the security objectives.

    <table>
      <tr class="header">
        <td>Threat, Assumption, or OSP</td>
        <td>Security Objectives</td>
        <td>Rationale</td>
      </tr>
      <xsl:for-each select="(//cc:threat | //cc:OSP | //cc:assumption)">
        <tr>
	  <td> <xsl:value-of select="@id"/> </td>
          <td>
            <xsl:for-each select="cc:objective-refer">
              <xsl:value-of select="@ref"/>
              <xsl:if test="position() != last()">
                <xsl:text>, </xsl:text>
              </xsl:if>
            </xsl:for-each>
          </td>
          <td>
            <xsl:for-each select="cc:objective-refer">
              <xsl:apply-templates select="cc:rationale"/>
              <xsl:if test="position() != last()">
                <br/>
              </xsl:if>
            </xsl:for-each>
          </td>
        </tr>
      </xsl:for-each>
    </table>
  </xsl:template>

  <xsl:template match="/cc:Module//cc:*[@title='Security Objectives for the Operational Environment']" mode="hook">
    <xsl:choose>
      <xsl:when test=".//cc:SOEs">
	The Operational Environment of the TOE implements technical and procedural measures to assist the TOE in correctly providing its security functionality (which is defined by the security objectives for the TOE).
	The security objectives for the Operational Environment consist of a set of statements describing the goals that the Operational Environment should achieve.
	This section defines the security objectives that are to be addressed by the IT domain or by non-technical or procedural means. The assumptions identified in Section 3 are incorporated as security objectives for the environment.
      </xsl:when>
      <xsl:otherwise>
This module does not define any objectives for the Operational Environment.
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>
  
  <xsl:template name="opt_appendix">
As indicated in the introduction to this PP, the baseline requirements (those that must be performed by the TOE) are contained in the body of this PP.
This Appendix contains three other types of optional requirements that may be included in the ST but are not required in order to conform to this PP.
The first type (in A.1) are strictly optional requirements that are independent of the TOE implementing any function.
If the TOE fulfills any of these requirements or supports a certain functionality, the vendor is encouraged but not required to add the related SFRs.
The second type (in A.2) are objective requirements that describe security functionality not yet widely available in commercial technology.
The requirements are not currently mandated in the body of this PP, but will be included in the baseline requirements in future versions of this PP.
Adoption by vendors is encouraged and expected as soon as possible.
The third type (in A.3) undefined<xsl:call-template name="imple_text"/>
  </xsl:template>

  <xsl:template name="imple_text">
that are dependent on the TOE implementing a particular function.
If the TOE fulfills any of these requirements, the vendor must either add the related SFR or disable the functionality for the evaluated configuration. 
  </xsl:template>


</xsl:stylesheet>
