const AMPERSAND=String.fromCharCode(38);
const LT=String.fromCharCode(60);

/// Holds the prefix for the settings we care about
var prefix="";

/// Dictionary to hold all the cookies
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

function retrieveBase(name){
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
	    pp_xml = xhttp.responseXML.documentElement
        }
    };
    xhttp.open("GET", name, true);
    xhttp.send();
}


// elem is a component element
function handleEnter(elem){
    if (elem != null){
        elem.classList.remove('hide');
    }

    var compsIter, comps;
    comps = document.getElementsByClassName('component');
    for (compsIter=comps.length-1; compsIter>=0; compsIter--){
        if (comps[compsIter]==elem) continue;
        comps[compsIter].classList.add('hide');
    }
}

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

function init(){
    if( document.URL.startsWith("file:///") ){
        var warn = document.getElementById("url-warning");
        warn.style.display='block';
    }
    var url = new URL(document.URL);
    prefix=url.searchParams.get("prefix");
    if (prefix==null) prefix="";
    cookieJar = readAllCookies();
    performActionOnClass("val", retrieveFromCookieJar);
    validateRequirements();
    handleEnter(null);
}
function resolver(pre){
    if(pre=='cc') return 'https://niap-ccevs.org/cc/v1';
    else return "http://www.w3.org/1999/xhtml";
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
        val=decodeURIComponent(blah[1]);
        ret[key]=val;
    }
    return ret;
}

function saveAllCookies(cookies){
    var key;
    // run through the cookies
    for (key in cookies) {
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
function fullReport(){
    var pp_xml = new DOMParser().parseFromString(atob(ORIG64), "text/xml");
    //- Fix up selections
    var xsels = pp_xml.evaluate("//cc:selectable", pp_xml, resolver, XPathResult.ANY_TYPE, null);
    var hsels = document.getElementsByClassName('selbox');
    var hsindex = 0;
    var choosens = new Set();
    while(true){
        var xmlsel = xsels.iterateNext();
        if( xmlsel == null ) break;
        if( hsindex == hsels.length) break;
        if( hsels[hsindex].checked ){
            // Can't mutate it while iterating
            // Keep a set
            //xmlsel.setAttribute("selected", "yes");
            choosens.add(xmlsel);
        }
        hsindex++;
    }
    for(let choosen of choosens){
        choosen.setAttribute("selected", "yes");
    }
    var ctr=0;

    //- Fix up assignments
    var xassigns = pp_xml.evaluate("//cc:assignable", pp_xml, resolver, XPathResult.ANY_TYPE, null)
    var assignments = [];
    while(true){
        var xassign = xassigns.iterateNext();
        if(xassign == null) break;
        assignments[ctr] = xassign;
        ctr++;
    }
    var hassigns = document.getElementsByClassName('assignment');
    for(ctr = 0; hassigns.length>ctr; ctr++){
        if(hassigns[ctr].value){
            assignments[ctr].setAttribute("val", hassigns[ctr].value);
        }
    }

    //- Fix up components
    var xcomps = pp_xml.evaluate("//cc:f-component|//cc:a-component", pp_xml, resolver, XPathResult.ANY_TYPE, null);
    var hcomps = document.getElementsByClassName('component');
    var disableds = new Set();
    for(ctr=0; hcomps.length>ctr; ctr++){
        var xcomp = xcomps.iterateNext();
        if(xcomp==null) break;
        if( hcomps[ctr].classList.contains('disabled') ){
            disableds.add(xcomp);
            console.log("Adding something");
        }
    }
    for(let disabled of disableds){
        disabled.setAttribute("disabled", "yes");
    }

    var xsl = new DOMParser().parseFromString(atob(XSL64), "text/xml");

    // var win = window.open("", "Report");
    // var htmlReport = transform(xsl, pp_xml, win.document);
    // win.document.body.appendChild( htmlReport );

    // This doesn't work on Chrome. THe max string size cuts us off.
    // var serializer = new XMLSerializer();
    // var xmlString = serializer.serializeToString(pp_xml);
    // var resultStr = (new XMLSerializer()).serializeToString(htmlReport);
    // console.log("Result size: " +resultStr.length);

    var htmlReport = transform(xsl, pp_xml, document);
    var rNode = document.getElementById('report-node');
    rNode.appendChild( htmlReport );


    var myBlobBuilder = new MyBlobBuilder();
    myBlobBuilder.append("<html><head><title></title></head><body>");
    myBlobBuilder.append(rNode.innerHTML);
    myBlobBuilder.append("</body></html>");
    initiateDownload('FullReport.html', myBlobBuilder.getBlob("text/html"));
}


function generateReport(){
    var report = LT+"?xml version='1.0' encoding='utf-8'?>\n"
    var aa;
    report += LT+"report xmlns='https://niap-ccevs.org/cc/pp/report/v1'>"
    var kids = document.getElementsByClassName('requirement');
    var isInvalid = false;
    for(aa=0; kids.length>aa; aa++){
        if( kids[aa].classList.contains("invalid") ){
            isInvalid = true;
        }
        report += "\n"+LT+"req id='"+kids[aa].id+"'>";
        report +=getRequirement(kids[aa]);
        report += LT+"/req>\n";
    }
    report += LT+"/report>";
    if( isInvalid ){
        alert("Warning: You are downloading an incomplete report.");
    }
    var blobTheBuilder = new MyBlobBuilder();
    blobTheBuilder.append(report);

    initiateDownload('Report.xml', blobTheBuilder.getBlob("text/xml"));
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
    ret = ret.replace(/\x26/g, AMPERSAND+'amp;');
    ret = ret.replace(/\x3c/g, AMPERSAND+'lt;');
    ret = ret.replace(/\]\]\>/g, ']]'+AMPERSAND+'gt;');
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
                // Like a fake recurrence call here
                ret+=getRequirement(node.nextSibling);
                ret+=LT+"/selectable>";
            }
            // Skip the next check.
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
            ret+=LT+"/assignment>\n";
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
                ret += LT+"/management-function>\n";
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

