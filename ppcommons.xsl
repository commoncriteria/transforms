<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:cc="https://niap-ccevs.org/cc/v1" xmlns:htm="http://www.w3.org/1999/xhtml">

  <xsl:key name="abbr" match="cc:glossary/cc:entry/cc:term/cc:abbr" use="text()"/>

  <!-- #Adds 3 non-breaking spaces -->
  <xsl:variable name="space3">&#160;&#160;&#160;</xsl:variable>


  <xsl:variable name="lower" select="'abcdefghijklmnopqrstuvwxyz'"/>
  <xsl:variable name="upper" select="'ABCDEFGHIJKLMNOPQRSTUVWXYZ'"/>

  <!-- 
       Template for javascript common to all transforms
  -->
  <xsl:template name="common_js">
    <!-- Include custom javascript defined in the pp -->
    <xsl:value-of select="//cc:extra-js"/>
  </xsl:template>


  <xsl:template match="cc:TSS|cc:Guidance|cc:Tests">
    <div class="eacategory"><xsl:value-of select="name()"/></div>
  </xsl:template>


  <!-- Common CSS rules for all files-->
  <xsl:template name="common_css">
    #toc a{
        display: block;
    }

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
          tr.header{
              border-bottom:3px solid gray;
              padding:8px 8px;
              text-align:left;
              font-weight:bold; /*font-size: 90%; font-family: verdana, arial, helvetica, sans-serif; */
          }
          table tr:nth-child(2n+2){
              background-color:#F4F4F4;
          }

   <!-- Include some custom css as defined by in the source PP -->
    <xsl:value-of select="//cc:extra-css"/>
    
  </xsl:template>

  <xsl:template match="cc:linkref">
    <xsl:variable name="linkend" select="translate(@linkend,$lower,$upper)"/>
    <xsl:variable name="linkendlower" select="translate(@linkend,$upper,$lower)"/>

    <xsl:if test="not(//*[@id=$linkendlower])">
      <xsl:message> Broken linked element at <xsl:value-of select="$linkend"/>
      </xsl:message>
    </xsl:if>
    <xsl:value-of select="text()"/>
    <a class="linkref" href="#{$linkend}">
      <xsl:value-of select="$linkend"/>
    </a>
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
	  <xsl:variable name="id" select="@id"/>
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
  
</xsl:stylesheet>
