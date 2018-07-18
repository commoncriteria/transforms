<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns="http://www.w3.org/1999/xhtml"
  xmlns:htm="http://www.w3.org/1999/xhtml"
  version="1.0">

  <xsl:template name="bp-con-state">
    <xsl:param name="has_appendix"/>
    <xsl:param name="impsatreqid"/>
    <dl>
      <dt>Conformance Statement</dt><dd> To be conformant to this PP, an <abbr title="Security Target">ST</abbr> must demonstrate Exact
          Conformance, a subset of Strict Conformance as defined in <a href="#bibCC">[CC]</a> Part 1
          (ASE_CCL).
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
    <xsl:if test="$has_appendix='on'"> Unconditional requirements are found in the main body of the
      document, while the selection-based, optional, and objective requirements are contained in respective sections in the appendix. </xsl:if>
    <xsl:if test="$has_appendix!='on'"> The type of each requirement is identified in line with the
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

  <xsl:template name="verrev">Version 3.1, Revision 5</xsl:template>

  <xsl:template name="bp-sfrs">
    The Security Functional Requirements included in this section 
    are derived from Part 2 of the Common Criteria for Information
    Technology Security Evaluation, <xsl:call-template name="verrev"/>,
    with additional extended functional components. 
  </xsl:template>

  <xsl:template name="bp-biblio">
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


  <xsl:template name="bp-secreq">
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
