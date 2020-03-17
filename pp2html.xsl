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

  <xsl:variable name="doctype" select="pp"/>

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
<!--    <xsl:call-template name="first-appendix"/>   -->
    <xsl:call-template name="optional-appendix"/>
    <xsl:call-template name="selection-based-appendix"/>
    <xsl:call-template name="objective-appendix"/>
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
  <xsl:template match="cc:assumptions">
    <dl>
      <xsl:for-each select="cc:assumption">
        <dt>
          <xsl:value-of select="@name"/>
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
  <xsl:template match="cc:threats">
    <dl>
      <!-- For -->
      <xsl:for-each select="cc:threat[cc:description]">
        <dt>
          <xsl:value-of select="@name"/>
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
          <xsl:value-of select="@name"/>
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
    <xsl:choose>
      <xsl:when test="cc:SO[cc:description]">
        <dl>
          <xsl:for-each select="cc:SO[cc:description]">
            <dt><xsl:value-of select="@name"/></dt>
            <dd>
              <p><xsl:apply-templates select="cc:description"/></p>
              Addressed by: <span class="SOlist">
                <xsl:apply-templates select="cc:addressed-by"/>
              </span>
            <xsl:apply-templates select="cc:appnote"/></dd>
          </xsl:for-each>
        </dl>
      </xsl:when>
      <xsl:otherwise>
        This CC-Module does not define any new security objectives.
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

<!-- ############### -->
<!--            -->
  <xsl:template match="cc:SOEs">
    <dl>
      <xsl:for-each select="cc:SOE">
        <dt>
          <xsl:value-of select="@name"/>
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
  <xsl:template match="cc:audit-table[cc:depends]">
      <div class="dependent"> The following audit events are included if:
         <ul> <xsl:for-each select="cc:depends">
            <li>
            <xsl:if test="@on='selection'">
              <xsl:for-each select="cc:uid">  
                <xsl:variable name="uid" select="text()"/>
                "<xsl:apply-templates select="//cc:selectable[@id=$uid]"/>"
              </xsl:for-each>
               is selected from 
              <xsl:variable name="uid" select="cc:uid[1]/text()"/>
              <xsl:apply-templates select="//cc:f-element[.//cc:selectable/@id=$uid]" mode="getId"/>
            </xsl:if> 
            <xsl:if test="@on='implements'">
              the TOE implements 
              <xsl:variable name="ref-id" select="@ref-id"/>
              "<xsl:value-of select="//cc:feature[@id=$ref-id]/@title"/>"
            </xsl:if>
            </li>
        </xsl:for-each> </ul><br/>
        <xsl:call-template name="audit-table"/>
      </div>        
  </xsl:template>

  <xsl:template match="cc:audit-table" name="audit-table">
    <xsl:variable name="thistable" select="@table"/>
    <xsl:apply-templates/>
    <table class="" border="1">
    <tr><th>Requirement</th>
        <th>Auditable Events</th>
        <th>Additional Audit Record Contents</th></tr>
    <xsl:for-each select="//cc:f-component">
	<xsl:variable name="fcomp" select="."/>
        <xsl:for-each select="cc:audit-event"> 
            <!-- The audit event is included in this table only if
                - The audit event's expressed table attribute matches this table
                - Or the table attribute is not expressed and the audit event's default audit attribute matches this table.
                - The default table for an audit event is the same as the status attribute of the enclosing f-component.  -->
            <xsl:if test="(@table=$thistable) or ((not(@table)) and ($fcomp/@status=$thistable))">
                <tr>
                    <td><xsl:apply-templates select="$fcomp" mode="getId"/></td>      <!-- SFR name -->
                    <xsl:choose>
                        <xsl:when test="(not (cc:audit-event-descr))">
                            <td>No events specified</td><td></td>
                        </xsl:when>
                        <xsl:otherwise>
                            <xsl:choose>
				<!-- When audit events are individually selectable -->
                                <xsl:when test="@type='optional'">
					<td> <b>[selection:</b><i> <xsl:apply-templates select="cc:audit-event-descr"/>, None</i><b>]</b> </td>
                                </xsl:when>
                                <xsl:otherwise>
                                   <td><xsl:apply-templates select="cc:audit-event-descr"/></td>
                                </xsl:otherwise>
                            </xsl:choose>
                            <td>
				<xsl:for-each select="cc:audit-event-info">
		 			<xsl:apply-templates select="."/> <br />  <!-- mode="intable"  --> 
				</xsl:for-each>
			    </td>
                        </xsl:otherwise>
                    </xsl:choose>
               </tr>
            </xsl:if>
        </xsl:for-each>
    </xsl:for-each>
    </table>
  </xsl:template>

