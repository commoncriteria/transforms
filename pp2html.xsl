<?xml version="1.0" encoding="utf-8"?>
<!--
    Stylesheet for Protection Profile Schema
    Based on original work by Dennis Orth
    Subsequent modifications in support of US NIAP
-->

<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:cc="https://niap-ccevs.org/cc/v1"
  xmlns="http://www.w3.org/1999/xhtml"
  xmlns:htm="http://www.w3.org/1999/xhtml"
  version="1.0">

  <xsl:param name="appendicize" select="''"/>

  <xsl:param name="custom-css-file" select="''"/>

 
  <!-- very important, for special characters and umlauts iso8859-1-->
  <xsl:output method="xml" encoding="UTF-8"/>

  <!-- Put all common templates into ppcommons.xsl -->
  <!-- They can be redefined/overridden  -->
  <xsl:include href="ppcommons.xsl"/>

  <xsl:include href="boilerplates.xsl"/>
<!-- ############### -->
<!--            -->
  <xsl:template match="/">
    <!-- Start with !doctype preamble for valid (X)HTML document. -->
    <xsl:text disable-output-escaping='yes'>&lt;!DOCTYPE html&gt;&#xa;</xsl:text>
    <html xmlns="http://www.w3.org/1999/xhtml">
      <xsl:call-template name="head"/>
      <body onLoad="init()">
          <xsl:call-template name="sanity-checks"/>

	<xsl:call-template name="body-begin"/>
	<xsl:apply-templates select="cc:*"/>
      </body>
    </html>
  </xsl:template>

<!-- ############### -->
<!--            -->
  <xsl:template match="cc:PP">
    <xsl:apply-templates select="cc:chapter"/>
    <xsl:call-template name="first-appendix"/>
    <xsl:call-template name="selection-based-appendix"/>
    <xsl:apply-templates select="cc:appendix"/>
  </xsl:template>

<!-- ############### -->
<!--            -->
  <xsl:template match="cc:usecases">
    <dl>
      <xsl:for-each select="cc:usecase">
        <dt> [USE CASE <xsl:value-of select="position()"/>] <xsl:value-of select="@title"/></dt>
        <dd>
          <xsl:apply-templates select="cc:description"/>
        </dd>
      </xsl:for-each>
    </dl>
  </xsl:template>
<!-- ############### -->
<!--            -->
  <xsl:template match="cc:glossary">
    <table>
      <xsl:for-each select="cc:entry">
        <xsl:element name="tr">

	  <!-- Adding this attribute was causing ID errors since it was often empty,
         and it's not clear that it is used for anything.  
    <xsl:attribute name="id">
	    <xsl:choose>
	      <xsl:when test="@id"><xsl:value-of select="@id"/></xsl:when>
	      <xsl:when test="cc:term"><xsl:value-of select="translate(cc:term/text(), $lower, $upper)"/></xsl:when>
	      <xsl:otherwise><xsl:value-of select="name/text()"/></xsl:otherwise>
	    </xsl:choose>
	  </xsl:attribute> -->
          <td>
            <xsl:apply-templates select="cc:term"/>
          </td>
          <td>
            <xsl:apply-templates select="cc:description"/>
          </td>
	</xsl:element>
      </xsl:for-each>
    </table>
  </xsl:template>

<!-- ############### -->
<!--            -->
  <xsl:template match="cc:glossary/cc:entry/cc:term/cc:abbr">
    <span id="abbr_{text()}"><xsl:value-of select="@title"/> (<abbr><xsl:value-of select="text()"/></abbr>)</span>
  </xsl:template>

  
  <!-- <xsl:template match="cc:abbr[contains(concat('|', translate(@class, ' ', '|'), '|'), '|expanded|')]"> -->
  <!--   <xsl:message>QQQ matching <xsl:value-of select="@title"/></xsl:message> -->
  <!--   <xsl:value-of select="@title"/> (<xsl:copy><xsl:apply-templates select="@*|node()"/></xsl:copy>) -->
  <!-- </xsl:template> -->

<!-- ############### -->
<!--            -->
  <xsl:template match="cc:bibliography">
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

<!-- ############### -->
<!--            -->
  <xsl:template match="cc:acronyms">
    <table>
      <tr class="header">
        <th>Acronym</th>
        <th>Meaning</th>
      </tr>
      <xsl:for-each select="cc:entry">
        <tr>
	  <xsl:for-each select="cc:*"><td><xsl:apply-templates/></td></xsl:for-each>
        </tr>
      </xsl:for-each>
    </table>
  </xsl:template>

