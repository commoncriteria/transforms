BASE=CCProtectionProfile
SHELL=/bin/bash


FLATN=rng-to-html/bin/rng-resolve-includes.py

TOHTML?=rng-to-html/bin/rng-to-html <($(FLATN) $(1)) $(1).html;
TORNC=trang -I rng -O rnc  $1 $1.rnc;


files := $(shell grep -l '<start>' *.rng) 

default: 
	$(foreach ff, $(files), $(call TOHTML,$(ff)))
rncs:
	$(foreach ff, $(files), $(call TORNC,$(ff)))

all: docs rnc
docs: $(BASE).html

rnc: $(BASE).rnc
$(BASE).rnc: $(BASE).rng
	$(foreach ff, $(files), $(

clean: 
	rm -f *.rnc *.html