<!-- ############### -->
<!--            -->
  <xsl:template match="cc:audit-event-info" mode="intable">
	<xsl:choose>
	    <xsl:when test="@type='optional'">
		    <b>[selection:</b>
		    <i><xsl:apply-templates select="cc:audit-event-info"/>
			    , None</i><b>]</b>
	    </xsl:when>
	    <xsl:otherwise>
			<xsl:apply-templates select="cc:audit-event-info"/>
	    </xsl:otherwise>
	  </xsl:choose>
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

        <xsl:message> <xsl:value-of select="name()"/><xsl:value-of select="@name"/></xsl:message>
      <xsl:for-each select="(//cc:threat | //cc:OSP | //cc:assumption)">
        <xsl:message> <xsl:value-of select="name()"/><xsl:value-of select="@name"/></xsl:message>
        <tr>
          <td>
 
            <xsl:value-of select="@name"/>
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


  <!-- ############### -->
  <!--            -->
  <xsl:template match="cc:a-component">
    <div class="comp" id="{translate(@id, $lower, $upper)}">
      <h4>
        <xsl:value-of select="concat(translate(@id, $lower, $upper), ' ')"/>
        <xsl:value-of select="@name"/>
      </h4>
      <xsl:call-template name="agroup"><xsl:with-param name="type">D</xsl:with-param></xsl:call-template>
      <xsl:call-template name="agroup"><xsl:with-param name="type">C</xsl:with-param></xsl:call-template>
      <xsl:call-template name="agroup"><xsl:with-param name="type">E</xsl:with-param></xsl:call-template>
    </div>
  </xsl:template>

  <!-- ############### -->
  <!--            -->
  <xsl:template name="agroup">
    <xsl:param name="type"/>
    <xsl:if test="./cc:a-element[@type=$type]">
        <h4><xsl:choose>
           <xsl:when test="$type='D'">Developer action</xsl:when>
           <xsl:when test="$type='C'">Content and presentation</xsl:when>
           <xsl:when test="$type='E'">Evaluator action</xsl:when>
        </xsl:choose> elements: </h4>
        <xsl:apply-templates select="./cc:a-element[@type=$type]"/>
    </xsl:if>
  </xsl:template>

  <!-- Used to match regular f-components -->
  <!-- ############### -->
  <!--            -->
  <xsl:template match="cc:f-component">
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
      <xsl:if test=".//cc:selection-depends">
        <div class="statustag">
          <b><i>This is a selection-based component. Its inclusion depends upon selection from
          <xsl:for-each select="cc:selection-depends">
            <b><i>
              <xsl:variable name="refid" select="@req"/>
              <xsl:apply-templates select="//cc:f-element[@id=$refid]" mode="getId"/>
              <xsl:call-template name="commaifnotlast"/>
            </i></b>
            </xsl:for-each>.
          </i></b>
        </div>
      </xsl:if>
      <xsl:if test="./cc:depends[@on='implements']">
        <div class="statustag">
          <i><b>This is an implementation-based component.
                Its inclusion depends on whether the TOE implements one (or more) of
                <ul>
                  <xsl:for-each select="cc:depends[@on='implements']">
                    <xsl:variable name="ref-id"><xsl:value-of select="@ref-id"/></xsl:variable>
                    <li><a href="#{@ref-id}"><xsl:value-of select="//cc:feature[@id=$ref-id]/@title"/></a></li>
                  </xsl:for-each>
                </ul>
                as described in Appendix A: Implementation-based Requirements.
        </b></i>
        </div>
      </xsl:if>
      <xsl:if test="@status='optional'">
        <!--  <div class="statustag">
          <i><b>This is an optional component. However, applied modules or packages might redefine it as mandatory.</b></i>
        </div>-->
      </xsl:if>
      <xsl:apply-templates/>
    </div>
  </xsl:template>


  <!-- ############### -->
  <!--            -->
  <xsl:template match="cc:f-component" mode="appendicize">
  <!-- in appendicize mode, don't display objective/sel-based/optional in main body-->
    <xsl:if test="(not(@status) and count(./cc:depends)=0) or (@status!='optional' and @status!='sel-based' and @status!='objective')">
      <xsl:apply-templates select="self::node()" mode="appendicize-nofilter" />
    </xsl:if>
  </xsl:template>

  <!-- ############### -->
  <!--            -->
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
  <xsl:template match="cc:f-element" >
    <div class="element">
      <xsl:variable name="reqid"><xsl:apply-templates select="." mode="getId"/></xsl:variable>
      <div class="reqid" id="{$reqid}">
        <a href="#{$reqid}" class="abbr"><xsl:value-of select="$reqid"/></a>
      </div>
      <div class="reqdesc">
        <xsl:apply-templates/>
      </div>
    </div>
  </xsl:template>