<!-- ############### -->
<!--            -->
  <xsl:template match="cc:assumptions">
    <dl>
      <xsl:for-each select="cc:assumption">
        <dt>
          <xsl:value-of select="@id"/>
        </dt>
        <dd>
          <xsl:apply-templates select="cc:description"/>
          <xsl:apply-templates select="cc:appnote"/>
        </dd>
      </xsl:for-each>
    </dl>
  </xsl:template>

<!-- ############### -->
<!--            -->
  <xsl:template match="cc:cclaims">
    <dl>
      <xsl:for-each select="cc:cclaim">
        <dt>
          <xsl:value-of select="@title"/>
        </dt>
        <dd>
          <xsl:apply-templates select="cc:description"/>
          <xsl:apply-templates select="cc:appnote"/>
        </dd>
      </xsl:for-each>
    </dl>
  </xsl:template>
  
<!-- ############### -->
<!-- Appears           -->
  <xsl:template match="cc:if-opt-app">
    <xsl:if test="$appendicize='on'">
      <xsl:apply-templates/>
    </xsl:if>
  </xsl:template>

<!-- ############### -->
<!--            -->
  <xsl:template match="cc:InsertAppendixExplainer">
    <xsl:if test="$appendicize='on'"> Unconditional requirements are found in the main body of the
      document, while appendices contain the selection-based, optional, and objective requirements. </xsl:if>
    <xsl:if test="$appendicize!='on'"> The type of each requirement is identified in line with the
      text. </xsl:if>
  </xsl:template>

<!-- ############### -->
<!--            -->
  <xsl:template match="cc:threats">
    <dl>
      <!-- For -->
      <xsl:for-each select="cc:threat[cc:description]">
        <dt>
          <xsl:value-of select="@id"/>
        </dt>
        <dd>
          <xsl:apply-templates select="cc:description"/>
          <xsl:apply-templates select="cc:appnote"/>
        </dd>
      </xsl:for-each>
    </dl>
  </xsl:template>
<!-- ############### -->
<!--            -->
  <xsl:template match="cc:OSPs">
    <dl>
      <xsl:for-each select="cc:OSP">
        <dt>
          <xsl:value-of select="@id"/>
        </dt>
        <dd>
          <xsl:apply-templates select="cc:description"/>
          <xsl:apply-templates select="cc:appnote"/>
        </dd>
      </xsl:for-each>
    </dl>
  </xsl:template>
<!-- ############### -->
<!--            -->
  <xsl:template match="cc:SOs">
    <dl>
      <xsl:for-each select="cc:SO">
        <dt>
          <xsl:value-of select="@id"/>
        </dt>
        <dd>
          <xsl:apply-templates select="cc:description"/>
          <p/> Addressed by: <span class="SOlist">
            <xsl:for-each select="cc:component-refer">
	      <!-- -->
	      <xsl:variable name="uncapped-req">
		<xsl:value-of select="translate(@ref,$upper,$lower)"/>
	      </xsl:variable>
	      <xsl:choose>

		<!-- if there's a reference and it matches a f-component id -->
		<xsl:when test="//cc:f-component[@id=$uncapped-req]">
		  <xsl:element name="span">
		    <xsl:attribute name="class">
		      <xsl:value-of select="//cc:f-component[@id=$uncapped-req]/@status"/>
		    </xsl:attribute>
		    <xsl:call-template name="req-refs">
                      <xsl:with-param name="req" select="@ref"/>
		    </xsl:call-template>
		    <!--
			This is here so that if we wanted to added text
			but make it different font.
		    -->
		    <span class="after"/>
		</xsl:element>
		</xsl:when>

		<!-- if there's a reference -->
		<xsl:when test="@ref">
		  <span class="external-ref"><xsl:value-of select="@ref"/></span>
		</xsl:when>

		<!-- if there's no reference, just shove in whatever -->
		<xsl:otherwise>
		  <xsl:apply-templates/>
		</xsl:otherwise>
	      </xsl:choose>
		<xsl:call-template name="commaifnotlast"/>
            </xsl:for-each>
          </span>
          <xsl:apply-templates select="cc:appnote"/></dd>
      </xsl:for-each>
    </dl>
  </xsl:template>
