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

  <!-- release variable, overridden to "final" for release versions -->
  <xsl:param name="release" select="'draft'"/>

  <xsl:param name="appendicize" select="''"/>

  <xsl:param name="custom-css-file" select="''"/>

  <!-- Variable for selecting how much debugging we want -->
  <xsl:param name="debug" select="'v'"/>

  <xsl:variable name="space3">&#160;&#160;&#160;</xsl:variable>
  
  <!-- very important, for special characters and umlauts iso8859-1-->
  <xsl:output method="html" encoding="UTF-8" indent="yes"/>
  
  <!-- Put all common templates into ppcommons.xsl -->
  <!-- They can be redefined/overridden  -->
  <xsl:include href="ppcommons.xsl"/>

  <xsl:template match="/cc:PP">

    <!-- Start with !doctype preamble for valid (X)HTML document. -->
    <xsl:text disable-output-escaping='yes'>&lt;!DOCTYPE html&gt;&#xa;</xsl:text>
    <html xmlns="http://www.w3.org/1999/xhtml">
      <head>
	<xsl:element name="title"><xsl:value-of select="//cc:PPTitle"/></xsl:element>
	    <script src='https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.1/MathJax.js?config=TeX-AMS-MML_HTMLorMML'></script>
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
const AMPERSAND=String.fromCharCode(38);
const NBSP=String.fromCharCode(160,160,160);


