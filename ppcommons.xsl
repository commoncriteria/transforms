<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:cc="https://niap-ccevs.org/cc/v1" xmlns:htm="http://www.w3.org/1999/xhtml">

  <xsl:key name="abbr" match="cc:glossary/cc:entry/cc:term/cc:abbr" use="text()"/>

  <xsl:variable name="lower" select="'abcdefghijklmnopqrstuvwxyz'"/>
  <xsl:variable name="upper" select="'ABCDEFGHIJKLMNOPQRSTUVWXYZ'"/>
  <xsl:template name="common_js">
// This was borrowed from a W3C example
function sortTable(tableid, n) {
  var table, rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;

  table = document.getElementById(tableid);
  switching = true;
  //Set the sorting direction to ascending:
  dir = "asc"; 
  /*Make a loop that will continue until
  no switching has been done:*/
  while (switching) {
    //start by saying: no switching is done:
    switching = false;
    rows = table.getElementsByTagName("TR");
    /*Loop through all table rows (except the
    first, which contains table headers):*/
    for (i = 1; (rows.length - 1) > i; i++) {
      //start by saying there should be no switching:
      shouldSwitch = false;
      /*Get the two elements you want to compare,
      one from current row and one from the next:*/
      x = rows[i].getElementsByTagName("TD")[n];
      y = rows[i + 1].getElementsByTagName("TD")[n];
      /*check if the two rows should switch place,
      based on the direction, asc or desc:*/
      if (dir == "asc") {
        if (x.textContent.toLowerCase() > y.textContent.toLowerCase()) {
          //if so, mark as a switch and break the loop:
          shouldSwitch= true;
          break;
        }
      } else if (dir == "desc") {
        if (y.textContent.toLowerCase() > x.textContent.toLowerCase()) {
          //if so, mark as a switch and break the loop:
          shouldSwitch= true;
          break;
        }
      }
    }
    if (shouldSwitch) {
      /*If a switch has been marked, make the switch
      and mark that a switch has been done:*/
      rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
      switching = true;
      //Each time a switch is done, increase this count by 1:
      switchcount ++;      
    } else {
      /*If no switching has been done AND the direction is "asc",
      set the direction to "desc" and run the while loop again.*/
      if (switchcount == 0) if( dir == "asc") {
        dir = "desc";
        switching = true;
      }
    }
  }
}
  </xsl:template>

  <!-- Common CSS rules for all files-->
  <xsl:template name="common_css">
    .assignable-content{
      font-style: italic;
    }
    .refinement{
      text-decoration: underline;
    }
    .toggler::before{
       <!-- Seems like a hack -->
       content: "\00a0\00a0\00a0\00a0";
    }
    .toggler{ 
       size: 15px 15px;
       background-size: 15px 15px;
       background-repeat: no-repeat;
       display: inline-block;
    }
    .activity_pane .toggler{
       background-image: url('images/expanded.png');
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
    .note-header::after{
      content: ":"
    }
    .note p:first-child{
      display: inline;
    }
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

  <xsl:template match="cc:steplist">
    <ul>
      <xsl:apply-templates/>
    </ul>
  </xsl:template>

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
    <xsl:if test="@exclusive">, choose one of</xsl:if> 
    <xsl:if test="@atleastone">, at least one of</xsl:if>: 
    <xsl:choose>      
      <xsl:when test="@linebreak='yes'">
	<ul>
	  <xsl:for-each select="cc:selectable">
	    <li><i><xsl:apply-templates/></i><xsl:call-template name="commaifnotlast"/></li>
	  </xsl:for-each>
	  <!-- <p style="margin-left: 40px;"><i><xsl:apply-templates/></i><xsl:call-template name="commaifnotlast"/></p> -->	
	  </ul>
      </xsl:when>
      <xsl:when test="@linebreak='no'"><xsl:for-each select="cc:selectable"><i><xsl:apply-templates/></i><xsl:call-template name="commaifnotlast"/></xsl:for-each></xsl:when>

      <xsl:when test=".//cc:selectables"><ul><xsl:for-each select="cc:selectable"><li><i><xsl:apply-templates/></i><xsl:call-template name="commaifnotlast"/></li></xsl:for-each></ul></xsl:when>

      <xsl:otherwise><xsl:for-each select="cc:selectable"><i><xsl:apply-templates/></i><xsl:call-template name="commaifnotlast"/></xsl:for-each></xsl:otherwise></xsl:choose>]</xsl:template>

    <!-- <xsl:for-each select="cc:selectable"> -->
    <!--   <xsl:choose> -->
    <!-- 	<xsl:when test="../@linebreak"> -->
    <!-- 	  <p style="margin-left: 40px;"><i><xsl:apply-templates/></i><xsl:call-template name="commaifnotlast"/></p> -->
    <!-- 	</xsl:when> -->
    <!-- 	<xsl:otherwise><i> -->
    <!-- 	  <xsl:apply-templates/></i><xsl:call-template name="commaifnotlast"/> -->
    <!-- 	</xsl:otherwise> -->
    <!--   </xsl:choose> -->
    <!-- </xsl:for-each> -->

  <xsl:template name="commaifnotlast"><xsl:if test="position() != last()"><xsl:text>, </xsl:text></xsl:if></xsl:template>

  <xsl:template match="cc:assignable"> [<b>assignment</b>: <span class="assignable-content"><xsl:apply-templates/>] </span></xsl:template>

  <xsl:template match="cc:refinement"><span class="refinement"><xsl:apply-templates/></span></xsl:template>

  <xsl:template match="cc:note">
    <div class="appnote">
      <span class="note-header"><xsl:choose>
	<xsl:when test="@role='application'">Application</xsl:when>
	<xsl:when test="@role='developer'">Developer</xsl:when>
	<xsl:otherwise><xsl:value-of select="@role"/></xsl:otherwise>
      </xsl:choose> Note</span> <span class="note">
      <xsl:apply-templates/>
      </span>
    </div>
  </xsl:template>

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

  <!-- Eat all comments and processing instructions-->
  <xsl:template match="comment()"/>
  <xsl:template match="processing-instruction()"/>
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


  <xsl:template match="@*|node()">
    <xsl:copy>
      <xsl:apply-templates select="@*|node()"/>
    </xsl:copy>
  </xsl:template>

  <xsl:template match="processing-instruction('xml-stylesheet')"/>


  <xsl:template match="cc:management-function-set">
    <table style="width: 100%;">
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
	    <xsl:if test="$manfunc/*[@ref=$id]"><xsl:value-of select="name($manfunc/*[@ref=$id])"/></xsl:if>
	  </td>
	</xsl:for-each>
    </tr>
  </xsl:template>




  <!-- By default, quietly unwrap all cc elements -->
  <xsl:template match="cc:*">
    <xsl:if test="contains($debug,'vv')">
      <xsl:message> Unmatched CC tag: <xsl:call-template name="path"/></xsl:message>
    </xsl:if>
    <xsl:apply-templates/>
  </xsl:template>

  <!-- -->
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
  
  <!-- Do not write xml-model processing instruction to HTML output. -->
  <xsl:template match="processing-instruction('xml-model')" />
</xsl:stylesheet>
