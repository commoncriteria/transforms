# Comments in this file are structured thusly:
#   Comments that are internal to this file are commented only with '#' such as this
#   current comment.
#   Comments that are used in a javadoc fashion, describe hooks and sections
#   (such as the one preceding 'IN ?= input' line) are commented with '#-'. Also if they describe
#   something, that line should immediately follow the javadoc comment.
#
# This file is intentially not called [Mm]akefile, because it is not meant to be called
# directly. Rather the project directory should have a "Makefile" that
# defines all the environment variables then includes this one.
# For example:
#   ```
#   TRANS?=transforms
#   -include LocalUser.make
#   include $(TRANS)/Helper.make
#   ```
# LocalUser.make is where each user would add their appropriate hooks. The file should not be committed 
# to git.


#---
#- Hooks
#---

#- Path to input files
IN ?= input

#- Path where output files are written
OUT ?= output

#- Local dictionary file
PROJDICTIONARY ?= local/Dictionary.txt

#- FPath
TRANS ?= transforms

#- Debugging levels '','v','vv' make sense right now.
DEBUG ?= v

#- Base name(with extensions) of input and output files
BASE ?= $(shell abc=`pwd`;echo $${abc\#\#*/})

#- Input XML file
PP_XML ?= $(IN)/$(BASE).xml

#- Input XML file
SD_XML ?= $(IN)/$(BASE)-sd.xml

#- XSL that creates regular HTML document
PP2HTML_XSL ?= $(TRANS)/pp2html.xsl

#- XSL that creates the tabularized HTML document
PP2TABLE_XSL ?= $(TRANS)/pp2table.xsl

#- XSL that creates the tabularized HTML document with just the requirements
PP2SIMPLIFIED_XSL ?= $(TRANS)/pp2simplified.xsl

#- XSL containing templates common to the other transforms
PPCOMMONS_XSL ?= $(TRANS)/ppcommons.xsl

#- Path to input XML document for the esr
ESR_XML ?= $(IN)/esr.xml

#- Output of the SD Document
SD_HTML ?= $(OUT)/$(BASE)-sd.html

#- Path where tabularized html document
TABLE ?= $(OUT)/$(BASE)-table.html

#- Path where tabularized html document with just the requirements
SIMPLIFIED ?= $(OUT)/$(BASE)-table-reqs.html

#- Path where the basic report is written
PP_HTML ?= $(OUT)/$(BASE).html

#- Path where the ESR is written
ESR_HTML ?= $(OUT)/$(BASE)-esr.html

#- Path where the report that has the different appendices for the different types of requirements is written
PP_OP_HTML ?= $(OUT)/$(BASE)-optionsappendix.html

#- Path where the release report is written
PP_RELEASE_HTML ?= $(OUT)/$(BASE)-release.html

#- Path to worksheet
WORKSHEET_HTML ?= $(OUT)/$(BASE)-worksheet.html

#- Your xsl transformer.
#- It should be at least XSL level-1 compliant.
#- It should be able to handle commands of the form
#- $XSL_EXE [--string-param <param-name> <param-value>]* -o <output> <xsl-file> <input>
XSL_EXE ?= xsltproc --stringparam debug '$(DEBUG)'
#---
#- Build targets
#---
#- Builds all
all: $(TABLE) $(SIMPLIFIED) $(PP_HTML) $(ESR_HTML) $(PP_RELEASE_HTML)

#- Spellchecks the htmlfiles using _hunspell_
spellcheck: $(ESR_HTML) $(PP_HTML)
	bash -c "hunspell -l -H -p <(cat $(TRANS)/dictionaries/*.txt $(PROJDICTIONARY)) $(OUT)/*.html | sort -u"

spellcheck-esr: $(ESR_HTML)
	bash -c "hunspell -l -H -p <(cat $(TRANS)/dictionaries/*.txt $(PROJDICTIONARY)) $(ESR_HTML) | sort -u"

spellcheck-os:  $(PP_HTML)
	bash -c "hunspell -l -H -p <(cat $(TRANS)/dictionaries/*.txt $(PROJDICTIONARY)) $(PP_HTML) | sort -u"

#- Checks the internal links to make sure they point to an existing anchor
linkcheck: $(TABLE) $(SIMPLIFIED) $(PP_HTML) $(ESR_HTML) $(PP_OP_HTML) $(PP_RELEASE_HTML)
	for bb in $(OUT)/*.html; do for aa in $$(\
	  sed "s/href=['\"]/\nhref=\"/g" $$bb | grep "^href=[\"']#" | sed "s/href=[\"']#//g" | sed "s/[\"'].*//g"\
        ); do grep "id=[\"']$${aa}[\"']" -q  $$bb || echo "Detected missing link $$bb-$$aa"; done; done

#- Target to build the normal report
pp:$(PP_HTML)


# Personalized CSS file
#EXTRA_CSS ?=
#	$(XSL_EXE) --stringparam custom-css-file $(EXTRA_CSS) -o $(PP_HTML) $(PP2HTML_XSL) $(PP_XML)

module-target:
	$(XSL_EXE) -o $(PP_HTML) $(TRANS)/module2html.xsl $(PP_XML)
	$(XSL_EXE) -o $(SD_HTML) $(PP2HTML_XSL) $(SD_XML)

$(PP_HTML):  $(PP2HTML_XSL) $(PPCOMMONS_XSL) $(PP_XML)
	$(XSL_EXE)  -o $(PP_HTML) $(PP2HTML_XSL) $(PP_XML)
	$(XSL_EXE) --stringparam appendicize on -o $(PP_OP_HTML) $(PP2HTML_XSL) $(PP_XML)
	$(XSL_EXE) --stringparam appendicize on -o $(PP_RELEASE_HTML) $(PP2HTML_XSL) $(PP_XML)

#- Target to build the release report
release: $(PP_RELEASE_HTML)
$(PP_RELEASE_HTML): $(PP2HTML_XSL) $(PPCOMMONS_XSL) $(PP_XML)
	$(XSL_EXE) --stringparam appendicize on -o $(PP_RELEASE_HTML) $(PP2HTML_XSL) $(PP_XML)

#- Builds the essential security requirements
esr:$(ESR_HTML)
$(ESR_HTML):  $(TRANS)/esr2html.xsl $(PPCOMMONS_XSL) $(ESR_XML)
	$(XSL_EXE) -o $(ESR_HTML) $(TRANS)/esr2html.xsl $(ESR_XML)

#- Builds the PP in html table form
table: $(TABLE)
$(TABLE): $(PP2TABLE_XSL) $(PP_XML)
	$(XSL_EXE)  --stringparam release final -o $(TABLE) $(PP2TABLE_XSL) $(PP_XML)

#- Builds the PP in simplified html table form
simplified: $(SIMPLIFIED)
$(SIMPLIFIED): $(PP2SIMPLIFIED_XSL) $(PP_XML) transforms/pp2simplified.xsl
	$(XSL_EXE) --stringparam release final -o $(SIMPLIFIED) $(PP2SIMPLIFIED_XSL) $(PP_XML)

#- Builds the PP worksheet
worksheet: $(WORKSHEET_HTML)
$(WORKSHEET_HTML): $(PP_XML)
	python3 $(TRANS)/python/pp-to-worksheet.py $(PP_XML):$(WORKSHEET_HTML)

#- Builds quick help
help:
	$(info $(shell echo -e "Here are the possible make targets (Hopefully they are self-explanatory)\x3A\n"))
	$(info $(shell grep -e $$(echo -e \\x3A) Makefile $(TRANS)/*.make -h | grep -v -e "^\\$$"| awk 'BEGIN { FS = "\x3A" } {print $$1}' ))

#- Builds more detailed help
more-help:
	grep -A 1 '^#-' Makefile $(TRANS)/*.make -h

#- Build to clean the system
clean:
	@for f in a $(TABLE) $(SIMPLIFIED) $(PP_HTML) $(PP_RELEASE_HTML) $(PP_OP_HTML) $(ESR_HTML) $(WORKSHEET_HTML) $(CONFIGANNEX_HTML); do \
		if [ -f $$f ]; then \
			rm "$$f"; \
		fi; \
	done

#- Does a git safe push
git-safe-push:
	git pull origin
	make clean
	make
	git push origin

#- Pulls in the latest transforms module into the project
git-update-transforms:
	git submodule update --remote transforms