<!-- ############### -->
<!--            -->
  <xsl:template match="cc:SOEs">
    <dl>
      <xsl:for-each select="cc:SOE">
        <dt>
          <xsl:value-of select="@id"/>
        </dt>
        <dd>
          <xsl:apply-templates select="cc:description"/>
          <xsl:apply-templates select="cc:appnote"/>
        </dd>
      </xsl:for-each>
    </dl>
  </xsl:template>
<!-- ############### -->
<!--            -->
  <xsl:template match="cc:InsertSPDCorrespondence">
    <table>
      <tr class="header">
        <td>Threat, Assumption, or OSP</td>
        <td>Security Objectives</td>
        <td>Rationale</td>
      </tr>
      <xsl:for-each select="(//cc:threat | //cc:OSP | //cc:assumption)">
        <tr>
          <td>
            <xsl:value-of select="@id"/>
          </td>
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


  <!-- Used to match regular ?-components -->
  <!-- ############### -->
  <!--            -->
  <xsl:template match="cc:f-component | cc:a-component">
    <div class="comp" id="{translate(@id, $lower, $upper)}">
      <h4>
        <xsl:value-of select="concat(translate(@id, $lower, $upper), ' ')"/>
        <xsl:value-of select="@name"/>
      </h4>

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
      <xsl:if test=".//cc:selection-depends">
        <div class="statustag">
          <b><i>This is a selection-based component. Its inclusion depends upon selection from
          <xsl:for-each select="cc:selection-depends">
            <b><i>
              <xsl:call-template name="req-refs">
                <xsl:with-param name="req" select="@req"/>
              </xsl:call-template>
              <xsl:call-template name="commaifnotlast"/>
            </i></b>
            </xsl:for-each>.
          </i></b>
        </div>
      </xsl:if>

      <xsl:if test="@status='optional'">
        <div class="statustag">
          <i><b>This is an optional component. However, applied modules or packages might redefine it as mandatory.</b></i>
        </div>
      </xsl:if>

      <xsl:apply-templates/>
    </div>
  </xsl:template>

<xsl:template match="cc:f-component | cc:a-component" mode="appendicize">
  <!-- in appendicize mode, don't display objective/sel-based/optional in main body-->
  <xsl:if test="not(@status) or (@status!='optional' and @status!='sel-based' and @status!='objective')">
    <xsl:apply-templates select="self::node()" mode="appendicize-nofilter" />
  </xsl:if>
</xsl:template>

<xsl:template match="cc:f-component | cc:a-component" mode="appendicize-nofilter">
  <div class="comp" id="{translate(@id, $lower, $upper)}">
    <h4>
      <xsl:value-of select="concat(translate(@id, $lower, $upper), ' ')"/>
      <xsl:value-of select="@name"/>
    </h4>

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
          <b><i>This selection-based component depends upon selection in
              <xsl:for-each select="cc:selection-depends">
                <b><i>
                  <xsl:variable name="capped-req"><xsl:value-of select="translate(@ref,$lower,$upper)"/></xsl:variable>
                  <xsl:call-template name="req-refs">
                    <xsl:with-param name="req" select="@req"/>
                  </xsl:call-template>
                  <!--                <xsl:if test="position() != last()"><xsl:text>, </xsl:text></xsl:if>-->
                  <xsl:call-template name="commaifnotlast"/>
                </i></b>
              </xsl:for-each>. </i>
            </b>
          </div>
        </xsl:if>
        <xsl:apply-templates/>
      </div>
  </xsl:template>

<!-- ############### -->
<!--            -->
  <xsl:template match="cc:f-element | cc:a-element" >
    <div class="element">
      <xsl:variable name="reqid" select="translate(@id, $lower, $upper)"/>
      <div class="reqid" id="{$reqid}">
        <a href="#{$reqid}" class="abbr">
          <xsl:value-of select="$reqid"/>
        </a>
      </div>
      <div class="reqdesc">
        <xsl:apply-templates/>
      </div>
    </div>
  </xsl:template>

<!-- ############### -->
<!--            -->
  <xsl:template match="cc:evalactionlabel">
    <h4><xsl:value-of select="@title"/></h4>
  </xsl:template>
  
<!-- ############### -->
<!--            -->
  <xsl:template match="cc:foreword">
    <div class="foreword">
      <h1 style="text-align: center">Foreword</h1>
      <xsl:apply-templates/>
    </div>
  </xsl:template>


<!-- ############### -->
<!--            -->
  <xsl:template match="cc:title">
    <xsl:apply-templates/>
  </xsl:template>