function initiateDownload(filename, blob) {
//    var blob = new Blob([data], {type: mimetype});
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
function setFocusOnComponent(comp){
    comp.getElementsByClassName('f-comp-title')[0].focus();
    return true;
}

function handleKey(event){
    if(! event.ctrlKey ) return;
    var key = event.which || event.keyCode;
    var curr = document.activeElement;
    var comps = document.getElementsByClassName('component');
    if (comps.length == 0) return;
    if (curr==document.body){
        curr=null;
    }
    var aa;
    if( key == 28){
        if (curr == null) curr =  comps[comps.length-1];
        for(aa=comps.length-1; aa >= 0; aa--){
            if(comps[aa] == curr) break;
            if(comps[aa].contains(curr)) break;
        }
        for(aa--; aa>=0; aa--){
            if(comps[aa].classList.contains('disabled')) continue;
            if(comps[aa].classList.contains('invalid')){
                return setFocusOnComponent(comps[aa]);
            }
        }
        return "";
    }
    else if( key == 30){
        if (curr == null) curr =  comps[0];
        for(aa=0; comps.length > aa; aa++){
            if(comps[aa] == curr) break;
            if(comps[aa].contains(curr)) break;
        }
        for(aa++; comps.length > aa; aa++){
            if(comps[aa].classList.contains('disabled')) continue;
            if(comps[aa].classList.contains('invalid')){
                return setFocusOnComponent(comps[aa]);
            }
        }
        return "";
    }
    else if (key==31){
        handleHelpRequest();
    }
}
function handleHelpRequest(){
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
        if(reqValidator(reqs[aa])){
            addRemoveClasses(reqs[aa],'valid','invalid');
        }
        else{
            addRemoveClasses(reqs[aa],'invalid','valid');
        }
    }
    var components = document.getElementsByClassName('component');
    for(aa=0; components.length > aa; aa++){
        if(components[aa].getElementsByClassName('invalid').length == 0 ){
            addRemoveClasses(components[aa],'valid','invalid');
        }
        else{
            addRemoveClasses(components[aa],'invalid','valid');
        }
    }
}

function addRemoveClasses(elem, addClass, remClass){
    elem.classList.remove(remClass);
    elem.classList.add(addClass);
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

// Function to expand and contract a given div
function toggle(descendent) {
    var cl = descendent.parentNode.classList;
    if (cl.contains('hide')){
      cl.remove('hide');
    }
    else{
      cl.add('hide');
    }
}

function transform(xsl, xml, owner){
    // code for IE
    if (window.ActiveXObject ){
        return xml.transformNode(xsl);
    }
    // code for Chrome, Firefox, Opera, etc.
    else if (document.implementation && document.implementation.createDocument){
        var xsltProcessor = new XSLTProcessor();
	xsltProcessor.importStylesheet(xsl);
        return xsltProcessor.transformToFragment(xml, owner);
    }
}

// Took this from stack overflow
// Class
var MyBlobBuilder = function() {
  this.parts = [];
}

MyBlobBuilder.prototype.append = function(part) {
  this.parts.push(part);
  this.blob = undefined; // Invalidate the blob
};

MyBlobBuilder.prototype.getBlob = function(mimetype) {
  if (!this.blob) {
    this.blob = new Blob(this.parts, { type: mimetype });
  }
  return this.blob;
};