<!-- ############### -->
<!--            -->
  <xsl:template match="cc:a-element" >
    <div class="element">
      <xsl:variable name="type"><xsl:value-of select="@type"/></xsl:variable>
      <xsl:variable name="reqid"><xsl:apply-templates select="." mode="getId"/></xsl:variable>
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
  <xsl:template match="cc:aactivity-sar"> <!-- should change this to cc:evalactivity-->
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
    <xsl:template name="handle-features">
        <xsl:for-each select="//cc:implements/cc:feature">
          <xsl:variable name="fid"><xsl:value-of select="@id"/></xsl:variable>
          <xsl:variable name="level"><xsl:if test="$appendicize='on'">3</xsl:if><xsl:if test="$appendicize!='on'">2</xsl:if></xsl:variable>
          <h3 class="indexable" data-level="{$level}" id="{@id}"><xsl:value-of select="@title"/></h3>
          <xsl:apply-templates select="cc:description"/>
          <xsl:if test="$appendicize='on'">
             <xsl:for-each select="//cc:subsection/cc:f-component/cc:depends[@on='implements' and @ref-id=$fid]/../..">
                <h3 id="{@id}-impl" class="indexable" data-level="{$level+1}"><xsl:value-of select="@title" /></h3>
                <xsl:apply-templates select="cc:f-component/cc:depends[@on='implements' and @ref-id=$fid]/.."
                    mode="appendicize-nofilter"/>
             </xsl:for-each>
          </xsl:if>
        </xsl:for-each>
    </xsl:template>


<!-- ############### -->
<!--                 -->
    <xsl:template name="first-appendix">
        <xsl:choose>
            <xsl:when test="$appendicize='on'">
                <xsl:call-template name="opt_appendix"/>
                <h2 id="strict-opt-reqs" class="indexable" data-level="2">Strictly Optional Requirements</h2>
                <xsl:for-each select="//cc:subsection[cc:f-component/@status='optional']">
                  <h3 id="{@id}-opt" class="indexable" data-level="3"><xsl:value-of select="@title" /></h3>
                  <xsl:apply-templates select="cc:f-component[@status='optional']"/>
                </xsl:for-each>

                <h2 id="obj-reqs" class="indexable" data-level="2">Objective Requirements</h2>
                <xsl:for-each select="//cc:subsection[cc:f-component/@status='objective']">
                  <h3 id="{@id}-obj" class="indexable" data-level="3"><xsl:value-of select="@title" /></h3>
                  <xsl:apply-templates select="cc:f-component[@status='objective']" mode="appendicize-nofilter"/>
                </xsl:for-each>

                <h2 id="impl-reqs" class="indexable" data-level="2">Implementation-Dependent Requirements</h2>
                <xsl:call-template name="handle-features"><xsl:with-param name="level">3</xsl:with-param></xsl:call-template>
            </xsl:when>
            <xsl:otherwise>
                <h1 id="impl-reqs" class="indexable" data-level="A">Implementation-Dependent Requirements</h1>
