<?xml version="1.0" encoding="utf-8"?>
<!--
    Audit Events XSL
-->

<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:cc="https://niap-ccevs.org/cc/v1"
  xmlns:sec="https://niap-ccevs.org/cc/v1/section"
  xmlns="http://www.w3.org/1999/xhtml"
  xmlns:htm="http://www.w3.org/1999/xhtml"
  version="1.0">

  <!-- ############### -->
  <!--                 -->
  <!-- ############### -->
  <xsl:template match="cc:audit-table[cc:depends]">
      <!-- This is the same as the audit-events template below, just with a different name.
           The other one should disappear eventually. -->
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
              <xsl:variable name="rid" select="cc:ref-id"/>
              "<xsl:value-of select="//cc:feature[@id=$rid]/@title"/>"
            </xsl:if>
            </li>
        </xsl:for-each> </ul><br/>
        <xsl:call-template name="audit-table"/>
      </div>        
  </xsl:template>    

	
  <!-- ############### -->
  <!--                 -->
  <!-- ############### -->
   <xsl:template match="cc:audit-events[cc:depends]">
      <div class="dependent"> The following audit events are included if:
         <ul> <xsl:for-each select="cc:depends">
            <li>
            <xsl:if test="@on='selection'">
              <xsl:for-each select="cc:ref-id">  
                <xsl:variable name="uid" select="text()"/>
                "<xsl:apply-templates select="//cc:selectable[@id=$uid]"/>"
              </xsl:for-each>
               is selected from 
              <xsl:variable name="uid" select="cc:ref-id[1]/text()"/>
              <xsl:apply-templates select="//cc:f-element[.//cc:selectable/@id=$uid]" mode="getId"/>
            </xsl:if> 
            <xsl:if test="@on='implements'">
              the TOE implements 
              <xsl:for-each select="cc:ref-id">
                 <xsl:variable name="ref-id" select="text()"/>
                 <xsl:if test="position()!=1">, </xsl:if>
                 "<xsl:value-of select="//cc:feature[@id=$ref-id]/@title"/>"
              </xsl:for-each>
            </xsl:if>
            </li>
        </xsl:for-each> </ul><br/>
        <xsl:call-template name="audit-events"/>
      </div>        
  </xsl:template>

  <xsl:template match="/cc:PP//cc:f-component|/cc:Package//cc:f-component" mode="compute-fcomp-status">
      <xsl:if test="not(@status)">mandatory</xsl:if><xsl:value-of select="@status"/>
  </xsl:template>
 
  <xsl:template match="/cc:Module//cc:f-component" mode="compute-fcomp-status"><xsl:choose>
    <xsl:when test="ancestor::cc:sel-sfrs">sel-based</xsl:when>
    <xsl:when test="ancestor::cc:opt-sfrs">optional</xsl:when>
    <xsl:when test="ancestor::cc:obj-sfrs">objective</xsl:when>
    <xsl:when test="ancestor::cc:man-sfrs">mandatory</xsl:when>
    <xsl:when test="ancestor::cc:base-pp">base-based</xsl:when>
    <xsl:when test="ancestor::cc:impl-dep-sfrs">feat-based</xsl:when>
    <xsl:otherwise><xsl:message>Detected unknown status of f-compoenent in mandatory <xsl:apply-templates mode="getId" select="."/></xsl:message></xsl:otherwise>
  </xsl:choose></xsl:template>
  <!-- ############### -->
  <!-- This template for audit tables is invoked from XML. --> 
  <!-- This one gets called for the main audit table in FAU_GEN.1 -->
  <!-- ############### -->
  <xsl:template match="cc:audit-table" name="audit-table">
    <xsl:param name="thistable" select="@table"/>


    <xsl:variable name="nicename"><xsl:choose>
      <xsl:when test="$thistable='sel-based'">Selection-based</xsl:when>
      <xsl:otherwise><xsl:value-of select="concat(translate(substring($thistable,1,1),$lower,$upper), substring($thistable,2))"/></xsl:otherwise>
    </xsl:choose></xsl:variable>
    
    <table class="" border="1">
<!--      <xsl:if test="not(node())">-->
        <caption><xsl:call-template name="ctr-xsl">
         <xsl:with-param name="ctr-type" select="'Table'"/>
	 <xsl:with-param name="id" select="concat('t-audit-',$thistable)"/>
         </xsl:call-template>: Auditable Events for <xsl:value-of select="$nicename"/> Requirements</caption>
