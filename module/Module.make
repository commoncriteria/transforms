# Point the default build to a module

RNG_FILE ?= transforms/schemas/CCModule.rng
SD_HTML ?= $(OUT)/$(BASE)-sd.html

BUILD_SD=$(call DOIT,$(PP_XML),$(TRANS)/xsl/module2sd.xsl,$(SD_HTML))
thedefaulttarget: module-target meta-info
include $(TRANS)/Helper.make
