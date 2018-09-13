BASE=CCProtectionProfile
SHELL=/bin/bash


FLATN=rng-to-html/bin/rng-resolve-includes.py

TOHTML?=rng-to-html/bin/rng-to-html <($(FLATN) $(1)) $(1).html;
TORNC=trang -I rng -O rnc  $1 $1.rnc;


files := $(shell grep -l '<start>' *.rng) 

default: docs
docs:
	$(foreach ff, $(files), $(call TOHTML,$(ff)))
rncs:
	$(foreach ff, $(files), $(call TORNC,$(ff)))

clean: 
	rm -f *.rnc *.html