<!--      </xsl:if>-->
      <!--<xsl:apply-templates/>-->
        <tr><th>Requirement</th>
        <th>Auditable Events</th>
        <th>Additional Audit Record Contents</th></tr>
    <xsl:for-each select="//cc:f-component">
	<xsl:variable name="fcomp" select="."/>
	<xsl:variable name="fcompstatus"><xsl:apply-templates select="." mode="compute-fcomp-status"/></xsl:variable>   
        <xsl:for-each select="cc:audit-event"> 
            <!-- The audit event is included in this table only if
                - The audit event's expressed table attribute matches this table
                - Or the table attribute is not expressed and the audit event's default audit attribute matches this table.
                - The default table for an audit event is the same as the status attribute of the enclosing f-component.  -->
            <xsl:if test="(@table=$thistable) or (not(@table) and ($fcompstatus=$thistable))">
                <tr>
                    <td><xsl:apply-templates select="$fcomp" mode="getId"/></td>      <!-- SFR name -->
                    <xsl:choose>
                        <xsl:when test="(not (cc:audit-event-descr))">
                            <td>No events specified.</td><td>N/A</td>
                        </xsl:when>
                        <xsl:otherwise>
                            <xsl:choose>
				<!-- When audit events are individually selectable -->
                                <xsl:when test="@type='optional'">
					<td> <b>[selection: </b><i> <xsl:apply-templates select="cc:audit-event-descr"/>, None</i><b>].</b> </td>
                                </xsl:when>
                                <xsl:otherwise>
                                   <td><xsl:apply-templates select="cc:audit-event-descr"/></td>
                                </xsl:otherwise>
                            </xsl:choose>
			    <xsl:choose>
			      <xsl:when test="cc:audit-event-info">
                            <td>
				<xsl:for-each select="cc:audit-event-info">
					<xsl:choose>
	    				<xsl:when test="@type='optional'">
		    				<b>[selection: </b>
		    					<i><xsl:apply-templates select="."/>
			    				, None</i><b>].</b>
	    				</xsl:when>
	   			 	<xsl:otherwise>
						<xsl:apply-templates select="."/>
	    				</xsl:otherwise>
	 			 	</xsl:choose>
					
		 	<!--		<xsl:apply-templates select="."/> --> <br />   
				</xsl:for-each>
			    </td>
				    </xsl:when>
				    <xsl:otherwise>
					    <td>None.</td>
				    </xsl:otherwise>
				</xsl:choose>
                        </xsl:otherwise>
                    </xsl:choose>
               </tr>
            </xsl:if>
        </xsl:for-each>
    </xsl:for-each>
  </table>
  </xsl:template>

  
  <!-- ############### -->
  <!--                 -->
  <!-- ############### -->
  <xsl:template match="cc:audit-event-info" mode="intable">
	<xsl:choose>
	    <xsl:when test="@type='optional'">
		    <b>[selection: </b>
		    <i><xsl:apply-templates select="cc:audit-event-info"/>
			    , None</i><b>].</b>
	    </xsl:when>
	    <xsl:otherwise>
			<xsl:apply-templates select="cc:audit-event-info"/>
	    </xsl:otherwise>
	  </xsl:choose>
  </xsl:template>
    
   
  <!-- ############### -->
  <!--                 -->
  <!-- ############### -->
   <xsl:template match="cc:audit-events" name="audit-events">
    <xsl:variable name="table" select="@table"/>
    <xsl:apply-templates/>
    <table class="" border="1">
    <tr><th>Requirement</th>
        <th>Auditable Events</th>
        <th>Additional Audit Record Contents</th></tr>
    <xsl:for-each select="//cc:f-component">
      <tr>
         <td><xsl:apply-templates select="." mode="getId"/></td>
         <xsl:choose>
            <xsl:when test="not(cc:audit-event[cc:table/@known=$table]|cc:audit-event[cc:table/@other=$table])">
              <td>No events specified.</td><td>N/A</td>
            </xsl:when>
            <xsl:otherwise>
              <xsl:apply-templates select="cc:audit-event[cc:table/@known=$table]|cc:audit-event[cc:table/@other=$table]" mode="intable"/>
            </xsl:otherwise>
         </xsl:choose>
      </tr>
    </xsl:for-each>
    </table>
  </xsl:template>

  <!-- ############### -->
  <!--                 -->
  <!-- ############### -->
  <xsl:template match="cc:audit-event" mode="intable">
    <td>
       <xsl:if test="@type='optional'">[OPTIONAL]</xsl:if>
       <xsl:apply-templates select="cc:description"/>
    </td>
    <td><xsl:if test="not(cc:add-info)">-</xsl:if>
             <xsl:apply-templates select="cc:add-info"/>
    </td>
  </xsl:template>
	



</xsl:stylesheet>
