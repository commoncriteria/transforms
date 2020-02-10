<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:cc="https://niap-ccevs.org/cc/v1" xmlns:htm="http://www.w3.org/1999/xhtml">

  <xsl:key name="abbr" match="cc:glossary/cc:entry/cc:term/cc:abbr" use="text()"/>

  <!-- Variable for selecting how much debugging we want -->
  <xsl:param name="debug" select="'v'"/>



  <xsl:param name="release" select="'draft'"/>
  <!-- #Adds 3 non-breaking spaces -->
  <xsl:variable name="space3">&#160;&#160;&#160;</xsl:variable>

  <xsl:variable name="title"><xsl:choose>
      <xsl:when test="//cc:PPTitle"><xsl:value-of select="//cc:PPTitle"/></xsl:when>
      <xsl:otherwise>PP-Module for <xsl:value-of select="/cc:*/@target-products"/></xsl:otherwise>
  </xsl:choose></xsl:variable>


  <xsl:variable name="lower" select="'abcdefghijklmnopqrstuvwxyz'"/>
  <xsl:variable name="upper" select="'ABCDEFGHIJKLMNOPQRSTUVWXYZ'"/>

  <!--##############################################
        Template for javascript common to all transforms
      ##############################################-->
  <xsl:template name="common_js">
    <!-- Include custom javascript defined in the pp -->
    <xsl:value-of select="//cc:extra-js"/>
  </xsl:template>

  <!-- ############################################################
           Gets the ID for the f-component or f-element
       ############################################################-->
  <xsl:template match="cc:f-component|cc:f-element" mode="getId">
    <xsl:variable name="iter"><xsl:choose>
      <xsl:when test="name()='f-component'"><xsl:value-of select="@iteration"/></xsl:when>
      <xsl:otherwise><xsl:value-of select="../@iteration"/></xsl:otherwise>
    </xsl:choose></xsl:variable>
    <xsl:variable name="baseID"><xsl:choose>
      <xsl:when test="name()='f-component'"><xsl:value-of select="@id"/></xsl:when>
      <xsl:otherwise><xsl:value-of select="../@id"/></xsl:otherwise>
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
      <xsl:when test="name()='a-component'"><xsl:value-of select="@id"/></xsl:when>
      <xsl:otherwise><xsl:value-of select="../@id"/></xsl:otherwise>
    </xsl:choose></xsl:variable>
    <xsl:value-of select="translate($baseID, $lower, $upper)"/>
    <xsl:if test="name()='a-element'">.<xsl:value-of select="count(preceding-sibling::cc:a-element)+1"/></xsl:if>
  </xsl:template>


   <!--##############################################
      ##############################################-->
 <!-- Common CSS rules for all files-->
  <xsl:template name="common_css">
    #toc a{
        display: block;
    }

    svg{
      width: 100%;
    }

    a[id^="ajq_"]{
        color:black;
    }

    <!-- h1{ -->
    <!--    width: 100%; -->
    <!--    border-bottom-style: solid; -->
    <!--    border-bottom-color: black; -->
    <!-- } -->
    body{
       max-width: 900px;
       margin: auto;
    }
    #toc span{
       margin-left: 20px;
    }
    .assignable-content{
      font-style: italic;
    }
    .refinement{
      text-decoration: underline;
    }
    div.eacategory{
      font-style: italic;
      font-weight: bold;
    }
    .activity_pane .toggler::after, .activity_pane .toggler{
       display: inline-block;
       height: auto;
       content: url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8A\
       AAAPCAYAAAA71pVKAAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAQOFAAEDhQGl\
       VDz+AAAAB3RJTUUH4gIXFDM7fhmr1wAAAfRJREFUKM+dkk9I02EYxz/P+25uurWR\
       tTkzI4NGl4jQgkq71K1DhnTQIDolRAQFQYSHTtGhU4e6eujQofBSFLOg0C4RUSjh\
       FnmqTTdKpj/mfv/eX4cUpmRYn9vz8v3w8D7PA/AWGADCbI4QcAb4AnAF8IBJEdX+\
       N0tEda40C4AHADviW1LFvpOX6+FwtAacVzqkGiWtwxo4F21OuPu7+yvxRNoDEhpY\
       cpzavkQyc7D76FCk+vN7j7VU6RdR4xAsikjGGP9FKrN3sPfEpajv2i2zhckR4JUG\
       UCr0erFavLkn2ytd2WPxcFOsZb74+SIQA0YPHBqIdB8Z6tChJv1m/N4P33OGAUsD\
       BIFxPNcOkq07jyeSbbo1tTu2q6vHEqU7D/ddSKcz2ZQJjBSmx925b9NjwEMAafha\
       eyQa/3Dq7O0243sCIEoRGAOA59nm5dM7OHVruzH+AkDjYEp23RrLT+U8Ub+fV0UR\
       oVyaMfVa9fqquF5GKX3ja2FCuc6yWbMipYNP755UgEdr8o2FMf5ivVYdKRfzRkRW\
       RfJTOc+2rWdAcUN5hdGP7x8viGgAXLvGbGFCKxW6tj74J3nOqVvP89M5V6kQ86UZ\
       f7lWvWWMt7Sp41VKb21uSfqnB++6kWi8BLTzL4ioq7H4tgC4z3/QAZSBxEaBXygN\
       v+jeFnAPAAAAAElFTkSuQmCC');
       max-width: 15px;
    }


    a {
      text-decoration: none;
      word-wrap: break-word;
    }
    a.abbr:link{
      color:black;
      text-decoration:none;
    }
    a.abbr:visited{
      color:black;
      text-decoration:none;
    }
    a.abbr:hover{
      color:blue;
      text-decoration:none;
    }
    a.abbr:hover:visited{
      color:purple;
      text-decoration:none;
    }
    a.abbr:active{
      color:red;
      text-decoration:none;
    }
    .note-header{
      font-weight: bold;
    }
    .note p:first-child{
      display: inline;
    }


    /* Tooltip container */
    .tooltipped {
       position: relative;
       display: inline-block;
       border-bottom: 1px dotted black; /* If you want dots under the hoverable text */
    }

    /* Tooltip text */
    .tooltiptext {
       visibility: hidden;
       width: 120px;
       background-color: black;
       color: #fff;
       text-align: center;
       padding: 5px 0;
       border-radius: 6px;

       /* Position the tooltip text - see examples below! */
       position: absolute;
       z-index: 1;
   }

   /* Show the tooltip text when you mouse over the tooltip container */
   .tooltipped:hover .tooltiptext {
       visibility: visible;
   }

   table.mfs td{
       text-align: center;
   }
   table.mfs td:first-child{
       text-align: left;
   }
   table{
       margin:auto;
       margin-top:1em;
       border-collapse:collapse; /*border: 1px solid black;*/
   }
   td{
       text-align:left;
       padding:8px 8px;
   }
   th{
       padding:8px 8px;
   }
   thead tr td{
       text-align: center;
       font-style: oblique;
       font-weight: bold;
   }
   tr.header{
       border-bottom:3px solid gray;
       padding:8px 8px;
       text-align:left;
       font-weight:bold; /*font-size: 90%; font-family: verdana, arial, helvetica, sans-serif; */
   }
   table tr:nth-child(2n+2){
       background-color:#F4F4F4;
   }

   .dependent{
       border: 1px solid gray;
       border-radius: 1px
   }
   .dependent-content{
       margin-left: 25px;
       font-style: italic;
   }
   <!-- Include some custom css as defined by in the source PP -->
    <xsl:value-of select="//cc:extra-css"/>
  </xsl:template>