This appendix enumerates requirements <xsl:call-template name="imple_text"/>
                <xsl:call-template name="handle-features"><xsl:with-param name="level">2</xsl:with-param></xsl:call-template>
            </xsl:otherwise>
        </xsl:choose>

        <xsl:if test="count(//cc:implements/cc:feature)=0">
          <p>This PP does not define any implementation-dependent requirements.</p>
        </xsl:if>
    </xsl:template>

<!-- ############### -->
<!--                 -->
    <xsl:template name="optional-appendix">
	<xsl:variable name="found" select="false"/> 
        <xsl:if test="$appendicize='on'">
            <h1 id="optional-reqs" class="indexable" data-level="A">Optional Requirements</h1>
            <xsl:call-template name="optional-text"/>
	    <!-- Loop through all components picking out the optional. 
		 Might want to set a flag increment a counter -->
	    <xsl:for-each select="//cc:subsection[cc:f-component]">
		<xsl:if test="@status='optional'"> 
		  <xsl:variable name="found" select="true"/>
                  <xsl:apply-templates select="." />
		</xsl:if>
            </xsl:for-each>
	    <xsl:if test="$found='false'">
              <p>This PP does not define any optional requirements.</p>
	    </xsl:if>
	</xsl:if>
    </xsl:template>

<!-- ############### -->
<!--                 -->
    <xsl:template name="selection-based-appendix">
	<xsl:variable name="found" select="false"/> 
        <xsl:if test="$appendicize='on'">
            <h1 id="sel-based-reqs" class="indexable" data-level="A">Selection-Based Requirements</h1>
            <xsl:call-template name="selection-based-text"/>
            <xsl:for-each select="//cc:subsection[cc:f-component]">
	       <xsl:if test="@status='sel-based'">
	           <xsl:variable name="found" select="true"/>
	           <xsl:apply-templates select="."/>
	       </xsl:if>
            </xsl:for-each>
	    <xsl:if test="$found='false'">
              <p>This PP does not define any selection-based requirements.</p>
	    </xsl:if>
        </xsl:if>
    </xsl:template>

	
<!-- ############### -->
<!--                 -->
    <xsl:template name="objective-appendix">
	<xsl:variable name="found" select="false"/> 
        <xsl:if test="$appendicize='on'">
            <h1 id="sel-based-reqs" class="indexable" data-level="A">Objective Requirements</h1>
            <xsl:call-template name="objective-text"/>
            <xsl:for-each select="//cc:subsection[cc:f-component]">
		<xsl:if test="@status='objective'">
    	            <xsl:variable name="found" select="true"/>
	            <xsl:apply-templates select="cc:f-component[cc:selection-depends]"/>
		</xsl:if>
            </xsl:for-each>
	    <xsl:if test="$found='false'">
              <p>This PP does not define any objective requirements.</p>
	    </xsl:if>
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
<!--    <xsl:if test="$appendicize!='on' or count(./cc:f-component)=0 or count(.//cc:f-component[not(@status)])">  -->
      <h3 id="{@id}" class="indexable" data-level="{count(ancestor::*)}"><xsl:value-of select="@title" /></h3>
      <xsl:apply-templates mode="hook" select="."/>
      <xsl:if test="$appendicize = 'on'">
        <xsl:apply-templates mode="appendicize" />
      </xsl:if>
      <xsl:if test="$appendicize != 'on'">
        <xsl:apply-templates />
      </xsl:if>
