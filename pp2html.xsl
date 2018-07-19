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

  <!-- Variable for selecting how much debugging we want -->
  <xsl:param name="debug" select="'v'"/>

  <!-- very important, for special characters and umlauts iso8859-1-->
  <xsl:output method="html" encoding="UTF-8"/>

  <!-- Put all common templates into ppcommons.xsl -->
  <!-- They can be redefined/overridden  -->
  <xsl:include href="ppcommons.xsl"/>

  <xsl:include href="boilerplates.xsl"/>
<!-- ############### -->
<!--            -->
  <xsl:template match="/cc:PP|/cc:Module">
    <!-- Start with !doctype preamble for valid (X)HTML document. -->
    <xsl:text disable-output-escaping='yes'>&lt;!DOCTYPE html&gt;&#xa;</xsl:text>
    <html xmlns="http://www.w3.org/1999/xhtml">
      <head>
	<xsl:element name="title"><xsl:value-of select="//cc:PPTitle"/></xsl:element>
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

<xsl:call-template name="common_js"/>
<xsl:text disable-output-escaping="yes">// &lt;![CDATA[
const AMPERSAND=String.fromCharCode(38);
const NBSP=String.fromCharCode(160,160,160);

function buildIndex(){
    var eles = document.getElementsByClassName("indexable");
    var toc = document.getElementById("toc");
    var aa=0, bb=0;

    // prefix_array tracks the current numbering as we iterate through the document
    var prefix_array=[];
    var isAlpha=false;
    // Run through all the indexable
    while(eles.length > aa){
        var spacer="";
        if( eles[aa].hasAttribute("data-level-alpha") &amp;&amp; !isAlpha){
           prefix_array=[];
           isAlpha=true;
        }

        // Current numbering level depth
        level = eles[aa].getAttribute("data-level");

        // Add numbering levels to array if level of depth increases
        while (level>prefix_array.length) {
          prefix_array.push(0);
	      }

        // Truncate levels of array if numbering level decreases
        if(prefix_array.length>level){
          prefix_array.length=level;
        }

        // Increment the level we're currently on
        prefix_array[level-1]++;

        // Make appendices use an alphabetical identifier.
        // This will not work for documents with greater than 26 appendices
        var prefix=""+(isAlpha?String.fromCharCode(64 +prefix_array[0]):prefix_array[0]);

        // Add numbering levels for each level higher than 1
        for (bb=1; level>bb; bb++) {
          prefix+="."+prefix_array[bb];
          spacer+=NBSP;
        }

        // Insert the prefix/identifier into the document
        eles[aa].firstElementChild.innerHTML=prefix;

        // Build the toc entry
        var div= document.createElement('div');
        toc.appendChild(div);
        var line = document.createTextNode(spacer);
        div.appendChild(line);
        line = document.createElement('a');
        line.href="#"+eles[aa].id;
        line.class="toc-link"
        line.innerHTML=eles[aa].textContent;
        div.appendChild(line);

        // Go to the next element
        aa++;
    }
}


function changeMyCounter(subroot, val){
    var bb;
    for(bb=0; bb!=subroot.childNodes.length; bb++){
    	if( subroot.childNodes[bb] instanceof Element &amp;&amp;
    	    "counter"==subroot.childNodes[bb].getAttribute("class")){
    	    subroot.childNodes[bb].innerHTML = val;
    	    return;
    	}
    }
}


