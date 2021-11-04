# --------------------
#     Helper.make
# --------------------

# Comments in this file are structured thusly:
#   Comments that are internal to this file are commented only with '#' such as this
#   current comment.
#   Comments that are used in a javadoc fashion, describe hooks and sections
#   (such as the one preceding 'IN ?= input' line) are commented with '#-'. Also if they describe
#   something, that line must immediately follow the javadoc comment.
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

H := \#\#

#- Base name(with extensions) of input and output files
BASE ?= $(shell echo "$${PWD$H*/}")


#- Input XML file
PP_XML ?= $(IN)/$(BASE).xml

#- Folder containing TDs
TD_DIR = TDs
TDs = $(shell [ ! -d $(TD_DIR) ] || find $(TD_DIR) -name '*.xml' -type f)


#- XSL that creates regular HTML document
PP2HTML_XSL ?= $(TRANS)/xsl/pp2html.xsl

#- XSL that creates the tabularized HTML document
PP2TABLE_XSL ?= $(TRANS)/xsl/pp2table.xsl

#- XSL that creates the tabularized HTML document with just the requirements
PP2SIMPLIFIED_XSL ?= $(TRANS)/xsl/pp2simplified.xsl

#- XSL containing templates common to the other transforms
PPCOMMONS_XSL ?= $(TRANS)/xsl/ppcommons.xsl

#- XSL that creates an SD-ish document from the PP_XML 
SD_XSL ?= $(TRANS)/xsl/module2sd.xsl

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

# Path where the report with TDs applied is generated
#PP_EFFECTIVE ?= $(OUT)/$(BASE)-effective.html

#- Path where the linkable version is written
PP_LINKABLE_HTML ?= $(OUT)/$(BASE)-release-linkable.html

#- Points to Jing jar file (for validation)
JING_JAR ?= jing-*/bin/jing.jar

#- Schema
RNG_FILE ?= $(TRANS)/schemas/CCProtectionProfile.rng

#- Validation line
#- Arg 1 is the RNG file path
#- ARg 2 is the XML file path
VALIDATOR ?=java -jar $(JING_JAR) "$(1)" "$(2)"

#- Points to the daisydiff jar file
DAISY_DIR ?= ExecuteDaisy

#- Git tags that the current release should be diffed against
DIFF_TAGS?=

# This is not really a good way to do this
# Points to a folder containing files to diff the currently
# developed 'release' version against
DIFF_DIR ?= diff-archive