<!-- ############### -->
<!--            -->
  <xsl:template match="cc:aactivity"> <!-- should change this to cc:evalactivity-->
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
  </xsl:template>

<!-- ############### -->
<!--            -->
  <xsl:template match="cc:indent">
    <div class="indent" style="margin-left:2em">
      <xsl:apply-templates/>
    </div>
  </xsl:template>





<!-- ############### -->
<!--                 -->
    <xsl:template match="cc:appendix[@title='Optional Requirements']"/>
    <xsl:template match="cc:appendix[@title='Selection-Based Requirements']"/>
    <xsl:template match="cc:appendix[@title='Objective Requirements']"/>


<!-- ############### -->
<!--                 -->
    <xsl:template name="first-appendix">
        <xsl:choose>
            <xsl:when test="$appendicize='on'">
                <h1 id="{@id}" class="indexable" data-level="A">Optional Requirements</h1>
                <xsl:call-template name="opt_appendix"/>
                <h2 id="strict-opt-reqs" class="indexable" data-level="2">Strictly Optional Requirements</h2>
                <xsl:apply-templates select="//cc:*[@status='optional']" mode="appendicize-nofilter"/>
                <h2 id="obj-reqs" class="indexable" data-level="2">Objective Requirements</h2>
                <xsl:apply-templates select="//cc:*[@status='objective']" mode="appendicize-nofilter"/>
                <h2 id="impl-reqs" class="indexable" data-level="2">Implementation-Dependent Requirements</h2>
            </xsl:when>
            <xsl:otherwise>
                <h1 id="impl-reqs" class="indexable" data-level="A">Implementation-Dependent Requirements</h1>
This appendix enumerates requirements <xsl:call-template name="imple_text"/>
            </xsl:otherwise>
        </xsl:choose>
        <xsl:if test="count(//cc:implements/cc:feature)=0">
This PP does not define any Implementation-Dependent Requirements.
        </xsl:if>
        <xsl:for-each select="//cc:implements/cc:feature">
            <xsl:variable name="fid"><xsl:value-of select="@id"/></xsl:variable>
            <h3 id="{@id}"><xsl:value-of select="@name"/></h3>
            <xsl:value-of select="cc:text"/>
            <xsl:apply-templates select="//cc:*/cc:depends[@on=$fid]/.."/>
        </xsl:for-each>


    </xsl:template>

<!-- ############### -->
<!--                 -->
    <xsl:template name="selection-based-appendix">
        <xsl:if test="$appendicize='on'">
            <h1 id="sel-based-reqs" class="indexable" data-level="A">Selection-Based Requirements</h1>
            <xsl:call-template name="selection-based-text"/>
            <xsl:apply-templates select="//cc:*[@status='sel-based']" mode="appendicize-nofilter"/>
        </xsl:if>
    </xsl:template>
  
<!-- ############### -->
<!--                 -->
  <xsl:template match="cc:appendix">
    <h1 id="{@id}" class="indexable" data-level="A"><xsl:value-of select="@title"/></h1>
      <!-- insert SFRs for "special" appendices, if @id is one of the "special" ones-->
    <xsl:apply-templates select="." mode="hook"/>
    <xsl:apply-templates/>
  </xsl:template>

<!-- ############### -->
<!--            -->
  <xsl:template match="cc:chapter">
    <h1 id="{@id}" class="indexable" data-level="1"><xsl:value-of select="@title"/></h1>
    <xsl:apply-templates mode='hook' select='.'/>
    <xsl:apply-templates/>
  </xsl:template>



<!-- ############### -->
<!--            -->
  <xsl:template match="cc:section">
    <h2 id="{@id}" class="indexable" data-level="2"><xsl:value-of select="@title"/></h2>
    <xsl:apply-templates mode="hook" select="."/>
    <xsl:apply-templates/>
  </xsl:template>


<!-- ############### -->
<!--            -->
  <xsl:template match="cc:subsection">
    <!-- the "if" statement is to not display subsection headers when there are no
    subordinate mandatory components to display in the main body (when in "appendicize" mode) -->
    <xsl:if test="$appendicize!='on' or count(./cc:f-component)=0 or count(.//cc:f-component[not(@status) or @status='threshold'])">
      <h3 id="{@id}" class="indexable" data-level="{count(ancestor::*)}"><xsl:value-of select="@title" /></h3>
      <xsl:apply-templates mode="hook" select="."/>
      <xsl:if test="$appendicize = 'on'">
        <xsl:apply-templates mode="appendicize" />
      </xsl:if>
      <xsl:if test="$appendicize != 'on'">
        <xsl:apply-templates />
      </xsl:if>
    </xsl:if>
  </xsl:template>

