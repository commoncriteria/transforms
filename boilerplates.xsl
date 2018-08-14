<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:cc="https://niap-ccevs.org/cc/v1"
  xmlns="http://www.w3.org/1999/xhtml"
  xmlns:htm="http://www.w3.org/1999/xhtml"
  version="1.0">

  <!-- Eat all hook-based cc -->
  <xsl:template match="cc:*" mode="hook"/>

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
    <a href="#{$optappid}" class="dynref">Appendix </a>,
    <a href="#{$selappid}" class="dynref">Appendix </a>, and 
    <a href="#{$objappid}" class="dynref">Appendix </a>.
    The first type (in this Appendix) are requirements that can be included
    in the <abbr title="Security Target">ST</abbr>, 
    but are not required in order for a TOE to claim conformance to
    this PP. The second type 
    (in <a href="#{$selappid}" class="dynref">Appendix </a>) are requirements based on selections
    in the body of the PP: if certain selections are made, then additional requirements in that
    appendix must be included. The third type (in 
    <a href="#{$objappid}" class="dynref">Appendix </a>) are components that
    are not required in order to conform to this PP, but will be included in the baseline
    requirements in future versions of this PP, so adoption by vendors is encouraged. Note that the
    ST author is responsible for ensuring that requirements that may be associated with those in
    <a href="#{$optappid}" class="dynref">Appendix </a>,
    <a href="#{$selappid}" class="dynref">Appendix </a>, and 
    <a href="#{$objappid}" class="dynref">Appendix </a>
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

  <xsl:template match="/cc:*[@boilerplate='yes']//cc:appendix[@title='Selection-Based Requirements']" 
		mode="hook">
As indicated in the introduction to this PP, 
the baseline requirements 
(those that must be performed by the TOE or its underlying platform)
are contained in the body of this PP.
There are additional requirements based on selections in the body of the PP:
if certain selections are made, then additional requirements below must be included.
  </xsl:template>

  <xsl:template match="/cc:*[@boilerplate='yes']//cc:appendix[@title='Objective Requirements']" 
		mode="hook">
This appendix includes requirements that specify security functionality which 
also addresses threats.
The requirements are not currently mandated in the body of this PP as they 
describe security functionality not yet widely-available in commercial technology.
However, these requirements may be included in the ST such that the TOE is still 
conformant to this PP, and it is expected that they be included as soon as possible.
  </xsl:template>

  <!-- ############## -->
  <xsl:template  match="/cc:*[@boilerplate='yes']//cc:chapter[@title='Conformance Claims']" 
		mode="hook">
    <xsl:variable name="impsatreqid"><xsl:value-of select="//cc:*[@title='Implicitly Satisfied Requirements']/@id"/></xsl:variable>
    <dl>
      <dt>Conformance Statement</dt><dd> To be conformant to this PP, an <abbr title="Security Target">ST</abbr> must demonstrate Exact
          Conformance, a subset of Strict Conformance as defined in <xsl:call-template name="citeCC"/> Part 1 (ASE_CCL).
	  The <abbr title="Security Target">ST</abbr> must include all components in this PP that are:<ul>
            <li>unconditional (which are always required)</li>
            <li>selection-based (which are required when certain <i>selections</i> are chosen in the
              unconditional requirements)</li>
          </ul>and may include components that are <ul>
            <li>optional or</li>
            <li>objective.</li>
          </ul>
           The type of each requirement is identified in line with the
      text.  
	  <p>
    <xsl:if test="$appendicize='on'"> Unconditional requirements are found in the main body of the
      document, while the selection-based, optional, and objective requirements are contained in respective sections in the appendix. </xsl:if>
    <xsl:if test="$appendicize!='on'"> The type of each requirement is identified in line with the
      text. </xsl:if>
The <abbr title="Security Target">ST</abbr> may iterate any of these components,
but it must not include any additional component (e.g. from <a href="#bibCC">[CC]</a> 
Part 2 or 3 or a PP not  conformant with this one, or extended by the 
<abbr title="Security Target">ST</abbr>) not defined in this PP
or a PP conformant to this one. 
	  </p>

	  <xsl:if test="$impsatreqid!=''">
	    <p>
Some components in this Protection Profile have a dependency on other components.
In accordance with <a href="#bibCC">[CC]</a> Part 1, 
<xsl:element name="a">
  <xsl:attribute name="href">#<xsl:value-of select="$impsatreqid"/></xsl:attribute>
  <xsl:attribute name="class">dynref</xsl:attribute>
  Appendix 
</xsl:element>
includes justifications for those cases where the PP does not explicitly 
contain the component upon which there is a dependency.
	    </p>
	  </xsl:if>
        </dd>
	<dt>CC Conformance Claims</dt><dd>This PP is conformant to Parts 2 (extended) and 3 (extended) of Common Criteria
          Version 3.1, Revision 5.<a href="#bibCC">[CC]</a>.</dd>
	  <dt>PP Claim</dt><dd>This PP does not claim conformance to any other Protection
          Profile.</dd><dt>Package Claim</dt><dd>This PP does not claim conformance to any packages.</dd></dl>
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
   <xsl:template match="/cc:*[@boilerplate='yes']//cc:*[@title='Security Requirements']" mode="hook">
This chapter describes the security requirements which have to be fulfilled by the TOE.
Those requirements comprise functional components from Part 2 and assurance components from Part 3 of <a href="#bibCC">[CC]</a>.
The following notations are used: <ul>
      <li><b>Refinement</b> operation (denoted by <b>bold text</b>): is used to add details to a
        requirement, and thus further restricts a requirement.</li>
      <li><b>Selection</b> (denoted by <i>italicized text</i>): is used to select one or more options
        provided by the [CC] in stating a requirement.</li>
      <li><b>Assignment</b> operation (denoted by <span class="assignable-content">italicized text</span>): is used to assign a specific value to an unspecified parameter, such as the length of a password. Showing the  value in square brackets indicates assignment.</li>
      <li><b>Iteration</b> operation: are identified with a number inside parentheses (e.g."(1)")</li>
    </ul>
  </xsl:template>

</xsl:stylesheet>
