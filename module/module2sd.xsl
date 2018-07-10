<?xml version="1.0" encoding="utf-8"?>
<!--
    Stylesheet for Protection Profile Schema
    Based on original work by Dennis Orth
    Subsequent modifications in support of US NIAP
-->

<x:stylesheet xmlns:x="http://www.w3.org/1999/XSL/Transform"
  xmlns:cc="https://niap-ccevs.org/cc/v1"
  xmlns="http://www.w3.org/1999/xhtml"
  xmlns:h="http://www.w3.org/1999/xhtml"
  version="1.0">

  <!-- Variable for selecting how much debugging we want -->
  <x:param name="debug" select="'v'"/>

  <x:variable name="space3">&#160;&#160;&#160;</x:variable>
  
  <!-- Forces output to make legitimate HTML and not XML -->
  <x:output method="html" encoding="UTF-8"/>

  <!-- Put all common templates into ppcommons.xsl -->
  <!-- They can be redefined/overridden  -->
  <x:include href="../ppcommons.xsl"/>


  <x:template match="/cc:PP">
    <!-- Start with !doctype preamble for valid (X)HTML document. -->
    <x:text disable-output-escaping='yes'>&lt;!DOCTYPE html&gt;&#xa;</x:text>

    <html xmlns="http://www.w3.org/1999/xhtml">
      <head> <title>Support Document - PP-Module for <x:value-of select="/cc:PP/@name"/>s</title>      </head>
      <body>
	<div style="text-align: center; margin-left: auto; margin-right: auto;">
	  <h1 class="title" style="page-break-before:auto;">Support Document - PP-Module for <x:value-of select="/cc:PP/@name"/>s</h1>
	  <noscript><h1 style="text-align:center; border-style: dashed; border-width: medium; border-color: red;">This page is best viewed with JavaScript enabled!</h1></noscript>
	  <img src="images/niaplogo.png" alt="NIAP"/>

	  <br/>Version: <x:value-of select="//cc:ReferenceTable/cc:PPVersion"/>
          <br/><x:value-of select="//cc:ReferenceTable/cc:PPPubDate"/>
          <br/><b><x:value-of select="//cc:PPAuthor"/></b>
	</div>

	<x:call-template name="foreward"/>
	<div id="toc"/>
	<x:call-template name="structure"/>

      </body>
    </html>
  </x:template>

  <x:template name="structure">
    <p>Assurance Activities can be defined for both SFRs and Security Assurance Requirements (SAR). These are defined in separate sections of the SD.</p>
    <p>If any Assurance Activity cannot be successfully completed in an evaluation then the overall verdict for the evaluation is a ‘fail’.
    In rare cases there may be acceptable reasons why an Assurance Activity may be modified or deemed not applicable for a particular TOE, but this must be agreed with the Certification Body for the evaluation. 
    </p>
    <p>In general, if all Assurance Activities (for both SFRs and SARs) are successfully completed in an evaluation then it would be expected that the overall verdict for the evaluation is a ‘pass’.
      To reach a ‘fail’ verdict when the Assurance Activities have been successfully completed would require a specific justification from the evaluator as to why the Assurance Activities were not sufficient for that TOE.
      </p>
      <p>Similarly, at the more granular level of Assurance Components, if the Assurance Activities for an Assurance Component and all of its related SFR Assurance Activities are successfully completed in an evaluation then it would be expected that the verdict for the Assurance Component is a ‘pass’.
      To reach a ‘fail’ verdict for the Assurance Component when these Assurance Activities have been successfully completed would require a specific justification from the evaluator as to why the Assurance Activities were not sufficient for that TOE. 
      </p>
  </x:template>

  <x:template name="foreward">
    <div class="foreword">
      <h1 style="text-align: center">Foreword</h1>
    <p>
    This is a Supporting Document (SD), intended to complement the Common Criteria version 3 and the
    associated Common Evaluation Methodology for Information Technology Security Evaluation.
    SDs may be “Guidance Documents”, that highlight specific approaches and application of the standard
    to areas where no mutual recognition of its application is required, and as such, are not of normative nature, or “Mandatory Technical Documents”, whose application is mandatory for evaluations whose
    scope is covered by that of the SD.
    The usage of the latter class is not only mandatory, but certificates
    issued as a result of their application are recognized under the CCRA.
    </p>
    <p><b>Technical Editor:</b><br/>
    National Information Assurance Partnership (NIAP)
    </p>
    <p><b style="page-break-before:always;">Document history:</b><br/>
    <table>
      <tr class="header">
        <th>Version</th>
        <th>Date</th>
        <th style="align:left;">Comment</th>
      </tr>
      <x:for-each select="cc:RevisionHistory/cc:entry">
        <tr>
          <td><x:value-of select="cc:version"/></td>
          <td><x:value-of select="cc:date"/></td>
          <td><x:apply-templates select="cc:subject"/></td>
        </tr>
      </x:for-each>
    </table>
    </p>
    <p><b>General Purpose:</b><br/>
    The purpose of this SD is to define evaluation methods for the functional behavior of 
    <x:value-of select="concat(/cc:PP/@name, /cc:PP/plural-suffix)"/>.
    </p>
    <p><b>Acknowledgements:</b><br/>
    This SD was developed with support from NIAP <x:value-of select="/cc:PP/@name"/> Technical Community members, with
representatives from industry, Government agencies, Common Criteria Test Laboratories, and
members of academia.
    </p>
    </div>
  </x:template>
</x:stylesheet>