<!-- ############### -->
<!--            -->
  <xsl:template match="cc:ctr-ref">
    <a onclick="showTarget('cc-{@refid}')" href="#cc-{@refid}" class="cc-{@refid}-ref" >
      <xsl:variable name="refid"><xsl:value-of select="@refid"></xsl:value-of></xsl:variable>
      <!-- should only run through once, but this is how we're changing contexts -->
      <xsl:for-each select="//cc:ctr[@id=$refid]">
	<xsl:call-template name="getPre"/>
      </xsl:for-each>
 <!--      <xsl:value-of select="//cc:ctr[@id=$refid]/@pre"/> -->
      <span class="counter"><xsl:value-of select="$refid"/></span>
    </a>
  </xsl:template>

  <!-- Need at least two objects -->
<!-- ############### -->
<!--            -->
  <xsl:template match="cc:ctr">
    <xsl:variable name="ctrtype"><xsl:choose>
	<xsl:when test="@ctr-type"><xsl:value-of select="@ctr-type"/></xsl:when>
	<xsl:otherwise><xsl:value-of select="@pre"/></xsl:otherwise></xsl:choose>
    </xsl:variable>

    <span class="ctr" data-myid="cc-{@id}" data-counter-type="ct-{$ctrtype}" id="cc-{@id}">
      <xsl:call-template name="getPre"/>
      <span class="counter"><xsl:value-of select="@id"/></span>
      <xsl:apply-templates/>
    </span>
  </xsl:template>

<!-- ############### -->
<!--            -->
  <xsl:template match="cc:figref">
    <a onclick="showTarget('figure-{@refid}')" href="#figure-{@refid}" class="figure-{@refid}-ref">
      <xsl:variable name="refid"><xsl:value-of select="@refid"></xsl:value-of></xsl:variable>

      <xsl:for-each select="//cc:figure[@id=$refid]">
	<xsl:call-template name="getPre"/>
      </xsl:for-each>
<!--      <xsl:value-of select="//cc:ctr[@id=$refid]">"/>-->
      <span class="counter"><xsl:value-of select="$refid"/></span>
    </a>
  </xsl:template>

<!-- ############### -->
<!--            -->
  <xsl:template match="cc:figure">
    <div class="figure" id="figure-{@id}">
      <img id="{@id}" src="{@entity}" width="{@width}" height="{@height}" />
      <p/>
      <span class="ctr" data-myid="figure-{@id}" data-counter-type="ct-figure">
	<xsl:call-template name="getPre"/>
	<span class="counter"><xsl:value-of select="@id"/></span>
      </span>:
      <xsl:value-of select="@title"/>
    </div>
  </xsl:template>

<!-- ############### -->
<!--            -->
  <xsl:template name="getPre">
    <xsl:choose>
      <xsl:when test="@pre"><xsl:value-of select="@pre"/></xsl:when>
      <xsl:when test="name()='figure'"><xsl:text>Figure </xsl:text></xsl:when>
      <xsl:when test="@ctr-type"><xsl:value-of select="@ctr-type"/><xsl:text>  </xsl:text></xsl:when>
      <xsl:otherwise><xsl:text>Table </xsl:text></xsl:otherwise>
    </xsl:choose>
  </xsl:template>


<!-- ############### -->
  <xsl:template match="cc:TSS|cc:Guidance|cc:Tests">
    <div class="eacategory"><xsl:value-of select="name()"/></div>
    <xsl:apply-templates/>
  </xsl:template>


  <!-- templates for creating references -->
  <!-- Assumes element with matching @id has a @title. -->
