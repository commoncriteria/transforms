# This file is intentially not called [Mm]akefile, because it is not meant to be called
# directly. Rather the project directory should have a "Makefile" that includes this, eg-
#   ```
#   TRANS?=transforms
#   include $(TRANS)/Helper.make
#   ```

IN ?= input
OUT ?= output
# You can easily build with another set of transforms (ie the developer ones) by running
#    make <target> TRANS=/path/to/transforms
PROJDICTIONARY ?= Dictionary.txt
TRANS ?= transforms

# If base not set, grab it from the directory name
BASE ?= $(shell abc=`pwd`;echo $${abc\#\#*/})
PP_XML ?= $(IN)/$(BASE).xml

PP2HTML_XSL ?= $(TRANS)/pp2html.xsl
PPCOMMONS_XSL ?= $(TRANS)/ppcommons.xsl
PP2TABLE_XSL ?= $(TRANS)/pp2table.xsl
PP2SIMPLIFIED_XSL ?= $(TRANS)/pp2simplified.xsl

ESR_XML=$(IN)/esr.xml
TABLE=$(OUT)/$(BASE)-table.html
SIMPLIFIED=$(OUT)/$(BASE)-table-reqs.html
PP_HTML=$(OUT)/$(BASE).html
ESR_HTML=$(OUT)/$(BASE)-esr.html
PP_OP_HTML=$(OUT)/$(BASE)-optionsappendix.html
PP_RELEASE_HTML=$(OUT)/$(BASE)-release.html


all: $(TABLE) $(SIMPLIFIED) $(PP_HTML) $(ESR_HTML) $(PP_RELEASE_HTML)


spellcheck: $(ESR_HTML) $(PP_HTML)
	bash -c "hunspell -l -H -p <(cat $(TRANS)/dictionaries/*.txt $(PROJDICTIONARY)) $(OUT)/*.html | sort -u"

spellcheck-esr: $(ESR_HTML)
	bash -c "hunspell -l -H -p <(cat $(TRANS)/dictionaries/*.txt $(PROJDICTIONARY)) $(ESR_HTML) | sort -u"	

spellcheck-os:  $(PP_HTML)
	bash -c "hunspell -l -H -p <(cat $(TRANS)/dictionaries/*.txt $(PROJDICTIONARY)) $(PP_HTML) | sort -u"

linkcheck: $(TABLE) $(SIMPLIFIED) $(PP_HTML) $(ESR_HTML) $(PP_OP_HTML) $(PP_RELEASE_HTML)
	for bb in $(OUT)/*.html; do for aa in $$(\
	  sed "s/href=['\"]/\nhref=\"/g" $$bb | grep "^href=[\"']#" | sed "s/href=[\"']#//g" | sed "s/[\"'].*//g"\
        ); do grep "id=[\"']$${aa}[\"']" -q  $$bb || echo "Detected missing link $$bb-$$aa"; done; done


pp:$(PP_HTML)
$(PP_HTML):  $(PP2HTML_XSL) $(PPCOMMONS_XSL) $(PP_XML)
	xsltproc -o $(PP_HTML) $(PP2HTML_XSL) $(PP_XML)
	xsltproc --stringparam appendicize on -o $(PP_OP_HTML) $(PP2HTML_XSL) $(PP_XML)
	xsltproc --stringparam appendicize on --stringparam release final -o $(PP_RELEASE_HTML) $(PP2HTML_XSL) $(PP_XML)

$(PP_RELEASE_HTML): $(PP2HTML_XSL) $(PPCOMMONS_XSL) $(PP_XML)
	xsltproc --stringparam appendicize on --stringparam release final -o $(PP_RELEASE_HTML) $(PP2HTML_XSL) $(PP_XML)


esr:$(ESR_HTML)
$(ESR_HTML):  $(TRANS)/esr2html.xsl $(PPCOMMONS_XSL) $(ESR_XML)
	xsltproc -o $(ESR_HTML) $(TRANS)/esr2html.xsl $(ESR_XML)

table: $(TABLE)
$(TABLE): $(PP2TABLE_XSL) $(PP_XML)
	xsltproc  --stringparam release final -o $(TABLE) $(PP2TABLE_XSL) $(PP_XML)

simplified: $(SIMPLIFIED) 
$(SIMPLIFIED): $(PP2SIMPLIFIED_XSL) $(PP_XML) transforms/pp2simplified.xsl
	xsltproc --stringparam release final -o $(SIMPLIFIED) $(PP2SIMPLIFIED_XSL) $(PP_XML)

rnc: $(TRANS)/schemas/schema.rnc
$(TRANS)/schemas/schema.rnc: $(TRANS)/schemas/schema.rng
	trang -I rng -O rnc  $(TRANS)/schemas/schema.rng $(TRANS)/schemas/schema.rnc
help:
	$(info $(shell echo -e "Here are the possible make targets (Hopefully they are self-explanatory)\x3A\n"))
	$(info $(shell grep -e $$(echo -e \\x3A) Makefile $(TRANS)/Helper.make -h | grep -v -e "^\\$$"| awk 'BEGIN { FS = "\x3A" } {print $$1}' ))
clean:
	@for f in a $(TABLE) $(SIMPLIFIED) $(PP_HTML) $(PP_RELEASE_HTML) $(PP_OP_HTML) $(ESR_HTML); do \
		if [ -f $$f ]; then \
			rm "$$f"; \
		fi; \
	done
