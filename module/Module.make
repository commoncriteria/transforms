# Point the default build to a module

RNG_FILE ?= transforms/schemas/CCModule.rng

BUILD_SD=$(call DOIT,$(PP_XML),$(TRANS)/xsl/module/module2sd.xsl,output/$(BASE)-sd.html)
#thedefaulttarget: module-target meta-info
include $(TRANS)/Helper.make