#- The command to diff HTML files
DIFF_EXE ?= java -jar $(DAISY_DIR)/*.jar "$(1)" "$(2)"  "--file=$(3)"

#- Points to the User.make need for diffing so that it can be
#- copied to those projects when they are automatically downloaded
#- for diffing 
DIFF_USER_MAKE ?= 


#- Your xsl transformer.
#- It should be at least XSL level-1 compliant.
#- It should be able to handle commands of the form
#- $XSL_EXE [--string-param <param-name> <param-value>]* -o <output> <xsl-file> <input>
XSL_EXE ?= xsltproc --stringparam debug '$(DEBUG)'
# Jing does not work for some reason.

#- Does the XSL
#- Arg 1 is input file
#- Arg 2 is XSL file
#- Arg 3 is output file
#- Arg 4 is parameter value pairs
DOXSL ?= $(XSL_EXE)  $(4) -o $(3)  $(2) $(1)

#- Transforms with XML and calls post-process.py
#- Arg 1 is input file
#- Arg 2 is XSL file
#- Arg 3 is output file
#- Arg 4 is parameter value pairs
DOIT ?= python3 $(TRANS)/py/retrieve-included-docs.py $1 $(OUT) &&\
	python3 $(TRANS)/py/post-process.py <($(XSL_EXE) $(4) $(2) $(1))\=$(3) 

#- Transforms with XML and calls post-process.py
#- Arg 1 is input file
#- Arg 2 is XSL file
#- Arg 3 is output file
#- Arg 4 is parameter value pairs
DOIT_SD ?= python3 $(TRANS)/py/retrieve-included-docs.py $1 $(OUT) &&\
           python3 $(TRANS)/py/post-process.py\
           <($(XSL_EXE) $(4) $(2) $(1))\=$(3)\
           <($(XSL_EXE)      $(5) $(1))\=$(6) 

FNL_PARM ?=--stringparam release final

#- Appendicize parameter
APP_PARM ?=--stringparam appendicize on

#- A temporary directory argument
TMP?=/tmp

# Transforms Version File
META_TXT ?= $(OUT)/meta-info.txt
#========================================
# TARGETS
#========================================

# .PHONY ensures that this target is built no matter what
# even if there exists a file named default
.PHONY: default meta-info all spellcheck spellcheck-esr  linkcheck pp help release clean diff little-diff listing effective


#---
#- Builds normal PP outputs (not modules)
#---
default:  $(PP_HTML) $(ESR_HTML) $(PP_RELEASE_HTML) meta-info

#- Builds all outputs
all: $(TABLE) $(SIMPLIFIED) $(PP_HTML) $(ESR_HTML) $(PP_RELEASE_HTML)

#- Spellchecks the htmlfiles using _hunspell_
spellcheck: $(ESR_HTML) $(PP_HTML)
	bash -c "hunspell -l -H -p <(cat $(TRANS)/dictionaries/*.txt $(PROJDICTIONARY)) $(OUT)/*.html | sort -u"

spellcheck-esr: $(ESR_HTML)
	bash -c "hunspell -l -H -p <(cat $(TRANS)/dictionaries/*.txt $(PROJDICTIONARY)) $(ESR_HTML) | sort -u"

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
	$(call DOIT_SD,$(PP_XML),$(PP2HTML_XSL),$(PP_RELEASE_HTML),$(FNL_PARM) $(APP_PARM),$(TRANS)/xsl/module2sd.xsl,$(SD_HTML))
	$(call DOIT,$(PP_XML),$(PP2HTML_XSL),$(PP_HTML), )
	python3 $(TRANS)/py/anchorize-periods.py $(PP_HTML) $(PP_LINKABLE_HTML) || true

#$(BASE)-sd.html: $(PP_XML)

$(PP_HTML):  $(PP2HTML_XSL) $(PPCOMMONS_XSL) $(PP_XML)
	$(call DOIT,$(PP_XML),$(PP2HTML_XSL),$(PP_HTML)        ,           )

YESTERDAY :=$(shell git log --max-count=1 --before=yesterday --pretty='format:%H')

# 1 commit
# 2 output file
# 3 User.make
# 4 Original file
DIFF_IT ?= \
        echo $1 $2 $3 $4 &&\
	rm -rf $(TMP)/$1 && mkdir -p $(TMP)/$1/$(BASE) &&\
	git clone --recursive . $(TMP)/$1/$(BASE) &&\
	if [ -r "$3" ]; then cp $3 $(TMP)/$1/$(BASE); fi &&\
	cd $(TMP)/$1/$(BASE) &&\
	echo "Bcheckout" &&\
	git checkout $1 && echo "B update" &&\
        git submodule update --recursive &&\
	PP_RELEASE_HTML=$1.html make release &&\
	cd - &&\
        pwd &&\
	$(call DIFF_EXE,$(TMP)/$1/$(BASE)/$1.html,$4,$2) &&\
	echo done
        #rm -rf $(TMP)/$1


#- Does a diff since two days ago.
little-diff: $(PP_RELEASE_HTML) $(OUT)/js
	$(call DIFF_IT,$(YESTERDAY),$(OUT)/diff-little.html,$(DIFF_USER_MAKE),$(PP_RELEASE_HTML))


diff: $(PP_RELEASE_HTML) $(OUT)/js
	if [ -d "$(DIFF_DIR)" ]; then \
	   for old in `find "$(DIFF_DIR)" -type f -name '*.html'`; do\
		$(call DIFF_EXE,$$old,$(PP_RELEASE_HTML),$(OUT)/diff-$${old##*/});\
	   done;\
           for old in `find "$(DIFF_DIR)" -type f -name '*.url'`; do\
	     base=$${old%.url};\
	     $(call DIFF_EXE,<(wget -O-  `cat $$old`),$(PP_RELEASE_HTML),$(OUT)/diff-$${base##*/}.html);\
	   done;\
	fi
	for aa in $(DIFF_TAGS); do\
		orig=$$(pwd);\
		cd $(TMP);\
		rm -rf $$aa;\
		mkdir $$aa;\
		cd $$aa;\
		git clone --recursive --branch $$aa https://github.com/commoncriteria/$${orig##*/};\
        cd $$orig; [ -r "$(DIFF_USER_MAKE)" ] && cp "$(DIFF_USER_MAKE)" $(TMP)/$$aa/$${orig##*/}; cd -;\
		cd $${orig##*/};\
		TRANS=transforms make release;\
		OLD=$$(pwd)/$(PP_RELEASE_HTML);\
		cd $$orig;\
		pwd;\
		(while sleep 60; do echo '#'; done) &\
		$(call DIFF_EXE,$$OLD,$(PP_RELEASE_HTML),$(OUT)/diff-$${aa}.html);\
#		rm -rf $(TMP)/$$aa;\
		kill %1;\
        done

# Following was attempted to removed garbage collection limit exception (But then it fails
# on timeout, so it was probably wise to keep the gc exception).
#		java -XX:-UseGCOverheadLimit -jar $(DAISY_DIR)/*.jar "$$OLD" "$(PP_RELEASE_HTML)"  --file="$(OUT)/diff-$${aa}.html";\

# Copies over resources needed by DIFF
$(OUT)/js:
	cp -r $(DAISY_DIR)/js $(OUT)
	[ -d "$(OUT)/css"    ] || cp -r $(DAISY_DIR)/css $(OUT)	
	[ -d "$(OUT)/images" ] || mkdir "$(OUT)/images"
	cp -u $(DAISY_DIR)/images/* $(OUT)/images


#- Target to build the anchorized report
$(PP_LINKABLE_HTML): $(PP_RELEASE_HTML) 
	python3 $(TRANS)/py/anchorize-periods.py $(PP_RELEASE_HTML) $(PP_LINKABLE_HTML) || true


#- Target to build the release report
#- It also builds the anchorized version (but doesn't care if it succeeds)
release: $(PP_RELEASE_HTML)
$(PP_RELEASE_HTML): $(PP2HTML_XSL) $(PPCOMMONS_XSL) $(PP_XML)
	$(call DOIT,$(PP_XML),$(PP2HTML_XSL),$(PP_RELEASE_HTML),$(APP_PARM) $(FNL_PARM))
	python3 $(TRANS)/py/anchorize-periods.py $(PP_RELEASE_HTML) $(PP_LINKABLE_HTML) || true
	$(BUILD_SD)

# Target to build the effective
# effective: $(PP_EFFECTIVE)
# $(PP_EFFECTIVE): $(PP2HTML_XSL) $(PPCOMMONS_XSL) $(PP_XML) $(TDs)
# 	python3 $(TRANS)/py/apply_tds.py $(PP_XML) $(TDs) $(OUT)/effective.xml
# 	$(call DOIT,$(OUT)/effective.xml,$(PP2HTML_XSL),$(PP_EFFECTIVE),$(APP_PARM) $(FNL_PARM))



inter:
	$(call DOXSL,$(PP_XML),$(PP2HTML_XSL),abc.xml,$(APP_PARM))
#- Builds the essential security requirements
esr:$(ESR_HTML)
$(ESR_HTML):  $(TRANS)/xsl/esr2html.xsl $(PPCOMMONS_XSL) $(ESR_XML)
	$(call DOXSL,  $(ESR_XML),  $(TRANS)/xsl/esr2html.xsl, $(ESR_HTML),)

#- Builds the PP in html table form
table: $(TABLE)
$(TABLE): $(PP2TABLE_XSL) $(PP_XML)
	$(call DOXSL, $(PP_XML), $(PP2TABLE_XSL), $(TABLE), $(FNL_PARAM))
#	$(XSL_EXE) $(FNL_PARM) -o $(TABLE) $(PP2TABLE_XSL) $(PP_XML)

#- Builds the PP in simplified html table form
simplified: $(SIMPLIFIED)
$(SIMPLIFIED): $(PP2SIMPLIFIED_XSL) $(PP_XML)
	$(call DOXSL, $(PP_XML), $(PP2SIMPLIFIED_XSL), $(SIMPLIFIED), $(FNL_PARAM))
#	$(XSL_EXE) $(FNL_PARM) -o $(SIMPLIFIED) $(PP2SIMPLIFIED_XSL) $(PP_XML)

#- The HTML listing file
listing:
	cd $(OUT) &&\
	(echo "<html><head><title>$(BASE)</title></head><body><ol>" &&\
	   for aa in $$(find . -name '*.html'); do\
		echo "<li><a href='$$aa'>$$aa</a></li>";\
	   done;\
	 echo "</ol></body></html>") > index.html


#- Validates the input XML file. It probably requires the JING package
validate:
	$(call VALIDATOR,$(RNG_FILE),$(PP_XML))

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

meta-info:
	echo -n 'T_VER=' > $(META_TXT)
	(\
	  cd transforms &&\
	  (git branch|tail -n 1|cut -c 3-) &&\
	  echo - &&\
	  ( git log -1 --date=iso --format=%cd | tr ' ' '_')\
	) |  tr -d " \t\n\r"     >> $(META_TXT)
	echo -en '\nBUILD_TIME=' >> $(META_TXT)
	date +"%Y-%m-%d %H:%M"   >> $(META_TXT)

# git checkout $(git log --before today -n 1 --pretty="format:%P")
# git submodule update --recursive