function buildIndex(){
    
    var eles = document.getElementsByClassName("indexable");
    var toc = document.getElementById("toc");
    var aa=0, bb=0;
    var ret=[];
    var isAlpha=false;
    // Run through all the indexable
    while(eles.length > aa){
        var spacer="";
        if( eles[aa].hasAttribute("data-level-alpha") &amp;&amp; !isAlpha){
           ret=[];
           isAlpha=true;
        }
    
        // Build levels
	level = eles[aa].getAttribute("data-level");
	while( level > ret.length ){
	    ret.push(0);
	}
        // Increment the one we're on
        ret[level-1]++;

	// WARNING: This will not work for documents with greater than 26 appendices
	var prefix=""+(isAlpha?String.fromCharCode(64 +ret[0]):ret[0]);
        for(bb=1; level>bb; bb++){
		prefix+="."+ret[bb];
		spacer+=NBSP;
	}
	prefix=prefix+(isAlpha?":":".");
	
	// Set the number
        eles[aa].firstElementChild.innerHTML=prefix

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

	
        // Zero out the ones after
        while(ret.length > level ){
            ret[level]=0;
            level++;
        }
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


function fixCounters(type){
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
function toggle(divID, imgID) {
    var item = document.getElementById(divID);
    var img = document.getElementById(imgID);
    if (item) {
        item.className = (item.className=='aacthidden') ? 'aact':'aacthidden';
    }
    if (img) {
        var currimage = img.src.substring(img.src.lastIndexOf('/')+1);
        img.src=(currimage=='collapsed.png')?'images/expanded.png':'images/collapsed.png';
    }
}

// Expands targets if they are hidden
function showTarget(id){
    var element = document.getElementById(id);
    while (element != document.body.rootNode ){
	if ( "aacthidden" == element.getAttribute("class") ){
	    toggle( element.id, "link-"+element.id );
	    return;
	}
	element = element.parentElement;
    }
}
function fixIndexRefs(){
    var brokeRefs = document.getElementsByClassName("dynref");
    var aa=0;
    for(aa=0; brokeRefs.length>aa; aa++){
       var linkend=(""+brokeRefs[aa].getAttribute("href")).substring(1);
       brokeRefs[aa].innerHTML+=document.getElementById(linkend).firstElementChild.textContent;
    }
}

// Called on page load to parse URL parameters and perform actions on them.
function init(){
    fixCounters("figure");
    buildIndex();
    fixIndexRefs();

    if(getQueryVariable("expand") == "on"){
	expand();
    }
}

// Pass a URL variable to this function and it will return it 's value
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


//    Expands all assurance activities
function expand(){
    var divID = "";
    var imgID = "link-";
    var hidden_elements = document.getElementsByClassName('aacthidden');
    for (var i = hidden_elements.length - 1; i >= 0; --i) {
        divID = hidden_elements[i].id;
        imgID += divID;
        toggle(divID,imgID);
        imgID = "link-";
    }
}
        </script>

        <style type="text/css">
	  <xsl:call-template name="common_css"/>

          /*       { background-color: #FFFFFF; } */
          body{
              margin-left:8%;
              margin-right:8%;
              foreground:black;
          }
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
          div.appnote{
              margin-left:0%;
              margin-top:1em;
          }
          div.aact{
              margin-left:0%;
              margin-top:1em;
              margin-bottom:1em;
              padding:1em;
              border:2px solid #888888;
              border-radius:3px;
              display:block;
          }
          .comment-aa{
              background-color:beige;
              color:green;
          }
          div.subaact{
              margin-left:0%;
              margin-top:1em;
          }
          div.aacthidden{
              margin-left:0%;
              margin-top:1em;
              margin-bottom:1em;
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
          div.expandstyle{
              display:table-cell;
              vertical-align:middle;
              padding-top:10px
          }
          span.expandstyle{
              vertical-align:middle;
              color:black;
              text-decoration:none;
              font-size:100%;
              font-weight:bold; /*font-family: verdana, arial, helvetica, sans-serif; */
          }
          .expandstyle a{
              color:black;
              text-decoration:none;
          }
          .expandstyle a:link{
              color:black;
              text-decoration:none;
          }
          .expandstyle a:visited{
              color:black;
              text-decoration:none;
          }
          .expandstyle a:hover{
              color:black;
              text-decoration:none;
          }
          .expandstyle a:active{
              color:black;
              text-decoration:none;
          }

	  sup{
   	      position: relative;
	      bottom: .5ex;
	      font-size: 80%;
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
              div.aacthidden{
                  display:none;
              }
              div.statustag{
                  box-shadow:4px 4px 3px #888888;
              }
              div.aact{
                box-shadow:0 2px 2px 0 rgba(0,0,0,.14),0 3px 1px -2px rgba(0,0,0,.2),0 1px 5px 0 rgba(0,0,0,.12);
              }
          }


          @media print{
              *.reqid{
                  font-size:90%;
                  font-family:verdana, arial,
          helvetica,
          sans-serif;
              }
              *.req{
                  margin-left:0%;
                  margin-top:1em;
                  margin-bottom:1em;
              }
              *.reqdesc{
                  margin-left:20%;
              }
              div.aacthidden{
                  padding:1em;
                  border:2px solid #888888;
                  border-radius:3px;
                  display:block;
              }

	      img[src="images/collapsed.png"] { display:none;}

          }



	  <!-- Tyring to get this to work -->
	  <!-- <xsl:if test="not($custom-css-file='')"> -->
	  <!--   <xsl:value-of select="document('file:///home/kevin/work/protection-profiles/mobile-device/mobile-device/input/Local.xml')/*)"/> -->
	  <!-- </xsl:if> -->

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
          <xsl:choose>
            <xsl:when test="$release='final'"><img src="images/niaplogo.png" alt="NIAP"/></xsl:when>
            <xsl:when test="$release='draft'"><img src="images/niaplogodraft.png" alt="NIAP"/></xsl:when>
          </xsl:choose>
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
          <xsl:for-each select="cc:RevisionHistory[@role=$release]/cc:entry">
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
  </xsl:template>
  <xsl:template name="TocElement">
    <xsl:param name="prefix"/>
    <p class="toc2">
      <xsl:value-of select="$prefix"/>.
      <a class="toc" href="#{@id}"> <xsl:value-of select="@title" /></a>
    </p>
  </xsl:template>

  <!-- <xsl:template match="cc:appendix" name="TocAppendix"> -->
  <!--   <xsl:if test="$appendicize='on' or (@id!='optional' and @id!='sel-based' and @id!='objective')"> -->
  <!--     <xsl:variable name="appendix-num"> -->
  <!--       <xsl:choose> -->
  <!--         <xsl:when test="$appendicize='on'"> -->
  <!--           <xsl:number format="A"/> -->
  <!--         </xsl:when> -->
  <!--         <xsl:otherwise> -->
  <!--           <xsl:number format="A" -->
  <!--             count="cc:appendix[@id!='optional' and @id!='objective' and @id!='sel-based']"/> -->
  <!--         </xsl:otherwise> -->
  <!--       </xsl:choose> -->
  <!--     </xsl:variable> -->
  <!--     <p xmlns="http://www.w3.org/1999/xhtml" class="toc2"> Appendix <xsl:value-of -->
  <!--         select="$appendix-num"/><xsl:text>: </xsl:text><a class="toc" href="#{@id}"><xsl:value-of -->
  <!--           select="@title"/></a></p> -->
  <!--   </xsl:if> -->
  <!-- </xsl:template> -->


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
  <xsl:template match="cc:glossary">
    <table>
      <xsl:for-each select="cc:entry">
        <xsl:element name="tr">

	  <xsl:attribute name="id">
	    <xsl:choose>
	      <xsl:when test="@id"><xsl:value-of select="@id"/></xsl:when>
	      <xsl:when test="cc:term"><xsl:value-of select="translate(cc:term/text(), $lower, $upper)"/></xsl:when>
	      <xsl:otherwise><xsl:value-of select="name/text()"/></xsl:otherwise>
	    </xsl:choose>
	  </xsl:attribute>
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

  <xsl:template match="cc:glossary/cc:entry/cc:term/cc:abbr">
    <span id="abbr_{text()}"><xsl:value-of select="@title"/> (<abbr><xsl:value-of select="text()"/></abbr>)</span>
  </xsl:template>

  <xsl:template match="cc:abbr[contains(concat('|', translate(@class, ' ', '|'), '|'), '|expanded|')]">
    <xsl:value-of select="@title"/> (<xsl:copy><xsl:apply-templates select="@*|node()"/></xsl:copy>)
  </xsl:template>

  <xsl:template match="cc:bibliography">
    <table>
      <tr class="header">
        <th>Identifier</th>
        <th>Title</th>
      </tr>
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

  <xsl:template match="cc:acronyms">
    <table>
      <tr class="header">
        <th>Acronym</th>
        <th>Meaning</th>
      </tr>
      <xsl:for-each select="cc:entry">
        <tr>
          <td>
            <xsl:apply-templates select="cc:term"/>
          </td>
          <td>
            <xsl:apply-templates select="cc:description"/>
          </td>
        </tr>
      </xsl:for-each>
    </table>
  </xsl:template>

  <xsl:template match="cc:ReferenceTable"> PP-Title:<![CDATA[&]]><xsl:value-of select="cc:PPTitle"/>
      PP-Version:<![CDATA[&]]><xsl:value-of select="cc:PPVersion"/>
      PP-Author:<![CDATA[&]]><xsl:value-of select="cc:PPAuthor"/> PP-Publication
      Date:<![CDATA[&]]><xsl:value-of select="cc:PPPubDate"/>
      Certification-ID:<![CDATA[&]]><xsl:value-of select="cc:PPCertificationID"/>
      CC-Version:<![CDATA[&]]><xsl:value-of select="cc:CCVersion"/>
      Keywords:<![CDATA[&]]><xsl:value-of select="cc:Keywords"/><xsl:for-each select="cc:entry"
        ><xsl:value-of select="cc:name"/>:<![CDATA[&]]><xsl:value-of select="cc:description"
      /></xsl:for-each></xsl:template>
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

  <xsl:template match="cc:InsertAppendixExplainer">
    <xsl:if test="$appendicize='on'"> Unconditional requirements are found in the main body of the
      document, while appendices contain the selection-based, optional, and objective requirements. </xsl:if>
    <xsl:if test="$appendicize!='on'"> The type of each requirement is identified in line with the
      text. </xsl:if>
  </xsl:template>

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
                <p/>
              </xsl:if>
            </xsl:for-each>
          </td>
        </tr>
      </xsl:for-each>
    </table>
  </xsl:template>

  <xsl:template match="cc:InsertRefMapping">
    <table>
      <tr class="header">
        <td>SFR ID</td>
        <td>NIST SP 800-53 Controls</td>
      </tr>
      <xsl:for-each select="(//cc:f-element)">
        <tr>
          <td>
            <xsl:value-of select="translate(@id,$lower,$upper)"/>
          </td>
          <td>
            <xsl:if test="not(cc:refs/cc:ref)">
              <xsl:text>None</xsl:text>
            </xsl:if>
            <xsl:for-each select="cc:refs/cc:ref">
              <p/>
              <a
                href="http://common-criteria.rhcloud.com/references/output/nist800-53controls.html#{@sect}">
                <xsl:value-of select="@sect"/>
              </a>
            </xsl:for-each>
          </td>
        </tr>
      </xsl:for-each>
    </table>
  </xsl:template>


  <!-- Used to match regular ?-components -->
  <xsl:template match="cc:f-component | cc:a-component">
    <xsl:variable name="sel">
      <!-- when we are not appending -->
      <xsl:if test="$appendicize!='on' or name()='a-component'">
        <xsl:value-of select="'_threshold_,_objective_, _optional_, _sel-based_'"/>
      </xsl:if>
      <xsl:if test="$appendicize='on'">
        <xsl:value-of select="'_threshold_'"/>
      </xsl:if>
    </xsl:variable>
    <xsl:call-template name="component-template">
      <xsl:with-param name="selected-statuses" select="$sel"/>
    </xsl:call-template>
  </xsl:template>

<!--##############################################################-->
<!--  Component template                                          -->
<!--##############################################################-->
  <xsl:template name="component-template">
    <xsl:param name="selected-statuses"/>
    <!--
	 Set id-suffix to "_threshold_" "_objective_" "_optional_" "_sel-based_"
	 based on what it is (or "" if not appendicizing).
    -->
    <xsl:variable name="id-suffix">
      <xsl:choose>
	<!-- set to nothing if appendicize is not on or we're selecting only threshold-->
        <xsl:when test="$appendicize!='on'"/>
        <xsl:when test="$selected-statuses='_threshold_'"/>
        <xsl:otherwise>
          <xsl:value-of select="$selected-statuses"/>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:variable>


    <!-- If we're not appendicizing or status is normal. Include-->
    <xsl:variable name="eff-status">_<xsl:choose>
    <xsl:when test="@status"><xsl:value-of select="@status"/></xsl:when>
    <xsl:otherwise>threshold</xsl:otherwise>
    </xsl:choose>_</xsl:variable>

    <xsl:if test="count(./*[contains($selected-statuses, $eff-status)])>0">
      <xsl:variable name="family" select="substring(@id,1,7)"/>
      <xsl:variable name="component" select="substring(@id,1,9)"/>
      <xsl:variable name="SFRID" select="@id"/>
      <!-- Make an anchor here -->
      <xsl:element name="div">
        <xsl:attribute name="class">comp</xsl:attribute>
        <xsl:attribute name="id">
          <xsl:value-of select="translate(@id, $lower, $upper)"/>
          <xsl:value-of select="$id-suffix"/>
        </xsl:attribute>
        <h4>
          <xsl:value-of select="concat(translate(@id, $lower, $upper), ' ')"/>
          <xsl:value-of select="@name"/>
        </h4>
	<xsl:apply-templates select="cc:note/text()"/>
<!-- BEGIN -->
    <xsl:if test="@status='objective'">
      <xsl:if test="$appendicize!='on'">
        <div class="statustag">
          <i>
            <b> This is an objective component.
	    <xsl:if test="@targetdate">
	      It is scheduled to be mandatory for products entering evaluation after
	      <xsl:value-of select="@targetdate"/>.
	    </xsl:if>
	    </b>
          </i>
        </div>
      </xsl:if>
      <xsl:if test="$appendicize='on' and @targetdate">
        <div class="statustag">
          <i>
            <b> This component is scheduled to be mandatory for products entering evaluations
              after <xsl:value-of select="@targetdate"/>.</b>
          </i>
        </div>
      </xsl:if>
    </xsl:if> <!-- End if objective -->

    <xsl:if test="@status='sel-based'">
      <div class="statustag">
        <b>
          <i>
            <xsl:if test="$appendicize!='on'"> This is a selection-based component. Its inclusion
              depends upon selection in </xsl:if>
            <xsl:if test="$appendicize='on'"> This component depends upon selection in </xsl:if>
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
    <xsl:if test="$appendicize!='on'">
      <xsl:if test="@status='optional'">
        <div class="statustag">
          <i><b>This is an optional component<xsl:call-template name='opt_text'/>.</b></i>
        </div>
      </xsl:if>
    </xsl:if>
<!-- END -->



	<xsl:call-template name="group">
	  <xsl:with-param name="type" select="'dev-action'"/>
	  <xsl:with-param name="selected-statuses" select="$selected-statuses"/>
	</xsl:call-template>
	<xsl:call-template name="group">
	  <xsl:with-param name="type" select="'con-pres'"/>
	  <xsl:with-param name="selected-statuses" select="$selected-statuses"/>
	</xsl:call-template>
	<xsl:call-template name="group">
	  <xsl:with-param name="type" select="'eval-action'"/>
	  <xsl:with-param name="selected-statuses" select="$selected-statuses"/>
	</xsl:call-template>

        <xsl:for-each select="cc:f-element">
          <xsl:call-template name="element-template">
	    <xsl:with-param name="selected-statuses" select="$selected-statuses"/>
          </xsl:call-template>
        </xsl:for-each>
      </xsl:element>
    </xsl:if>
  </xsl:template>

  <!-- Prints out only those templates whose status is inside selected-statuses-->
  <xsl:template name="element-template">
    <xsl:param name="selected-statuses"/>

    <xsl:variable name="eff-status"><xsl:choose>
      <xsl:when test="../@status"><xsl:value-of select="../@status"/></xsl:when>
      <xsl:otherwise>threshold</xsl:otherwise>
    </xsl:choose></xsl:variable>
    <xsl:variable name="ueff-status">_<xsl:value-of select="$eff-status"/>_</xsl:variable>

    <xsl:if test="contains($selected-statuses, $ueff-status)">
      <xsl:variable name="reqid" select="translate(@id, $lower, $upper)"/>
      <xsl:element name="div">
        <xsl:attribute name="class">req <xsl:value-of select="$eff-status"/></xsl:attribute>
        <div class="reqid" id="{$reqid}">
          <a href="#{$reqid}" class="abbr">
            <xsl:value-of select="$reqid"/>
          </a>
        </div>
        <div class="reqdesc">
          <xsl:apply-templates/>
        </div>
      </xsl:element>
    </xsl:if>
  </xsl:template>

  <xsl:template match="cc:foreword">
    <div class="foreword">
      <h1 style="text-align: center">Foreword</h1>
      <xsl:apply-templates/>      
    </div>
  </xsl:template>


  <xsl:template match="cc:title">
    <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="cc:aactivity">
    <xsl:variable name="aactID" select="concat('aactID-', generate-id())"/>
    <div class="expandstyle">
      <a href="javascript:toggle('{$aactID}', 'link-{$aactID}');">
        <span class="expandstyle"> Assurance Activity </span>
        <img style="vertical-align:middle" id="link-{$aactID}" src="images/collapsed.png"
          height="15" width="15"/>
      </a>
    </div>
    <div class="aacthidden" id="{$aactID}">
      <i>
        <xsl:apply-templates/>
      </i>
    </div>
  </xsl:template>

  <xsl:template match="cc:tss|cc:guidance|cc:tests">
    <xsl:choose>
      <xsl:when test="name()='tss'">
        <h4>TSS</h4>
      </xsl:when>
      <xsl:when test="name()='guidance'">
        <h4>Guidance</h4>
      </xsl:when>
      <xsl:when test="name()='tests'">
        <h4>Tests</h4>
      </xsl:when>
    </xsl:choose>
    <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="cc:indent">
    <div class="indent" style="margin-left:2em">
      <xsl:apply-templates/>
    </div>
  </xsl:template>


  <xsl:template match="cc:appendix">
    <xsl:if test="$appendicize='on' or (@id!='optional' and @id!='sel-based' and @id!='objective')">
      <h1 id="{@id}" class="indexable" data-level="1" data-level-alpha="true">
	Appendix
	<span class="num"></span><xsl:value-of select="$space3"/><xsl:value-of select="@title"/>
      </h1>
      <!-- Convert the words -->
      <xsl:apply-templates/>

      <!-- If we need to steal templates from the rest of the document -->
      <xsl:call-template name="requirement-stealer">
        <xsl:with-param name="selected-status" select="@id"/>
      </xsl:call-template>
    </xsl:if>
  </xsl:template>

  <xsl:template name="requirement-stealer">
    <xsl:param name="selected-status"/>
    <!-- Select all f-components which have an f-element with a selected-status-->

    <xsl:for-each select="//cc:f-component[@status=$selected-status][cc:f-element]">
      <xsl:call-template name="component-template">
        <xsl:with-param name="selected-statuses"
			select="concat('_', concat($selected-status,'_'))"/>
      </xsl:call-template>
    </xsl:for-each>
  </xsl:template>

  <xsl:template match="cc:chapter">
    <h1 id="{@id}" class="indexable" data-level="1"><span class="num"></span><xsl:value-of select="$space3"/>

      <xsl:value-of select="@title"/>
    </h1>
    <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="cc:section">
    <h2 id="{@id}" class="indexable" data-level="2"><span class="num"></span><xsl:value-of select="$space3"/>

      <xsl:value-of select="@title"/>
    </h2>
    <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="cc:subsection">

    <xsl:variable name="shouldshow">
      <xsl:if test="$appendicize!='on' or not(cc:f-component) or (*/@status='threshold')">yes</xsl:if>
    </xsl:variable>
    <xsl:variable name="is_index"><xsl:choose>
      <xsl:when test="ancestor::*[@stopindex]"/>
      <xsl:otherwise>indexable</xsl:otherwise>
    </xsl:choose></xsl:variable>
    
    <xsl:if test="contains($shouldshow,'yes')">
      <h3 id="{@id}" class="{$is_index}" data-level="{count(ancestor::*)}">
	<span class="num"></span>
	<xsl:if test="not(ancestor::*[@stopindex])"><xsl:value-of select="$space3"/></xsl:if>
	<xsl:value-of select="@title" />
      </h3>
      <xsl:apply-templates/>
    </xsl:if>
  </xsl:template>


  <xsl:template match="cc:ctr-ref">
    <a onclick="showTarget('cc-{@refid}')" href="#cc-{@refid}" class="cc-{@refid}-ref" >
      <xsl:variable name="refid"><xsl:value-of select="@refid"></xsl:value-of></xsl:variable>
      <xsl:for-each select="//cc:ctr[@id=$refid]">
	<xsl:call-template name="getPre"/>
      </xsl:for-each>
 <!--      <xsl:value-of select="//cc:ctr[@id=$refid]/@pre"/> -->
      <span class="counter"><xsl:value-of select="$refid"/></span>
    </a>
  </xsl:template>

  <!-- Need at least two objects -->
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

  <xsl:template match="cc:figure">
    <div class="figure" id="figure-{@id}">
      <img>
        <xsl:attribute name="id">
          <xsl:value-of select="@id"/>
        </xsl:attribute>
        <xsl:attribute name="src">
          <xsl:value-of select="@entity"/>
        </xsl:attribute>
        <xsl:attribute name="width">
          <xsl:value-of select="@width"/>
        </xsl:attribute>
        <xsl:attribute name="height">
          <xsl:value-of select="@height"/>
        </xsl:attribute>
      </img>
      <p/>
      <span class="ctr" data-myid="figure-{@id}" data-counter-type="ct-figure">
	<xsl:call-template name="getPre"/>
	<span class="counter"><xsl:value-of select="@id"/></span>
      </span>:
      <xsl:value-of select="@title"/>
    </div>
  </xsl:template>

  <xsl:template name="getPre">
    <xsl:choose>
      <xsl:when test="@pre"><xsl:value-of select="@pre"/></xsl:when>
      <xsl:when test="name()='figure'"><xsl:text>Figure </xsl:text></xsl:when>
      <xsl:otherwise><xsl:text>Table </xsl:text></xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <!-- templates for creating references -->
  <!-- Assumes element with matching @id has a @title. -->
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

  <xsl:template match="cc:linkref">
    <xsl:call-template name="req-refs">
      <xsl:with-param name="class">linkref</xsl:with-param>
      <xsl:with-param name="req">
        <xsl:value-of select="translate(@linkend, $upper, $lower)"/>
      </xsl:with-param>
    </xsl:call-template>
  </xsl:template>

  <xsl:template match="cc:secref">
    <a href="#{@linkend}" class="dynref">Section </a>
  </xsl:template>


  <xsl:template match="cc:appref">
    <a href="#{@linkend}" class="dynref">Appendix </a>
  </xsl:template>

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

  <xsl:template match="cc:cite">
    <xsl:variable name="linkend" select="@linkend"/>
    <xsl:element name="a">
      <xsl:attribute name="href">
        <xsl:text>#</xsl:text>
        <xsl:value-of select="$linkend"/>
      </xsl:attribute>
      <xsl:text>[</xsl:text>
      <xsl:value-of select="//cc:bibliography/cc:entry[@id=$linkend]/cc:tag"/>
      <xsl:text>]</xsl:text>
    </xsl:element>
  </xsl:template>

  <xsl:template match="cc:util">
    <span class="util">
      <xsl:apply-templates/>
    </span>
  </xsl:template>
  <xsl:template match="cc:path">
    <span class="path">
      <xsl:apply-templates/>
    </span>
  </xsl:template>

  <!-- -->
  <!-- -->
  <!-- -->
  <xsl:template name="req-refs">
    <xsl:param name="class"/>
    <xsl:param name="req"/>
    <!--lower req-->
    <xsl:variable name="lreq">
      <xsl:value-of select="translate($req,$upper,$lower)"/>
    </xsl:variable>
    <xsl:variable name="req-anchor">
      <xsl:choose>
        <xsl:when test="$appendicize!='on'"/>
        <!--
	     Elements, whether selectable or not, never get the
	     suffix in the 'id' attribute in their resulting element
	-->
	<xsl:when test="//cc:f-element[@id=$lreq]|//cc:a-element[@id=$lreq]"/>
	<xsl:when test="//*[@id=$lreq and @status='threshold']"/>
	<xsl:when test="//*[@id=$lreq and @status='sel-based']">_sel-based_</xsl:when>
	<xsl:when test="//*[@id=$lreq and @status='objective']">_objective_</xsl:when>
	<xsl:when test="//*[@id=$lreq and @status='optional']">_optional_</xsl:when>
	<xsl:otherwise>
	  <xsl:message>
    	    Broken linked element at <xsl:value-of select="$lreq"/>
	  </xsl:message>
	</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:variable name="capped-req">
      <xsl:value-of select="translate($lreq,$lower,$upper)"/>
    </xsl:variable>
    <xsl:element name="a">
      <xsl:attribute name="class">
        <xsl:value-of select="$class"/>
      </xsl:attribute>
      <xsl:attribute name="href">#<xsl:value-of select="concat($capped-req,$req-anchor)"
        /></xsl:attribute>
      <xsl:value-of select="$capped-req"/>
    </xsl:element>
  </xsl:template>

  <!-- -->
  <!-- -->
  <!-- -->

  <xsl:template name="group">
    <xsl:param name="type"/>
    <xsl:param name="selected-statuses"/>
    <xsl:if test="cc:group[@type=$type]">
      <h4>
	<xsl:choose>
	  <xsl:when test="$type='dev-action'">Developer action</xsl:when>
	  <xsl:when test="$type='con-pres'">Content and presentation</xsl:when>
	  <xsl:when test="$type='eval-action'">Evaluator action</xsl:when>
	</xsl:choose>
      elements:</h4>


      <xsl:for-each select="./cc:group[@type=$type]/cc:a-element">
        <xsl:call-template name="element-template">
	  <xsl:with-param name="selected-statuses" select="$selected-statuses"/>
        </xsl:call-template>
      </xsl:for-each>
    </xsl:if>
  </xsl:template>

  <xsl:template name="opt_text">; however, Modules for this Protection Profile might redefine it as non-optional</xsl:template>
</xsl:stylesheet>