<!-- ############### -->
<!--            -->
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

  <xsl:template match="cc:testlist">
    <ul>
      <xsl:apply-templates/>
    </ul>
  </xsl:template>

  <xsl:template match="cc:test">
    <li>
      <b>Test <xsl:for-each select="ancestor::cc:test"><xsl:value-of
            select="count(preceding-sibling::cc:test) + 1"/>.</xsl:for-each><xsl:value-of
          select="count(preceding-sibling::cc:test) + 1"/>: </b>
      <xsl:apply-templates/>
    </li>
  </xsl:template>

  <xsl:template name="references">
    <h1 id="biblio" class="indexable" data-level="A">References</h1>
    <table>
      <tr class='header'><th>Identifier</th><th>Title</th></tr>
      <xsl:apply-templates select="//cc:bibliography"/>
    </table>
  </xsl:template>

  <xsl:template match="cc:componentsneeded">
    <table>
      <tr class='header'><th>Component</th><th>Explanation</th></tr>
      <xsl:apply-templates select="//cc:componentneeded"/>
    </table>
  </xsl:template>

  <xsl:template match="cc:componentneeded">
    <tr>
        <td><xsl:apply-templates select="cc:componentid"/></td>
        <td><xsl:apply-templates select="cc:notes"/></td>
    </tr>
  </xsl:template>

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
    <xsl:variable name="target" select="key('abbr', @linkend)"/>
    <xsl:variable name="abbr" select="$target/text()"/>

    <a class="abbr" href="#abbr_{$abbr}">
      <abbr title="{$target/@title}">
        <xsl:value-of select="$abbr"/>
      </abbr>
    </a>
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

  <xsl:template match="cc:assignable">[<b>assignment</b>: <span class="assignable-content"><xsl:apply-templates/></span>]</xsl:template>

  <xsl:template match="cc:refinement"><span class="refinement"><xsl:apply-templates/></span></xsl:template>

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


  <xsl:template match="cc:management-function-set">
    <table class="mfs" style="width: 100%;">
      <tr class="header">
        <td>Management Function</td>
        <xsl:apply-templates select="./cc:manager"/>
      </tr>
      <xsl:apply-templates select="./cc:management-function"/>
    </table>
  </xsl:template>


  <xsl:template match="cc:manager">
    <td> <xsl:apply-templates/> </td>
  </xsl:template>

  <xsl:template match="cc:management-function">
    <tr>
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


  <xsl:template name="make-management-value">
    <xsl:param name="type"/>
    <xsl:choose>
      <xsl:when test="$type='O'"><div>O<span class="tooltiptext">Optional</span></div></xsl:when>
      <xsl:when test="$type='M'"><div>X<span class="tooltiptext">Mandatory</span></div></xsl:when>
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
  <xsl:template match="htm:*">
    <xsl:choose>
      <xsl:when test="cc:depends">
        <div class="dependent"> The following content should be included if:
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
          </xsl:for-each> </ul>
          <div class="dependent-content">
            <xsl:call-template name="handle-html"/>
          </div>        
        </div>        
      </xsl:when>
      <xsl:otherwise>
        <xsl:call-template name="handle-html"/>
      </xsl:otherwise>
    </xsl:choose>
 </xsl:template>

  <xsl:template name="handle-html">
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

  <!-- Makes a ref to requirement -->