<!-- ############### -->
<!--            -->
  <xsl:template match="cc:xref">
    <xsl:variable name="linkendorig" select="@linkend"/>
    <xsl:variable name="linkend" select="translate(@linkend,$lower,$upper)"/>
    <xsl:variable name="linkendlower" select="translate(@linkend,$upper,$lower)"/>
    <xsl:element name="a">
      <xsl:attribute name="onclick">showTarget('<xsl:value-of select="$linkend"/>')</xsl:attribute>
      <xsl:attribute name="href">
        <xsl:text>#</xsl:text>
        <xsl:value-of select="$linkend"/>
      </xsl:attribute>
      <xsl:choose>
        <xsl:when test="text()"><xsl:value-of select="text()"/></xsl:when>
	<xsl:when test="//*[@id=$linkendlower]/@title">
	  <xsl:value-of select="//*[@id=$linkendlower]/@title"/>
	</xsl:when>
	<xsl:when test="//*[@id=$linkendlower]/@name">
	  <xsl:value-of select="//*[@id=$linkendlower]/@name"/>
	</xsl:when>
	<xsl:when test="//*[@id=$linkendlower]/cc:term">
	  <xsl:value-of select="//*[@id=$linkendlower]/cc:term"/>
	</xsl:when>
	<xsl:when test="//*/cc:term[text()=$linkendorig]">
	  <xsl:value-of select="$linkendorig"/>
	</xsl:when>
	<xsl:otherwise>
	  <xsl:message>Cant find
	  <xsl:value-of select="$linkendlower"/>
	  </xsl:message>
	</xsl:otherwise>
      </xsl:choose>
    </xsl:element>
  </xsl:template>

<!-- ############### -->
<!--            -->
  <xsl:template match="cc:linkref">
    <xsl:call-template name="req-refs">
      <xsl:with-param name="class">linkref</xsl:with-param>
      <xsl:with-param name="req">
        <xsl:value-of select="translate(@linkend, $upper, $lower)"/>
      </xsl:with-param>
    </xsl:call-template>
  </xsl:template>

<!-- ############### -->
<!--            -->
  <xsl:template match="cc:secref">
    <a href="#{@linkend}" class="dynref">Section </a>
  </xsl:template>


<!-- ############### -->
<!--            -->
  <xsl:template match="cc:appref">
    <a href="#{@linkend}" class="dynref"></a>
    <!-- <a href="#{@linkend}" class="dynref">Appendix </a> -->
  </xsl:template>

<!-- ############### -->
<!--            -->
  <xsl:template match="cc:chapter | cc:section | cc:subsection | cc:appendix" mode="secreflookup">
    <xsl:param name="linkend"/>
    <xsl:param name="prefix"/>
    <!-- make the identifier a letter or number as appropriate for appendix or chapter/section -->
    <xsl:variable name="pos">
      <xsl:choose>
        <xsl:when test="name()='appendix'">
          <xsl:choose>
            <xsl:when test="$appendicize='on'">
              <xsl:number format="A"/>
            </xsl:when>
            <xsl:otherwise>
              <xsl:number format="A"
                count="cc:appendix[@id!='optional' and @id!='objective' and @id!='sel-based']"/>
            </xsl:otherwise>
          </xsl:choose>
        </xsl:when>
        <xsl:otherwise>
          <xsl:number/>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:if test="@id=$linkend">
      <xsl:value-of select="concat($prefix,$pos)"/>
    </xsl:if>
    <xsl:if test="./cc:chapter | ./cc:section | ./cc:subsection">
      <xsl:apply-templates mode="secreflookup"
        select="./cc:chapter | ./cc:section | ./cc:subsection">
        <xsl:with-param name="linkend" select="$linkend"/>
        <xsl:with-param name="prefix" select="concat($prefix,$pos,'.')"/>
      </xsl:apply-templates>
    </xsl:if>
  </xsl:template>


<!-- ############### -->
<!--            -->
  <xsl:template match="cc:citeCC"><a href="#bibCC">[CC]</a></xsl:template>

<!-- ############### -->
<!--            -->
  <xsl:template match="cc:util">
    <span class="util">
      <xsl:apply-templates/>
    </span>
  </xsl:template>

<!-- ############### -->
<!--            -->
  <xsl:template match="cc:path">
    <span class="path">
      <xsl:apply-templates/>
    </span>
  </xsl:template>



  
  <!-- identity transform - useful for debugging -->

<!-- ############### -->
<!--                 -->
  <xsl:template match="@*|node()">
    <!-- <xsl:message>Unmatched element caught by identity transform: <xsl:value-of select ="name()"/></xsl:message> -->
    <xsl:copy>
      <xsl:apply-templates select="@*|node()"/>
    </xsl:copy>
  </xsl:template>

  <!-- if no template matches when the mode is set to appendicize,
       default to a template without the mode set.  this may default
       to calling the identity transform above -->


<!-- ############### -->
<!--                 -->
  <xsl:template match="@*|node()" mode="appendicize">
      <xsl:apply-templates select="current()" />
  </xsl:template>




</xsl:stylesheet>


