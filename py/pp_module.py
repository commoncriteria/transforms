import generic_pp_doc

class ppmod(generic_pp_doc.generic_pp_doc):
    def __init__(self, root, workdir, output, boilerplate):
        super().__init__(root, workdir, output, boilerplate)
        
    def title(self):
        node = self.rf("//cc:PPTitle")
        if node is not None:
            return node.text
        if "target-products" in self.root.attrib:
            return "PP-Module for " + self.root.attrib["target-products"]
        else:
            ret = "PP-Module for " +  self.root.attrib["target-product"] + "s"
            return ret

    def ppdoctype_short(self):
        return "PP-Module"
        
    def handle_conformance_claims(self, node):
        self.o("""
    <dl>
        <dt>Conformance Statement</dt>
        <dd>
          <p>This PP-Module inherits exact conformance as required from the specified
          Base-PP and as defined in the CC and CEM addenda for Exact Conformance, Selection-based
          SFRs, and Optional SFRs (dated May 2017).</p>
          <p>The following PPs and PP-Modules are allowed to be specified in a 
            PP-Configuration with this PP-Module. </p> <ul>
""")
        bases = self.rfa("//cc:base-pp")
        for base in bases:
            self.o("<li>")
            self.make_xref(base)
            self.ol("</li>")
        self.ol("</ul>\n")
        self.ol("</dd>")
        self.ol("<dt>CC Conformance Claims</dt>")
        self.ol("<dd>This PP-Module is conformant to Parts 2 (extended) and 3 (conformant) of Common Criteria "+self.ccver()+".</dd>")
        self.ol("<dt>PP Claim </dt>")
        self.ol("<dd>This PP-Module does not claim conformance to any Protection Profile. </dd>")
        self.ol("<dt>Package Claim</dt>")
        self.ol("<dd>This PP-Module")
        pks = self.rfa("//cc:include-pkg")
        ctr=len(pks)
        if ctr == 0:
            self.o("does not claim conformance to any packages")
        else:
            lagsep=""
            for pk in pks:
                ctr=ctr-1
                self.o(lagsep)
                lagsep=","
                if ctr==2 :
                    lagsep="and"
                self.show_package(pk)
            self.o("conformant")
        self.ol(".</dd>")
        self.ol("</dl>")
        
        
        
    def handle_other_hooks(self, title, node):
        return
