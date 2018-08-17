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

# If we don't specify it, make will default to the less featureful bourne shell
SHELL=/bin/bash

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

#- Points to the daisydiff jar file
DAISY_DIR ?= ../ExecuteDaisy

#- Git tags that the current release should be diffed against
DIFF_TAGS?=

# This is not really a good way to do this
# Points to a folder containing files to diff the currently
# developed 'release' version against
DIFF_DIR ?= diff-archive

#- Your xsl transformer.
#- It should be at least XSL level-1 compliant.
#- It should be able to handle commands of the form
#- $XSL_EXE [--string-param <param-name> <param-value>]* -o <output> <xsl-file> <input>
XSL_EXE ?= xsltproc --stringparam debug '$(DEBUG)'

#- TRANSFORM 1 using 2 into 3 [with 4 options]
DOIT ?= $(XSL_EXE) $(4) $(2) $(1) | python3 $(TRANS)/post-process.py -::$(3) 

FNL_PARM ?=--stringparam release final
#- Appendicize parameter
APP_PARM ?=--stringparam appendicize on

#- A temporary directory argument
TMP?=--stringparam tmpdir /tmp/

#---
#- Builds everything but worksheet
#---
default: $(TABLE) $(SIMPLIFIED) $(PP_HTML) $(ESR_HTML) $(PP_RELEASE_HTML)

#- Builds all outputs
all: $(TABLE) $(SIMPLIFIED) $(PP_HTML) $(ESR_HTML) $(PP_RELEASE_HTML) $(WORKSHEET_HTML)

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
#       Download all remote base-pps
	[ $(SKIP) == 1 ] || python3 $(TRANS)/pre-process.py $(PP_XML) /tmp
	$(call DOIT,$(PP_XML),$(TRANS)/module/module2html.xsl,$(PP_RELEASE_HTML),$(TMP))
	$(call DOIT,$(PP_XML),$(TRANS)/module/module2sd.xsl,output/$(BASE)-sd.html) 
	$(call DOIT,$(PP_XML),$(PP2HTML_XSL),$(PP_HTML))

$(PP_HTML):  $(PP2HTML_XSL) $(PPCOMMONS_XSL) $(PP_XML)
	$(call DOIT,$(PP_XML),$(PP2HTML_XSL),$(PP_HTML) )
	$(call DOIT,$(PP_XML),$(PP2HTML_XSL),$(PP_RELEASE_HTML),$APP_PARM)


#- Build the Diff file
diff: $(PP_RELEASE_HTML)
	[ ! -d "$(DIFF_DIR)" ] ||\
	   for old in `find "$(DIFF_DIR)" -type f -name '*.html'`; do\
	     java -jar $(DAISY_DIR)/*.jar "$$old" "$(PP_RELEASE_HTML)"  --file="$(OUT)/diff-$${old##*/}";\
	   done;\
           for old in `find "$(DIFF_DIR)" -type f -name '*.url'`; do\
	     base=$${old%.url}; java -jar $(DAISY_DIR)/*.jar <(wget -O-  `cat $$old`) $(PP_RELEASE_HTML)   --file="$(OUT)/diff-$${base##*/}.html";\
	   done
	for aa in $(DIFF_TAGS); do\
		orig=$$(pwd);\
		cd $(TMP);\
		rm -rf $$aa;\
		mkdir $$aa;\
		cd $$aa;\
		git clone --recursive --branch $$aa https://github.com/commoncriteria/$${orig##*/};\
		cd $${orig##*/};\
		make;\
		OLD=$$(pwd)/$(PP_RELEASE_HTML);\
		cd $$orig;\
		pwd;\
		java -jar $(DAISY_DIR)/*.jar "$$OLD" "$(PP_RELEASE_HTML)"  --file="$(OUT)/diff-$${aa}.html";\
#		rm -rf $(TMP)/$$aa;\
	done
	[ -d "$(OUT)/js"  ] || cp -r $(DAISY_DIR)/js $(OUT)
	[ -d "$(OUT)/css" ] || cp -r $(DAISY_DIR)/css $(OUT)	



#- Target to build the release report
release: $(PP_RELEASE_HTML)
$(PP_RELEASE_HTML): $(PP2HTML_XSL) $(PPCOMMONS_XSL) $(PP_XML)
	$(call DOIT,$(PP_XML),$(PP2HTML_XSL),$(PP_RELEASE_HTML),$(APP_PARM))

#- Builds the essential security requirements
esr:$(ESR_HTML)
$(ESR_HTML):  $(TRANS)/esr2html.xsl $(PPCOMMONS_XSL) $(ESR_XML)
	$(XSL_EXE) -o $(ESR_HTML) $(TRANS)/esr2html.xsl $(ESR_XML)

#- Builds the PP in html table form
table: $(TABLE)
$(TABLE): $(PP2TABLE_XSL) $(PP_XML)
	$(call DOIT,$(PP_XML),$(PP2TABLE_XSL),$(TABLE),$(FNL_PARM)) 

#- Builds the PP in simplified html table form
simplified: $(SIMPLIFIED)
$(SIMPLIFIED): $(PP2SIMPLIFIED_XSL) $(PP_XML) transforms/pp2simplified.xsl
	$(XSL_EXE) $(FNL_PARM) -o $(SIMPLIFIED) $(PP2SIMPLIFIED_XSL) $(PP_XML)

#- Builds the PP worksheet
worksheet: $(WORKSHEET_HTML)
$(WORKSHEET_HTML): $(PP_XML)
	python3 $(TRANS)/worksheet/pp-to-worksheet.py $(TRANS)/worksheet/Worksheet.js $(TRANS)/worksheet/Worksheet.css $(TRANS)/worksheet/ResultsToSt.xsl $(PP_XML)::$(WORKSHEET_HTML)




#- Builds quick help
help:
	grep -A 1 '^#-' -r $(TRANS)/*.make --include='*.make' -h

#- Build to clean the system
clean:
	rm -rf $(OUT)/js $(OUT)/css $(OUT)/*.*

#- Does a git safe push
git-safe-push:
	git pull origin
	make clean
	make
	git push origin

#- Pulls in the latest transforms module into the project
git-update-transforms:
	git submodule update --remote transforms