<!-- ############### -->
<!--            -->
  <xsl:template name="req-refs">
    <!-- Optional css classes -->
    <xsl:param name="class"/>
    <!-- Requirement id -->
    <xsl:param name="req"/>

    <xsl:param name="iter"/>
    <!--lower req-->
    <xsl:variable name="lreq">
      <xsl:value-of select="translate($req,$upper,$lower)"/>
    </xsl:variable>

    <!--Uppercase req -->
    <xsl:variable name="capped-req">
      <xsl:value-of select="translate($lreq,$lower,$upper)"/>
    </xsl:variable>

    <a class="{$class}" href="#{$capped-req}{$iter}"><xsl:value-of select="concat($capped-req,$iter)"/></a>
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

<!-- ############################ -->
<!-- Contains JavaScript for initializing the page -->
  <xsl:template name="init_js">
    <xsl:text disable-output-escaping="yes">// &lt;![CDATA[

// Called on page load to parse URL parameters and perform actions on them.
function init(){
    if(getQueryVariable("expand") == "on"){
      expand();
    }
    fixAbbrs();
}


function fixAbbrs(){
    var aa;
    var brk_els = document.getElementsByClassName("dyn-abbr");
    //
    for(aa=0; aa!=brk_els.length; aa++){
        var abbr = brk_els[aa].firstElementChild.getAttribute("href").substring(1);
        var el = document.getElementById("long_"+abbr)
        if (el==null) {
             console.log("Could not find 'long_abbr_'"+abbr);
             continue;
        }
        var abbr_def = el.textContent;
        brk_els[aa].setAttribute("title", abbr_def);
    }
}



