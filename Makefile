#
# Makefile for easier installation and cleanup.
#

PACKAGE=hugophotoswipe
DOC_DIR='./docs/'

.PHONY: help

.DEFAULT_GOAL := help

help:
	@grep -E '^[0-9a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) |\
		 awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m\
		 %s\n", $$1, $$2}'

install: ## Install for the current user using the default python command
	python setup.py install --user

install2: ## Install for the current user using the python2 command
	python2 setup.py install --user

test: ## Run nosetests using the default nosetests command
	nosetests -v

test2: ## Run nosetests using the nosetests2 command
	nosetests2 -v

cover: ## Test unit test coverage using default nosetests
	nosetests --with-coverage --cover-package=$(PACKAGE) \
		--cover-erase --cover-inclusive --cover-branches

cover2: ## Test unit test coverage using nosetests2
	nosetests2 --with-coverage --cover-package=$(PACKAGE) \
		--cover-erase --cover-inclusive --cover-branches

clean: ## Clean build dist and egg directories left after install
	rm -rf ./dist ./build ./$(PACKAGE).egg-info
	rm -rf ./${PACKAGE}/*.pyc ./${PACKAGE}/*/*.pyc
	rm -rf ./${PACKAGE}/__pycache__ ./${PACKAGE}/html/__pycache__\
		./${PACKAGE}/results/__pycache__

dist: ## Make Python source distribution
	python setup.py sdist

dist2: ## Make Python 2 source distribution
	python2 setup.py sdist

docs: doc

doc: install ## Build documentation with sphinx
	$(MAKE) -C $(DOC_DIR) html