function fixCounters(){
    var figs = document.getElementsByClassName("ctr");
    var occurs = {};                                         // Map that stores how many times we've seen each thing
    var aa;
    for(aa=0; aa!= figs.length; aa++){                       // Go through every counted object
    	var ct = figs[aa].getAttribute("data-counter-type");  // Get which counter type it is
    	var curr = occurs[ct]!=null?parseInt(occurs[ct]):1;   // Figure out how many times we've seen it
    	occurs[ ct ] = curr + 1;                              // Save off increment for next time
    	changeMyCounter( figs[aa], curr);

    	var figId = figs[aa].getAttribute("data-myid");
    	var figRefs = document.getElementsByClassName(figId+"-ref");
    	var bb;
        for(bb=0; bb!=figRefs.length; bb++){
    	    changeMyCounter(figRefs[bb], curr);
    	}
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
function fixIndexRefs(){
    var brokeRefs = document.getElementsByClassName("dynref");
    var aa=0;
    for(aa=0; brokeRefs.length>aa; aa++){
       var linkend=(""+brokeRefs[aa].getAttribute("href")).substring(1);
       var target = document.getElementById(linkend);
       if (target == null ){
          console.log("Could not find element w/ id: " + linkend);
          continue;
       }
       brokeRefs[aa].innerHTML+=target.firstElementChild.textContent;
    }
}

// Called on page load to parse URL parameters and perform actions on them.
function init(){
    fixCounters();
    buildIndex();
    fixIndexRefs();
    fixToolTips();
    if(getQueryVariable("expand") == "on"){
      expand();
    }
}

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
    for (var ii = ap.length - 1; ii >= 0; --ii) {
        ap[ii].classList.remove('hide');
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

	  <!-- Tyring to get this to work -->
	  <xsl:if test="not($custom-css-file='')">
	    <xsl:message>One was passed
	       <xsl:value-of select="document($custom-css-file)/*"/>
	    </xsl:message>
	    
	  </xsl:if>

	</style>
      </head>
      <body onLoad="init()">
        <h1 class="title" style="page-break-before:auto;">
          <xsl:value-of select="//cc:ReferenceTable/cc:PPTitle"/>
        </h1>

        <noscript>
          <h1
            style="text-align:center; border-style: dashed; border-width: medium; border-color: red;"
            >This page is best viewed with JavaScript enabled!</h1>
        </noscript>
        <div class="center">
            <img src="images/niaplogo.png" alt="NIAP"/>
          <br/>

	  <!-- Might think about getting rid of this and just making it part of the foreword -->
	  
	  <p/>Version: <xsl:value-of select="//cc:ReferenceTable/cc:PPVersion"/>
          <p/><xsl:value-of select="//cc:ReferenceTable/cc:PPPubDate"/>
        <p/><b><xsl:value-of select="//cc:PPAuthor"/></b></div>

	<xsl:apply-templates select="//cc:foreword"/>


	<h2 style="page-break-before:always;">Revision History</h2>
        <table>
          <tr class="header">
            <th>Version</th>
            <th>Date</th>
            <th>Comment</th>
          </tr>
          <xsl:for-each select="cc:RevisionHistory/cc:entry">
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
	<div class="toc" id="toc">
	</div>

        <xsl:apply-templates select="//cc:chapter"/>
        <xsl:apply-templates select="//cc:appendix"/>
      </body>
    </html>

    <!-- <xsl:for-each select="//cc:acronyms/cc:entry/cc:term"> -->
    <!--   <xsl:variable name="tc"><xsl:value-of select="text()"/></xsl:variable> -->
    <!--   <xsl:if test="not(//cc:abbr[@linkend=$tc])"> -->
    <!-- 	<xsl:message>Abbr glossary term '<xsl:value-of select="$tc"/>' is never used.</xsl:message> -->
    <!--   </xsl:if> -->
    <!-- </xsl:for-each> -->
  </xsl:template>
<!-- ############### -->
<!--            -->
  <xsl:template name="TocElement">
    <xsl:param name="prefix"/>
    <p class="toc2">
      <xsl:value-of select="$prefix"/>.
      <a class="toc" href="#{@id}"> <xsl:value-of select="@title" /></a>
    </p>
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
      <xsl:for-each select="cc:threat">
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

      <xsl:if test="@status='sel-based'">
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
<!--            -->
  <xsl:template match="cc:appendix">
    <xsl:if test="$appendicize='on'">
      <h1 id="{@id}" class="indexable" data-level="1" data-level-alpha="true">
         Appendix
         <span class="num"></span><xsl:value-of select="$space3"/><xsl:value-of select="@title"/>
      </h1>
      <!-- insert SFRs for "special" appendices, if @id is one of the "special" ones-->
      <xsl:if test="@id='optional' or @id='sel-based' or @id='objective'" >
	<xsl:apply-templates mode='hook' select='.'/>
        <xsl:apply-templates />
        <!-- when @id of the appendix is optional/sel-based/objective,
        match with the @status of the component, which is the same value -->
        <xsl:apply-templates select="//cc:f-component[@status=current()/@id]" mode="appendicize-nofilter"/>
      </xsl:if>
      <xsl:if test="@id!='optional' and @id!='sel-based' and @id!='objective'">
	<xsl:apply-templates select="." mode="hook"/>
        <xsl:apply-templates/>
      </xsl:if>
    </xsl:if>

    <xsl:if test="$appendicize!='on' and @id!='optional' and @id!='sel-based' and @id!='objective'">
      <h1 id="{@id}" class="indexable" data-level="1" data-level-alpha="true">
  	      Appendix
  	      <span class="num"></span><xsl:value-of select="$space3"/><xsl:value-of select="@title"/>
      </h1>
      <xsl:apply-templates select="." mode="hook"/>
      <xsl:apply-templates/>
    </xsl:if>
  </xsl:template>

<!-- ############### -->
<!--            -->
  <xsl:template match="cc:chapter">
    <h1 id="{@id}" class="indexable" data-level="1"><span class="num"></span><xsl:value-of select="$space3"/>

      <xsl:value-of select="@title"/>
    </h1>
    <xsl:if test="@title='Security Requirements' and /cc:*[@boilerplate='yes']">
      <xsl:call-template name="bp-secreq"/>
    </xsl:if>
    <xsl:if test="@title='Conformance Claims' and  /cc:*[@boilerplate='yes']">
      <xsl:call-template name="bp-con-state">
	<xsl:with-param name="has_appendix"><xsl:value-of select="$appendicize"/></xsl:with-param>
	<xsl:with-param name="impsatreqid"><xsl:value-of select="//cc:*[@title='Implicitly Satisfied Requirements']/@id"/></xsl:with-param>
      </xsl:call-template>
    </xsl:if>

    <xsl:apply-templates/>
  </xsl:template>

<!-- ############### -->
<!--            -->
  <xsl:template match="cc:section">
    <h2 id="{@id}" class="indexable" data-level="2"><span class="num"></span><xsl:value-of select="$space3"/>

      <xsl:value-of select="@title"/>
    </h2>

    <xsl:apply-templates mode="hook" select="."/>
    <xsl:apply-templates/>
  </xsl:template>


<!-- ############### -->
<!--            -->
  <xsl:template match="cc:subsection">
    <!-- the "if" statement is to not display subsection headers when there are no
    subordinate mandatory components to display in the main body (when in "appendicize" mode) -->
    <xsl:if test="$appendicize!='on' or ../@id!='SFRs' or count(.//cc:f-component[not(@status) or @status='threshold'])">
      <h3 id="{@id}" class="indexable" data-level="{count(ancestor::*)}">
	    <span class="num"></span><xsl:value-of select="$space3"/>
      <xsl:value-of select="@title" />
      </h3>
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
    <a href="#{@linkend}" class="dynref">Appendix </a>
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
  <xsl:template match="cc:cite">
    <xsl:variable name="linkend" select="@linkend"/>
    <a href="#{$linkend}">[<xsl:value-of select="//cc:bibliography/cc:entry[@id=$linkend]/cc:tag"/>]</a>
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

  <!-- Makes a ref to requirement -->
<!-- ############### -->
<!--            -->
  <xsl:template name="req-refs">
    <!-- Optional css classes -->
    <xsl:param name="class"/>
    <!-- Requirement id -->
    <xsl:param name="req"/>

    <!--lower req-->
    <xsl:variable name="lreq">
      <xsl:value-of select="translate($req,$upper,$lower)"/>
    </xsl:variable>

    <!--Uppercase req -->
    <xsl:variable name="capped-req">
      <xsl:value-of select="translate($lreq,$lower,$upper)"/>
    </xsl:variable>
    
    <a class="{$class}" href="#{$capped-req}"><xsl:value-of select="$capped-req"/></a>
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