// ]]&gt;</xsl:text>
</xsl:template>


  <xsl:template name="head">
    <xsl:param name="title"/>
      <head>
	<title><xsl:value-of select="$title"/></title>
	<script src='https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.1/MathJax.js?config=TeX-AMS-MML_HTMLorMML' ></script>
        <script type="text/x-mathjax-config">
            MathJax.Hub.Config({
            extensions: ["tex2jax.js"],
            jax: ["input/TeX", "output/HTML-CSS"],
            showMathMenu: false,
            tex2jax: {
              inlineMath: [ ['$','$'], ["\\(","\\)"] ],
              displayMath: [ ['$$','$$'], ["\\[","\\]"] ],
              processEscapes: true
            },
            styles: {

                ".MathJax_Display": {
                "text-align": "left !important",
                margin:       "0em 0em !important"
            }}
            });
        </script>
        <script type="text/javascript">

<xsl:call-template name="init_js"/>

<xsl:text disable-output-escaping="yes">// &lt;![CDATA[
const AMPERSAND=String.fromCharCode(38);

// Pass a URL variable to this function and it will return its value
function getQueryVariable(variable)
{
    var query = window.location.search.substring(1);
    var vars = query.split(AMPERSAND);
    for (var i=0;i!=vars.length;i++) {
        var pair = vars[i].split("=");
        if(pair[0] == variable){return pair[1];}
    }
    return(false);
}


//    Expands all evaluation activities
function expand(){
    var ap = document.getElementsByClassName('activity_pane');
    for (var ii = 0; ii!=ap.length; ii++) {
        ap[ii].classList.remove('hide');
    }
}

// Function to expand and contract a given div
function toggle(descendent) {
    var cl = descendent.parentNode.parentNode.classList;
    if (cl.contains('hide')){
      cl.remove('hide');
    }
    else{
      cl.add('hide');
    }
}

// Expands targets if they are hidden
function showTarget(id){
    var element = document.getElementById(id);
    while (element != document.body.rootNode ){
	element.classList.remove("hide");
	element = element.parentElement;
    }
}


