## Copyright (C) 2018 David Miguel Susano Pinto <david.pinto@bioch.ox.ac.uk>
##
## Copying and distribution of this file, with or without modification,
## are permitted in any medium without royalty provided the copyright
## notice and this notice are preserved.  This file is offered as-is,
## without any warranty.

PYTHON ?= python

data/raw-metadata.csv: src/handle-figures.py
	## The output of this is not sorted (it's basically an SQL
	## query, so we pipe it to sort.
	$(PYTHON) $< list-figures | sort -n -t ',' -k 1 > $@

data/figures/all: src/handle-figures.py data/raw-metadata.csv
	$(PYTHON) $< download-json data/figures/ data/raw-metadata.csv
	touch data/figures/all
