## Copyright (C) 2018 David Miguel Susano Pinto <david.pinto@bioch.ox.ac.uk>
##
## Copying and distribution of this file, with or without modification,
## are permitted in any medium without royalty provided the copyright
## notice and this notice are preserved.  This file is offered as-is,
## without any warranty.


## TL;DR
##
## Use like so:
##
##     export OMERO=/opt/OMERO.server-5.4.5-ice35-b83/bin/omero
##     export PYTHONPATH=/opt/OMERO.server-5.4.5-ice35-b83/lib/python/
##     make login
##     make metadata
##     make figures
##
##

## Default target is the first target, so have help here to prevent
## trigerring anything by accident.  I think there's no reasonable
## default target.
help:
	@echo "For help, read the source"


PYTHON ?= python
OMERO ?= omero
MKDIR_P ?= mkdir -p

PYTHONPATH := lib-python/:$(PYTHONPATH)


METADATA_FILE := data/raw-metadata.csv
DATA_DIR := data/
FIGURES_DIR := $(DATA_DIR)figures/

FIGURE_IDS := $(shell cut -d, -f 1 $(METADATA_FILE))
ids2file = $(patsubst %, $(FIGURES_DIR)%.$(1), $(FIGURE_IDS))
FIGURES_JSON := $(call ids2file,json)
FIGURES_JPEG := $(call ids2file,jpg)


$(FIGURES_DIR) $(DATA_DIR):
	$(MKDIR_P) $@

data/raw-metadata.csv: src/list-figures.py | $(DATA_DIR)
	## The output of this is not sorted (it's basically an SQL
	## query), so we pipe it to sort.
	$(PYTHON) $< | sort -n -t ',' -k 1 > $@

$(FIGURES_JSON): src/download-figures.py | $(METADATA_FILE) $(FIGURES_DIR)
	$(PYTHON) $< $(FIGURES_DIR) $(METADATA_FILE)

$(FIGURES_JPEG): src/figure-json2jpeg.py $(FIGURES_JSON) | $(METADATA_FILE)
	$(PYTHON) $< $(FIGURES_DIR) $(METADATA_FILE)

## TODO:
##
## I guess we should have one file data/questions/COMPARTMENT_TYPE and
## each user has a file with image ids
questions:
	$(PYTHON) src/questionnaire.py QUESTIONS_FPATH ANSWERS_DIR \
	   $(shell cut -d, -f 1 ID_TO_ASK)


login:
	$(OMERO) sessions login

metadata: data/raw-metadata.csv

jsons: $(FIGURES_JSON)

figures: $(FIGURES_JPEG)


.PHONY: help login metadata jsons figures questions