// ]]&gt;</xsl:text>
        </script>

        <style type="text/css">
        <xsl:call-template name="common_css"/>


          .figure{
              font-weight:bold;
          }
          h1{
              page-break-before:always;
              text-align:left;
              font-size:200%;
              margin-top:2em;
              margin-bottom:2em;
              font-family:verdana, arial, helvetica, sans-serif;
              margin-bottom:1.0em;
          }
          h1.title{
              text-align:center;
          }
          h2{
              font-size:125%;
              border-bottom:solid 1px gray;
              margin-bottom:1.0em;
              margin-top:2em;
              margin-bottom:0.75em;
              font-family:verdana, arial, helvetica, sans-serif;
          }
          h3{
              font-size:110%;
              margin-bottom:0.25em;
              font-family:verdana, arial, helvetica, sans-serif;
          }
          h4{
              margin-left:0%;
              font-size:100%;
              margin-bottom:0.75em;
              font-family:verdana, arial, helvetica, sans-serif;
          }
          h5,
          h6{
              margin-left:6%;
              font-size:90%;
              margin-bottom:0.5em;
              font-family:verdana, arial, helvetica, sans-serif;
          }
          p{
              margin-bottom:0.6em;
              margin-top:0.2em;
          }
          pre{
              margin-bottom:0.5em;
              margin-top:0.25em;
              margin-left:3%;
              font-family:monospace;
              font-size:90%;
          }
          ul{
              margin-bottom:0.5em;
              margin-top:0.25em;
          }
          td{
              vertical-align:top;
          }
          dl{
              margin-bottom:0.5em;
              margin-top:0.25em;
          }
          dt{
              margin-top:0.7em;
              font-weight:bold;
              font-family:verdana, arial, helvetica, sans-serif;
          }

          a.linkref{
              font-family:verdana, arial, helvetica, sans-serif;
              font-size:90%;
          }

          *.simpleText{
              margin-left:10%;
          }
          *.propertyText{
              margin-left:10%;
              margin-top:0.2em;
              margin-bottom:0.2em
          }
          *.toc{
              background:#FFFFFF;
          }
          *.toc2{
              background:#FFFFFF;
          }
          div.comp{
              margin-left:8%;
              margin-top:1em;
              margin-bottom:1em;
          }
          div.element{
              margin-bottom:1em;
          }
          div.appnote{
              margin-left:0%;
              margin-top:1em;
          }
          .comment-aa{
              background-color:beige;
              color:green;
          }
          div.subaact{
              margin-left:0%;
              margin-top:1em;
          }
          div.activity_pane_body{
              margin-left:0%;
              margin-top:1em;
              margin-bottom:1em;
              padding:1em;
              border:2px solid #888888;
              border-radius:3px;
              display:block;
              margin-left:0%;
              margin-top:1em;
              margin-bottom:1em;
              box-shadow:0 2px 2px 0 rgba(0,0,0,.14),0 3px 1px -2px rgba(0,0,0,.2),0 1px 5px 0 rgba(0,0,0,.12);
          }
          div.optional-appendicies{
              display:none;
          }

          div.statustag{
              margin-left:0%;
              margin-top:1em;
              margin-bottom:1em;
              padding: 0.6em;
              border:2px solid #888888;
              border-radius:3px;
          }

          div.toc{
              margin-left:8%;
              margin-bottom:4em;
              padding-bottom:0.75em;
              padding-top:1em;
              padding-left:2em;
              padding-right:2em;
          }
          span.SOlist{
              font-size:90%;
              font-family:verdana, arial, helvetica, sans-serif;
          }
          h2.toc{
              border-bottom:none;
              margin-left:0%;
              margin-top:0em;
          }
          p.toc{
              margin-left:2em;
              margin-bottom:0.2em;
              margin-top:0.5em;
          }
          p.toc2{
              margin-left:5em;
              margin-bottom:0.1em;
              margin-top:0.1em;
          }
          div.center{
              display:block;
              margin-left:auto;
              margin-right:auto;
              text-align:center;
          }
          div.figure{
              display:block;
              margin-left:auto;
              margin-right:auto;
              text-align:center;
              margin-top:1em;
          }
          div.activity_pane_header{
              display:table-cell;
              vertical-align:middle;
              padding-top:10px
          }
          span.activity_pane_label{
              vertical-align:middle;
              color:black;
              text-decoration:none;
              font-size:100%;
              font-weight:bold; /*font-family: verdana, arial, helvetica, sans-serif; */
          }
          .dyn-abbr a, .dyn-abbr a:active, .dyn-abbr a:visited{
              background-color: inherit;
              color: inherit;
              text-decoration: inherit;;
          }

          @media screen{
              *.reqid{
                  float:left;
                  font-size:90%;
                  font-family:verdana, arial, helvetica, sans-serif;
                  margin-right:1em;
              }
              *.req{
                  margin-left:0%;
                  margin-top:1em;
                  margin-bottom:1em;
              }
              *.reqdesc{
                  margin-left:20%;
              }

              .activity_pane.hide .toggler::after, .activity_pane.hide .toggler{
	          content: url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8A\
		  AAAPCAYAAAA71pVKAAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAQOFAAEDhQGl\
		  VDz+AAAAB3RJTUUH4gIXFC4BR3keeQAAAfZJREFUKM+d0k1PE1EUBuB37h2nQ+30\
		  w5YObR0FhIppqBgWuDCaSBQjiQZNTIxLfoAkBHXh2vg7xID+ABPXBl3UdAMaN1CR\
		  j5ZijZ22DKW9d44LP1KMROvZnMU5z+KcvBzAAgADwCdV1RzXlYQ26tYhrYM6u/qX\
		  ATwCcKodrAOYv3z9IV28OuP6/NHPAGYZ45G/QQ5AAFjNbyzdTA2NewcGx7xeI5wu\
		  FZenQOQQuasHncN/9IJo1sn+unkpbqVFIJhgydQo13VjDKCJSnnLBJAHUPoTBoA3\
		  uzvlfiNgDhn+KMiVCB6xYCZSoaPHz5wrba/cbuztpBWFvQLI+R2DSGZqleKNuJX2\
		  cVVjAIExDo/uV7pPjGhSNntrleI9+n7Ox33Y549Wq/ZWTyh8rNcfjPlaZ4xzZvUM\
		  ezrNvnJ+fXFCiL2k2rpQq2wnAqH4tYjZFyZq/Y8CKZoim51z1nIZQ4jGNIC5fZhz\
		  7fHA4JVuj26AyIWiMDSbdTi1L/T29RO7ahdfKgqbInJLANCKZ6Kx5J24dVowztW6\
		  Y+8WNt91FNYXc4WN988BzAL4QOT+Aj/x8GFf+MHI+UlI2cBS9kVlLZfxSFdMS9GY\
		  V1WtKETDPShhz85emLRHx++TETBLAJ4qCov8c7ajsZMr/5PtBQB3AXSpqsbagd8A\
		  O+HMRUtPNsQAAAAASUVORK5CYII=');
              }

              .activity_pane.hide .activity_pane_body{
                  display:none;
              }
              div.statustag{
                  box-shadow:4px 4px 3px #888888;
              }
          }


          @media print{
              *.reqid{
                  font-size:90%;
                  font-family:verdana, arial, helvetica, sans-serif;
              }
              *.req{
                  margin-left:0%;
                  margin-top:1em;
                  margin-bottom:1em;
              }
              *.reqdesc{
                  margin-left:20%;
              }
              div.activity_pane_body{
                  padding:1em;
                  border:2px solid #888888;
                  border-radius:3px;
                  display:block;
              }

	            img[src="images/collapsed.png"] { display:none;}

          }
	</style>
      </head>
    </xsl:template>


    <xsl:template name="body-begin">
      <h1 class="title" style="page-break-before:auto;"><xsl:value-of select="$title"/></h1>
      <noscript>
        <h1 style="text-align:center; border-style: dashed; border-width: medium; border-color: red;"
            >This page is best viewed with JavaScript enabled!</h1>
      </noscript>
      <div class="center">
	<img src="images/niaplogo.png" alt="NIAP Logo"/>
        <br/>
	<!-- Might think about getting rid of this and just making it part of the foreword -->
	<p/>Version: <xsl:value-of select="//cc:ReferenceTable/cc:PPVersion"/>
        <p/><xsl:value-of select="//cc:ReferenceTable/cc:PPPubDate"/>
        <p/><b><xsl:value-of select="//cc:PPAuthor"/></b>
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
              <td>
                <xsl:value-of select="cc:version"/>
              </td>
              <td>
                <xsl:value-of select="cc:date"/>
              </td>
              <td>
                <xsl:apply-templates select="cc:subject"/>
              </td>
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
  <xsl:template match="cc:cite">
    <xsl:variable name="linkend" select="@linkend"/>
    <a href="#{$linkend}">[<xsl:value-of select="//cc:bibliography/cc:entry[@id=$linkend]/cc:tag"/>]</a>
  </xsl:template>

</xsl:stylesheet>
