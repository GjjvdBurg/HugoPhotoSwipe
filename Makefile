# Makefile for easier installation and cleanup.
#
# Uses self-documenting macros from here:
# http://marmelab.com/blog/2016/02/29/auto-documented-makefile.html

SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c
MAKEFLAGS += --warn-undefined-variables --no-builtin-rules

PACKAGE=hugophotoswipe
VENV_DIR=/tmp/hps_venv

.PHONY: help

.DEFAULT_GOAL := help

help:
	@grep -E '^[0-9a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) |\
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m\
		%s\n", $$1, $$2}'

################
# Installation #
################

.PHONY: install

install: ## Install for the current user using the default python command
	python setup.py install --user

################
# Distribution #
################

.PHONY: release dist

release: ## Make a release
	python make_release.py

dist: ## Make Python source distribution
	python setup.py sdist bdist_wheel

###########
# Testing #
###########

.PHONY: test

test: venv ## Run unit tests in virtual environment
	source $(VENV_DIR)/bin/activate && green -a -s 1 -vv ./tests

test_direct: ## Run unit tests without virtual environment (typically for CI)
	pip install .[tests] && python -m unittest discover -v ./tests


#######################
# Virtual environment #
#######################

.PHONY: venv

venv: $(VENV_DIR)/bin/activate ## Create a virtual environment

$(VENV_DIR)/bin/activate:
	test -d $(VENV_DIR) || python -m venv $(VENV_DIR)
	source $(VENV_DIR)/bin/activate && pip install -e .[dev]
	touch $(VENV_DIR)/bin/activate

############
# Clean up #
############

clean_venv: ## Clean up the virtual environment
	rm -rf $(VENV_DIR)

clean: ## Clean build dist and egg directories left after install
	rm -rf ./dist
	rm -rf ./build
	rm -rf ./$(PACKAGE).egg-info
	rm -rf ./cover
	rm -rf $(VENV_DIR)
	rm -f MANIFEST
	rm -f ./*_valgrind.log*
	find . -type f -iname '*.pyc' -delete
	find . -type d -name '__pycache__' -empty -delete