<!--    </xsl:if>  -->
  </xsl:template>

<!-- ############### -->
<!--            -->
  <xsl:template match="cc:ctr-ref">
    <a onclick="showTarget('cc-{@refid}')" href="#cc-{@refid}" class="cc-{@refid}-ref" >
      <xsl:variable name="refid"><xsl:value-of select="@refid"/></xsl:variable>
      <!-- should only run through once, but this is how we're changing contexts -->
 <!--      <xsl:value-of select="//cc:ctr[@id=$refid]/@pre"/> -->
      <xsl:apply-templates select="//cc:ctr[@id=$refid]" mode="getPre"/>
      <span class="counter"><xsl:value-of select="$refid"/></span>
      <xsl:apply-templates/>
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
      <xsl:apply-templates select="." mode="getPre"/>
      <span class="counter"><xsl:value-of select="@id"/></span>
      <xsl:apply-templates/>
    </span>
  </xsl:template>

<!-- ############### -->
<!--            -->
  <xsl:template match="cc:figref">
    <a onclick="showTarget('figure-{@refid}')" href="#figure-{@refid}" class="figure-{@refid}-ref">
      <xsl:variable name="refid"><xsl:value-of select="@refid"></xsl:value-of></xsl:variable>
      <xsl:apply-templates select="//cc:figure[@id=$refid]" mode="getPre"/>
<!--      <xsl:value-of select="//cc:ctr[@id=$refid]">"/>-->
      <span class="counter"><xsl:value-of select="$refid"/></span>
    </a>
  </xsl:template>

<!-- ############### -->
<!--            -->
  <xsl:template match="cc:figure">
    <div class="figure" id="figure-{@id}">
      <img id="{@id}" src="{@entity}" width="{@width}" height="{@height}"/>
      <p/>
      <span class="ctr" data-myid="figure-{@id}" data-counter-type="ct-figure">
        <xsl:apply-templates select="." mode="getPre"/>
        <span class="counter"><xsl:value-of select="@id"/></span>
      </span>:
      <xsl:value-of select="@title"/>
    </div>
  </xsl:template>

<!-- ############### -->
<!--            -->
  <xsl:template match="cc:equation">
    <table><tr>
      <td>$$<xsl:apply-templates select="cc:value"/>$$</td>
      <td style="vertical-align: middle; padding-left: 100px">(<xsl:apply-templates select="cc:label"/>)</td>
    </tr></table>
  </xsl:template>


<!-- ############### -->
<!--            -->
  <!-- <xsl:template match="cc:figure|cc:ctr" mode="getPre" name="getPre"> -->
  <xsl:template match="cc:figure|cc:ctr" mode="getPre" >
    <xsl:variable name="label"><xsl:choose>
     <!-- <xsl:when test="text()"><xsl:value-of select="text()"/><xsl:message>Matched on text <xsl:value-of select="text()"/></xsl:message></xsl:when> -->
      <xsl:when test="@pre"><xsl:value-of select="@pre"/></xsl:when>
      <xsl:when test="name()='figure'"><xsl:text>Figure </xsl:text></xsl:when>
      <xsl:when test="@ctr-type"><xsl:if test="not(contains(@ctr-type,'-'))"><xsl:value-of select="@ctr-type"/><xsl:text>  </xsl:text></xsl:if></xsl:when>
      <xsl:otherwise>Table </xsl:otherwise>
    </xsl:choose></xsl:variable>

    <xsl:value-of select="$label"/>

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
          <xsl:message>Cant find <xsl:value-of select="$linkendlower"/>
          </xsl:message>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:element>
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

    <xsl:choose>
      <xsl:when test="./cc:depends">
         <xsl:message> Found a depends </xsl:message>
      </xsl:when>
    </xsl:choose>

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


