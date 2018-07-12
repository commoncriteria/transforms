<?xml version="1.0" encoding="utf-8"?>
<!--
XSL for Protection Profile Modules
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
  <x:output method="xml" encoding="UTF-8"/>

  <!-- Put all common templates into ppcommons.xsl -->
  <!-- They can be redefined/overridden  -->
  <x:include href="../ppcommons.xsl"/>

  <x:template match="cc:*">
    <x:apply-templates/>
  </x:template>

  <x:template match="/cc:PP">
    <!-- Start with !doctype preamble for valid (X)HTML document. -->

    <html xmlns="http://www.w3.org/1999/xhtml">
      <head> 
	<title>Supporting Document - PP-Module for <x:value-of select="/cc:PP/@name"/>s</title>
	<style type="text/css">
	  #toc a{
	     display: block;
	  }

	</style>
      </head>
      <body>
	<div style="text-align: center; margin-left: auto; margin-right: auto;">
	  <h1 class="title" style="page-break-before:auto;">Supporting Document - PP-Module for <x:value-of select="/cc:PP/@name"/>s</h1>
	  <noscript><h1 style="text-align:center; border-style: dashed; border-width: medium; border-color: red;">This page is best viewed with JavaScript enabled!</h1></noscript>
	  <img src="images/niaplogo.png" alt="NIAP"/>

	  <br/>Version: <x:value-of select="//cc:ReferenceTable/cc:PPVersion"/>
          <br/><x:value-of select="//cc:ReferenceTable/cc:PPPubDate"/>
          <br/><b><x:value-of select="//cc:PPAuthor"/></b>
	</div>
	<x:call-template name="foreward"/>
	<x:call-template name="toc"/>
	<x:call-template name="intro"/>
	<x:apply-templates select="/cc:PP/cc:chapter/cc:section[@id='glossary']"/>
	<x:call-template name="sfrs"/>
	<x:call-template name="sars"/>
      </body>
    </html>
  </x:template>

  <x:template name="toc">
    <h1>Table of Contents</h1>
    <div id="toc"/>
  </x:template>

  <x:template name="sfrs">
    <h2 id="sfr" class="indexable" data-level="0">Evaluation Activities for SFRs</h2>
    <p>The EAs presented in this section capture the actions the evaluator performs 
    to address technology specific aspects covering specific SARs (e.g. ASE_TSS.1, 
    ADV_FSP.1, AGD_OPE.1, and ATE_IND.1) – this is in addition to the CEM work units 
    that are performed in <a href="#sar_aas" class="dynref"></a>.</p>
    
    <p>Regarding design descriptions (designated by the subsections labelled TSS, as 
    well as any required supplementary material that may be treated as proprietary), 
    the evaluator must ensure there is specific information that satisfies the EA. 
    For findings regarding the TSS section, the evaluator’s verdicts will be 
    associated with the CEM work unit ASE_TSS.1-1.
    Evaluator verdicts associated with the supplementary evidence will also be 
    associated with ASE_TSS.1-1, 
    since the requirement to provide such evidence is specified in ASE in the cPP.</p>
    
    <p>For ensuring the guidance documentation provides sufficient information for 
    the administrators/users as it pertains to SFRs, the evaluator’s verdicts will 
    be associated with CEM work units ADV_FSP.1-7, AGD_OPE.1-4, and AGD_OPE.1-5.</p>

    <p>Finally, the subsection labelled Tests is where the authors have determined 
    that testing of the product in the context of the associated SFR is necessary.
    While the evaluator is expected to develop tests, there may be instances where 
    it is more practical for the developer to construct tests, or where the 
    developer may have existing tests. 
    Therefore, it is acceptable for the evaluator to witness developer-generated 
    tests in lieu of executing the tests. 
    In this case, the evaluator must ensure the developer’s tests are executing both 
    in the manner declared by the developer and as mandated by the EA. 
    The CEM work units that are associated with the EAs specified in this section 
    are: ATE_IND.1-3, ATE_IND.1-4, ATE_IND.1-5, ATE_IND.1-6, and ATE_IND.1-7.</p>
    
    <!-- Run through all the base modules -->
    <x:for-each select="/cc:PP/cc:chapter[@id='req']/cc:*">
      <h3 class="indexable" data-level="1" id="{@id}"><x:value-of select="@title"/></h3>

      <x:apply-templates select="cc:subsection[@title='Applicable Modified SFRs']"/>
      <x:if test="not(cc:subsection[@title='Applicable Modified SFRs']/cc:*)">
	<h:p>This PP Module does not modify any requirements for this Base-PP.</h:p>
      </x:if>
      
      <x:choose>
	<x:when test="cc:subsection[@title='Additional SFRs']/cc:*">
	  <x:apply-templates select="cc:subsection[@title='Additional SFRs']"/>
	    </x:when>
	    <x:otherwise><h:p>This PP Module does define any additional requirements for this Base-PP.</h:p></x:otherwise>
      </x:choose>
    </x:for-each>
  </x:template>

  <x:template name="sars">
    <h2 id="sar_aas" class="indexable" data-level="0"> Assurance Activities for SARs</h2>
    <p>The PP-Module does not define any SARs beyond those defined within the <x:call-template name="bases"/> to which it can claim conformance.</p>
  </x:template>

  <x:template name="aaforsfrs">
    <h1 id="mandatory_aas" class="indexable" data-level="0">Assurance Activities for SFRs</h1>
    <p>The EAs presented in this section capture the actions the evaluator performs to address technology specific aspects covering specific SARs (e.g. ASE_TSS.1, ADV_FSP.1, AGD_OPE.1, and ATE_IND.1) – this is in addition to the CEM work units that are performed in <a href="#sar_aas" class="dynref"></a>.</p>

    <p>Regarding design descriptions (designated by the subsections labelled TSS, as well as any required supplementary material that may be treated as proprietary), the evaluator must ensure there is specific information that satisfies the EA. For findings regarding the TSS section, the evaluator’s verdicts will be associated with the CEM work unit ASE_TSS.1-1. Evaluator verdicts associated with the supplementary evidence will also be associated with ASE_TSS.1-1, since the requirement to provide such evidence is specified in ASE in the cPP. </p>

    <p>For ensuring the guidance documentation provides sufficient information for the administrators/users as it pertains to SFRs, the evaluator’s verdicts will be associated with CEM work units ADV_FSP.1-7, AGD_OPE.1-4, and AGD_OPE.1-5.</p>

    <p>Finally, the subsection labelled Tests is where the authors have determined that testing of the product in the context of the associated SFR is necessary. While the evaluator is expected to develop tests, there may be instances where it is more practical for the developer to construct tests, or where the developer may have existing tests. Therefore, it is acceptable for the evaluator to witness developer-generated tests in lieu of executing the tests. In this case, the evaluator must ensure the developer’s tests are executing both in the manner declared by the developer and as mandated by the EA. The CEM work units that are associated with the EAs specified in this section are: ATE_IND.1-3, ATE_IND.1-4, ATE_IND.1-5, ATE_IND.1-6, and ATE_IND.1-7.</p>
    <x:apply-templates select="/cc:PP/cc:chapter[@id='req']"/>

  </x:template>


  <x:template name="intro">
    <h1 id="introduction" class="indexable" data-level="0">Introduction</h1>
    <h2 id="scope" class="indexable" data-level="1">Technology Area and Scope of Supporting Document</h2>


    <p>The scope of the <x:value-of select="/cc:PP/@name"/> PP-Module is
    to describe the security functionality of 
    <x:value-of select="/cc:PP/@target-products"/> products in terms of 
    [CC] and to define functional and assurance requirements for such products. 
    This PP-Module is intended for use with the
    <x:choose>
      <x:when test="count(/cc:PP/cc:module/cc:base-pp)=1">
	<a href="{/cc:PP/cc:module/cc:base-pp/@url}"><x:value-of select="/cc:PP/cc:module/cc:base-pp/@name"/></a>
      </x:when>
      <x:otherwise>
	following Base-PPs:
	<ul>
	  <x:for-each select="/cc:PP/cc:module/cc:base-pp">
	    <li><a href="{/cc:PP/cc:module/cc:base-pp/@url}"><x:value-of select="/cc:PP/cc:module/cc:base-pp/@name"/></a></li>
	  </x:for-each>
	</ul>
      </x:otherwise>
    </x:choose>.</p>
    <p>This SD is mandatory for evaluations of TOEs that claim conformance to the PP-Module for <x:value-of select="concat(/cc:PP/@name,', version ', /cc:PP/cc:PPReference/cc:ReferenceTable/cc:PPVersion)"/>.
    Although Evaluation Activities are defined mainly for the evaluators to follow, in general they also help Developers to prepare for evaluation by identifying specific requirements for their TOE.
    The specific requirements in Evaluation Activities may in some cases clarify the meaning of Security
    Functional Requirements (SFR), and may identify particular requirements for the content of Security
    Targets (ST) (especially the TOE Summary Specification), user guidance documentation, and possibly
    supplementary information (e.g. for entropy analysis or cryptographic key management architecture).</p>

    <h2 id="structure" class="indexable" data-level="1">Structure of the Document</h2>
    <p>Evaluation Activities can be defined for both SFRs and Security Assurance Requirements (SAR),
    which are themselves defined in separate sections of the SD.</p>

    <p>If any Evaluation Activity cannot be successfully completed in an evaluation then
    the overall verdict for the evaluation is a 'fail'.
    In rare cases there may be acceptable reasons why an Evaluation Activity
    may be modified or deemed not applicable for a particular TOE, 
    but this must be approved by the Certification Body for the evaluation.</p>

    <p>In general, if all Evaluation Activities (for both SFRs and SARs) are successfully
    completed in an evaluation then it would be expected that the overall verdict for 
    the evaluation is a ‘pass’.
    To reach a ‘fail’ verdict when the Evaluation Activities have been successfully 
    completed would require a specific justification from the evaluator as to why the 
    Evaluation Activities were not sufficient for that TOE.
    </p>
    <p>Similarly, at the more granular level of Assurance Components, if the Evaluation 
    Activities for an Assurance Component and all of its related SFR Evaluation 
    Activities are successfully completed in an evaluation then it would be expected 
    that the verdict for the Assurance Component is a ‘pass’.
    To reach a ‘fail’ verdict for the Assurance Component when these Evaluation 
    Activities have been successfully completed would require a specific justification 
    from the evaluator as to why the Evaluation Activities were not sufficient for that TOE. 
    </p>
  </x:template>

  <x:template name="foreward">
    <div class="foreword">
      <h1 style="text-align: center">Foreword</h1>
      <p>This is a Supporting Document (SD), intended to complement the Common Criteria version 3
      and the associated Common Evaluation Methodology for
      Information Technology Security Evaluation.</p>
      <p>SDs may be “Guidance Documents”, that highlight specific approaches 
      and application of the standard to areas where no mutual recognition of
      its application is required, and as such, are not of normative nature, 
      or “Mandatory Technical Documents”, whose application is mandatory for evaluations 
      whose scope is covered by that of the SD.
      The usage of the latter class is not only mandatory, but certificates
      issued as a result of their application are recognized under the CCRA.</p>

      <p><b>Technical Editor:</b><br/>
      National Information Assurance Partnership (NIAP)
      </p>

      <p><b style="page-break-before:always;">Document history:</b>
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
      This SD was developed with support from NIAP <x:value-of select="/cc:PP/@name"/> 
      Technical Community members, with representatives from industry, Government 
      agencies, Common Criteria Test Laboratories, and members of academia.
      </p>
    </div>
  </x:template>


  <x:template match="cc:glossary">
    <table>
      <x:for-each select="cc:entry">
        <tr>
          <td><x:apply-templates select="cc:term"/></td>
          <td><x:apply-templates select="cc:description"/></td>
	</tr>
      </x:for-each>
    </table>
  </x:template>

  <x:template match="cc:glossary/cc:entry/cc:term/cc:abbr">
    <span id="abbr_{text()}"><x:value-of select="@title"/> (<abbr><x:value-of select="text()"/></abbr>)</span>
  </x:template>

  <x:template match="cc:section">
    <h2 id="{@id}" class="indexable" data-level="1"><x:value-of select="@title"/></h2>
    <x:apply-templates/>
  </x:template>

  <!-- <x:template name="showifexist"> -->
  <!--   <x:param name="bef"/> -->
  <!--   <x:param name="it"/> -->
  <!--   <x:param name="aft"/> -->
  <!--   <x:if test="$it"><x:value-of select="concat($bef,$it,$aft)"/></x:if> -->
  <!-- </x:template> -->

  <x:template match="cc:subsection">
    <x:message>The ID is <x:value-of select="@id"/></x:message>
    <h3 id="{@id}" class="indexable" data-level="{count(ancestor::*)-1}">
      <x:value-of select="@title" />
    </h3>
    <x:apply-templates select="cc:*"/>
  </x:template>
  
  <x:template match="cc:f-component | cc:a-component">
    <div class="comp" id="{translate(@id, $lower, $upper)}">
      <h4>
	<x:value-of select="concat(translate(@id, $lower, $upper), ' ')"/>
	<x:value-of select="@name"/>
      </h4>
      <x:apply-templates select=".//cc:aactivity"/> 
    </div>
  </x:template>

  <!-- Makes a ref to requirement -->
  <x:template name="req-refs">
    <!-- Optional css classes -->
    <x:param name="class"/>
    <!-- Requirement id -->
    <x:param name="req"/>

    <!--lower req-->
    <x:variable name="lreq">
      <x:value-of select="translate($req,$upper,$lower)"/>
    </x:variable>

    <!--Uppercase req -->
    <x:variable name="capped-req">
      <x:value-of select="translate($lreq,$lower,$upper)"/>
    </x:variable>
    
    <a class="{$class}" href="#{$capped-req}"><x:value-of select="$capped-req"/></a>
  </x:template>

  <x:template name="bases">Base-PP<x:if test="/cc:PP/cc:module/cc:base-p[1]">s</x:if></x:template>
</x:stylesheet>
