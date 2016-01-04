all: docs/t1.html rnc

docs/t1.html: schema.rng docs
	rng-to-html/bin/rng-to-html schema.rng docs
docs:
	mkdir docs

rnc: schema.rnc
schema.rnc: schema.rng
	trang -I rng -O rnc  schema.rng schema.rnc

clean: 
	rm -rf schema.rnc docs
