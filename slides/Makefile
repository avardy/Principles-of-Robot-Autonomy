SHELL := /bin/bash
.DEFAULT_GOAL := all

LATEXMK ?= latexmk
LATEXMK_FLAGS ?= -pdf -interaction=nonstopmode -halt-on-error -shell-escape
PDFJAM ?= pdfjam
PDFJAM_FLAGS ?= --landscape --frame true --nup 2x2 --scale 0.9 --delta '1cm 1cm'
PDFJAM_ENV ?= env LC_ALL=C

SLIDE_TEX := $(filter-out common_preamble.tex,$(wildcard *.tex))

ifeq ($(strip $(HANDOUT)),1)
OUTPUT_SUFFIX :=
JOBNAME_SUFFIX :=
else
OUTPUT_SUFFIX := _present
JOBNAME_SUFFIX := _present
endif

OUTPUT_PATTERN := %$(OUTPUT_SUFFIX).pdf

ifeq ($(strip $(SLIDES)),)
BUILD_SOURCES := $(SLIDE_TEX)
else
BUILD_SOURCES := $(addsuffix .tex,$(basename $(SLIDES)))
endif

ifeq ($(strip $(HANDOUT)),1)
EXTRA_TARGETS := $(BUILD_SOURCES:%.tex=%_quad.pdf)
else
EXTRA_TARGETS :=
endif

BUILD_TARGETS := $(BUILD_SOURCES:%.tex=%$(OUTPUT_SUFFIX).pdf) $(EXTRA_TARGETS)

.PHONY: all clean clean-all list help

all: $(BUILD_TARGETS)

$(OUTPUT_PATTERN): %.tex common_preamble.tex
	@echo "Building $@ (HANDOUT=$(HANDOUT))"
	if [ "$(HANDOUT)" = "1" ]; then \
		wrapper="$*.handout.tex"; \
		printf '\\PassOptionsToClass{handout}{beamer}\n\\input{%s}\n' "$<" > "$$wrapper"; \
		$(LATEXMK) $(LATEXMK_FLAGS) -jobname=$*$(JOBNAME_SUFFIX) "$$wrapper"; \
		rm -f "$$wrapper"; \
	else \
		$(LATEXMK) $(LATEXMK_FLAGS) -jobname=$*$(JOBNAME_SUFFIX) $<; \
	fi

%_quad.pdf: %.pdf
	@echo "Generating 2x2 print layout $@"
	$(PDFJAM_ENV) $(PDFJAM) $(PDFJAM_FLAGS) --outfile "$@" "$<"

clean:
	@for tex in $(BUILD_SOURCES); do \
		if [ -f $$tex ]; then \
			base=$${tex%.tex}; \
			echo "Cleaning $$tex"; \
			$(LATEXMK) -c $$tex >/dev/null; \
			$(LATEXMK) -jobname=$${base}_present -c $$tex >/dev/null 2>&1 || true; \
			rm -f $${base}_quad.pdf $$base.nav $$base.snm $$base.vrb $${base}_present.nav $${base}_present.snm $${base}_present.vrb; \
		fi; \
	done

clean-all:
	@for tex in $(SLIDE_TEX); do \
		base=$${tex%.tex}; \
		echo "Purging $$tex"; \
		$(LATEXMK) -C $$tex >/dev/null; \
		$(LATEXMK) -jobname=$${base}_present -C $$tex >/dev/null 2>&1 || true; \
		rm -f $$base.pdf $${base}_present.pdf $${base}_quad.pdf; \
		rm -f $$base.nav $$base.snm $$base.vrb $${base}_present.nav $${base}_present.snm $${base}_present.vrb; \
	done

list:
	@printf "Available decks:\n"
	@for tex in $(SLIDE_TEX); do printf "  %s\n" "$$tex"; done

help:
	@echo "Examples:"
	@echo "  make                # build every deck"
	@echo "  make SLIDES=ch03 ap01  # build only ch03 + ap01"
	@echo "  make HANDOUT=1 SLIDES=ch03  # build ch03 in handout mode"
	@echo "  make clean SLIDES=ch03  # clean aux files for ch03"
	@echo "  make clean-all      # remove aux + pdf for all decks"
