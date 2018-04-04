<?xml version="1.0" encoding="utf-8"?>
<!--
    Stylesheet for Protection Profile Schema
    Subsequent modifications in support of US NIAP
-->

<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:cc="https://niap-ccevs.org/cc/v1"
  xmlns="http://www.w3.org/1999/xhtml"
  xmlns:htm="http://www.w3.org/1999/xhtml"
  version="1.0">


  <!-- Variable for selecting how much debugging we want -->
  <xsl:param name="debug" select="'v'"/>

  <xsl:include href="ppcommons.xsl"/>


  <xsl:template match="/cc:PP">

    <!-- Start with !doctype preamble for valid (X)HTML document. -->
    <xsl:text disable-output-escaping='yes'>&lt;!DOCTYPE html&gt;&#xa;</xsl:text>
    <html xmlns="http://www.w3.org/1999/xhtml">
      <head>
	<xsl:element name="title"><xsl:value-of select="//cc:PPTitle"/> Worksheet</xsl:element>
        <style type="text/css">
    input[type=checkbox] + span {
       opacity: .6;
    }

    input[type=checkbox]:checked + span {
       opacity: 1;
    }

    .words{
       padding-left: 40px;
    }
    .f-el-title{
       font-family: monospace;
       font-size: x-large;
    }

    .sidenav .valid .stat::before,
    .valid .f-el-title::before{
       content: "\\2713";
       color: #0F0;
    }

    .sidenav .invalid .stat::before,
    .invalid .f-el-title::before{
       content: "\\2715";
       color: #F00;
    }


    .disabled {
       opacity: .2;
       pointer-events: none;
    }
    
    .warning{
       text-align:center;
       border-style: dashed;
       border-width: medium;
       border-color: red;
    }
    .sidenav {
        height: 100%;            /* 100% Full-height */
        position: fixed;         /* Stay in place */
        z-index: 1;              /* Stay on top */
        top: 0;                  /* Stay at the top */
        left: 0;
        width: 40px; 
        overflow-x: hidden;      /* Disable horizontal scroll */
        transition: 0.5s;        /* 0.5 second transition effect to slide in the sidenav */
        background-color: #FFF;  /* Black*/
        border-right: thin dotted #AAA;
     }

    .sidenav:hover{
        width: 200px;
    }

    .sidenav a{
        display: none;
        text-decoration: none;
    }

    .sidenav tr.disabled{
        display: none;
    }


    .sidenav:hover a{
        display: inline;
    }
    #main{
       margin-left:50px;
    }

           </style>

           <script Type='text/javascript'>

    const AMPERSAND=String.fromCharCode(38);
    const LT=String.fromCharCode(60);

    var cookieJar=[];
    /**
     * This runs some sort of function on
     * all elements of a class.
     * @param classname Value of the class 
     * @param fun Function that is run on all elements. 
     *    For its 1st parameter, it takes the element. For the 2nd
     *    it's the number of the element.
     */
    function performActionOnClass(classname, fun){
        // Run through all the elements with possible
        // values
        var aa;
        var elems = document.getElementsByClassName(classname);
        for(aa=0; elems.length> aa; aa++){
           fun(elems[aa], aa);
        }
    }
    var prevCheckbox = false;
    function isPrevCheckbox(elem){
        var ret = prevCheckbox;
        prevCheckbox = false;
        return ret;
    }

    function isCheckbox(elem){
        return elem.getAttribute("type") == "checkbox";
    }

    function getId(index){
        return "v_" + index;
    } 

    var prefix="";
    function saveToCookieJar(elem, index){
        var id = prefix+":"+getId(index);
        if( isCheckbox(elem)){
            cookieJar[id]=elem.checked;
        }
        else if( elem.tagName == 'SELECT' ){
            cookieJar[id]=elem.selectedIndex;
        }
        else{
            if(elem.value != undefined){
               if( elem.value != "undefined" ) cookieJar[id]=elem.value;
            }
        }
    }

    function retrieveFromCookieJar(elem, index){
        var id = prefix+":"+getId(index);
        if( isCheckbox(elem)){
            elem.checked= (cookieJar[id] == "true");
        }
        else if( elem.tagName == 'SELECT' ){
            if( id in cookieJar ){
               elem.selectedIndex = cookieJar[id];
            }
        }
        else{
            if( id in cookieJar) {
               if(cookieJar[id] != "undefined"){
                  elem.value= cookieJar[id];
               }
            }
        }
    }
    var prefix="";

    function init(){
        if( document.URL.startsWith("file:///") ){
           var warn = document.getElementById("url-warning");
           warn.style.display='block';
        }
        var url = new URL(document.URL);
        prefix = url.searchParams.get("prefix");
        cookieJar = readAllCookies();
        performActionOnClass("val", retrieveFromCookieJar);
        validateRequirements();
    }

    function readAllCookies() {
            ret=[];
            var ca = document.cookie.split(';');
            var aa,bb;
            for(aa=0;ca.length > aa ; aa++) {
                if (3>ca[aa].length){ continue;}
                var blah=ca[aa].split('=');
                if (2 != blah.length){
                   console.log("Malformed Cookie.");
                   continue;
                }
                key=blah[0].trim();
                console.log("Read " + key);
                val=decodeURIComponent(blah[1]);
                ret[key]=val;
            }
            return ret;
    }

    function saveAllCookies(cookies){
        var key;
        // run through the cookies
        for (key in cookies) {
           console.log("Saving off "+key);
           createCookie(key, cookies[key] );
        }
    }

    function createCookie(name,value) {
        var date = new Date();
        // 10 day timeout
        date.setTime(date.getTime()+(10*24*60*60*1000));
        var expires = "; expires="+date.toGMTString();
        document.cookie = name+"="+encodeURIComponent(value)+expires+"; path=/";

    }

    function eraseCookie(name) {
        createCookie(name,"",-1);
    }

    function generateReport(){
        var report = LT+"?xml version='1.0' encoding='utf-8'?>\\n"
        var aa;
       
        report += LT+"report xmlns='https://niap-ccevs.org/cc/pp/report/v1'>"
        var kids = document.getElementsByClassName('requirement');
        for(aa=0; kids.length>aa; aa++){
            report += "\\n"+LT+"req id='"+kids[aa].id+"'>";
            report +=getRequirement(kids[aa]);
            report += LT+"/req>\\n";
        }
        report += LT+"/report>";
        initiateDownload('Report.text', report);
    }

    function getRequirements(nodes){
      ret="";
      var bb=0;
      for(bb=0; bb!=nodes.length; bb++){
         ret+=getRequirement(nodes[bb]);
      }
      return ret;
    }

    function convertToXmlContent(val){
        var ret = val;
        ret = ret.replace(/\\&amp;/g, '&amp;amp;');
        ret = ret.replace(/\\&lt;/g, '&amp;lt;');
        ret = ret.replace(/\\]\\]\\>/g, ']]&amp;gt;');
        return ret;
    }

    function getRequirement(node){
        var ret = ""
        // If it's an element
        if(node.nodeType==1){
           if(isPrevCheckbox(node)){
               return "";
           }
           if(isCheckbox(node)){
               if(node.checked){
                  ret+=LT+"selectable index='"+node.getAttribute('data-rindex')+"'>"; 
                  ret+=getRequirement(node.nextSibling);
                  ret+=LT+"/selectable>";
               }
               prevCheckbox=true;
           }
           else if(node.classList.contains("selectables")){
               ret+=LT+"selectables>"
               ret+=getRequirements(node.children);
               ret+=LT+"/selectables>"
           }
           else if(node.classList.contains("assignment")){
               var val = "";
               if(node.value){
                 val=node.value;
               }
               ret+=LT+"assignment>";
               ret+=convertToXmlContent(val);
               ret+=LT+"/assignment>\\n";
           }
           else if(node.classList.contains('mfun-table')){
               ret += LT+"management-function-table>"
               var rows = node.getElementsByTagName("tr");
               // Skip first row
               for(var row=1; rows.length>row; row++){
                  ret += LT+"management-function>";
                  var cols=rows[row].getElementsByTagName("td");
                  for( var col=1; cols.length>col; col++){
                     ret += LT+"val>"; 
                     if( cols[col].children.length == 0 ){
                        ret += cols[col].textContent;
                     }
                     else{
                        var si = cols[col].children[0].selectedIndex;
                        if(si!=-1){
                           ret += cols[col].children[0].children[si].textContent;
                        }
                     }
                     ret += LT+"/val>";
                  }
                  ret += LT+"/management-function>\\n";
               }
               ret += LT+"/management-function-table>";
           }
           else{
               ret+=getRequirements(node.children);
           }
        }
        // If it's text
        else if(node.nodeType==3){
           return node.textContent;
        }
        return ret;
    }

    function initiateDownload(filename, data) {

        var blob = new Blob([data], {type: 'text/xml'});
        if(window.navigator.msSaveOrOpenBlob) {
            window.navigator.msSaveBlob(blob, filename);
        }
        else{
            var elem = window.document.createElement('a');
            elem.href = window.URL.createObjectURL(blob);
            elem.download = filename;        
            document.body.appendChild(elem);
            elem.click();        
            document.body.removeChild(elem);
        }
    }

    function chooseMe(sel){
       var common = sel.parentNode;
       while( common.tagName != "SPAN" ){
          common = common.parentNode;
       }
       toggleFirstCheckboxExcept(common, sel);
    }

    var selbasedCtrs={}

    function areAnyMastersSelected(id){
       var masters = document.getElementsByClassName(id+"_m");
       for(bb=0; masters.length>bb; bb++){
          if (masters[bb].checked){
             return true;
          }
       }
       return false;
    }

    function modifyClass( el, clazz, isAdd ){
      if(el == null){
          console.log("Failed to find element with id: " + id);
          return false;
      }
      if(isAdd) el.classList.add(clazz);
      else      el.classList.remove(clazz);
      return true;
    }
    /* 
     * This design does not account for cascading dependent components .
     * There are none currently, so this limitation is acceptable.
     */
    function updateDependency(root, ids){
       var aa, bb;

       // Run through all 
       for(aa=0; ids.length>aa; aa++){     
          var enabled = areAnyMastersSelected(ids[aa]);
          // We might need to recur on these if the selection-based
          // requirement had a dependent selection-based requirement.
          modifyClass( document.getElementById(ids[aa]), "disabled", !enabled);
          var sn_s = document.getElementsByClassName(ids[aa]);
          for(bb=0; sn_s.length>bb; bb++){
             modifyClass(sn_s[bb], "disabled", !enabled)
          }
       }
    }

    var sched;
    function update(){
       if (sched != undefined){
         clearTimeout(sched);
       }
       sched = setTimeout(delayedUpdate, 1000);
    }

    function validateSelectables(sel){
       var child  = sel.firstElementChild;
       if( child.tagName == 'UL' ){
          child=child.firstElementChild;
       }
       var numChecked=0;
       // Now we either have a checkbox or an li
       while(child!=null){
          if(child.tagName == "LI"){
             if(child.firstElementChild.checked){
                numChecked++;
                if( !reqValidator(child) ){
                   return false;
                }
             }
          }
          else if(child.checked){
                numChecked++;
                if( !reqValidator(child) ){
                   return false;
                }
          }
          child = child.nextElementSibling;
       }
       if(numChecked==0) return false;
       if(numChecked==1) return true;
       return !sel.classList.contains("onlyone");
    }

    function reqValidator(elem){
        var child = elem.firstElementChild;
        var ret;
        while(child != null){
           if( child.classList.contains("selectables")){
              ret = validateSelectables(child);
              if(!ret) return false;
           }
           else if( child.classList.contains("assignment")){
              if(! child.value) return false;
           }
           else{
              ret = reqValidator(child);
              if(!ret) return false;
           }
           child = child.nextElementSibling;
        }
        return true;
    }

    function validateRequirements(){
        var aa;
        var reqs = document.getElementsByClassName('requirement');
        for(aa=0; reqs.length > aa; aa++){
             var indy =   document.getElementById("sn_"+reqs[aa].id);
             if(reqValidator(reqs[aa])){
                 indy.classList.add('valid');
                 indy.classList.remove('invalid');
                 reqs[aa].classList.add('valid');
                 reqs[aa].classList.remove('invalid');
             }
             else{
                 indy.classList.add('invalid');
                 indy.classList.remove('valid');
                 reqs[aa].classList.add('invalid');
                 reqs[aa].classList.remove('valid');
             }
        }
    }


    function delayedUpdate(){
       performActionOnClass("val", saveToCookieJar);
       saveAllCookies(cookieJar);

       validateRequirements();
       sched = undefined;
    }

    function toggleFirstCheckboxExcept(root, exc){
       if (root == exc) return;
       if ( isCheckbox(root)){
          if( exc.checked ){
             root.disabled=true;
             root.classList.add('disabled');
             root.nextSibling.classList.add('disabled');
             root.checked=false;
          }
          else{
             root.disabled=false;
             root.classList.remove('disabled');
             root.nextSibling.classList.remove('disabled');
          }
          return;
       }
       var children = root.children;
       var aa;
       for (aa=0; aa!=children.length; aa++){
          toggleFirstCheckboxExcept(children[aa], exc);
       }
    }

           </script>
	 </head>
	 <body onload='init();'>
	   <div id="main">

	     <h1> Worksheet for the <xsl:value-of select="//cc:PPTitle"/></h1>
	     <noscript>
	     <h1 class="warning">This page requires JavaScript.</h1></noscript>
	     <h2 class="warning" id='url-warning' style="display: none;">
	       Most browsers do not store cookies from local pages (i.e, 'file:///...').
	       When you close this page, all data will most likely be lost.
             </h2>

	     <xsl:apply-templates/>


             <br/>
             <button type="button" onclick="generateReport()">Generate Report</button>
           </div> <!-- End of main -->
	   <div class="sidenav">
	     <div style="font-size: xx-large">&#187;</div>
             <table>
             </table>
	   </div>
	 </body>
    </html>
  </xsl:template>




  
</xsl:stylesheet>
