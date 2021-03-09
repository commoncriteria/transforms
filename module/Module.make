# Point the default build to a module

RNG_FILE ?= transforms/schemas/CCModule.rng

thedefaulttarget: module-target meta-info
include $(TRANS)/Helper.make
