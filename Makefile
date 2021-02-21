.DEFAULT_GOAL := help

# Job parameter: src directory.
CURRENT_DIR := $(shell pwd)

.PHONY: help format lint install.dependencies version.get

#help:	@ List available tasks on this project
help:
	@grep -E '[a-zA-Z\.\-]+:.*?@ .*$$' $(MAKEFILE_LIST)| tr -d '#'  | awk 'BEGIN {FS = ":.*?@ "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

#install.dependencies: @ install dependencies.
install.dependencies:
	@echo "> Installing dependencies."; \
	python3 -m venv venv; \
	. venv/bin/activate; \
	venv/bin/python3 -m pip install --upgrade pip; \
	venv/bin/pip install -r $(CURRENT_DIR)/requirements-dev.txt -r $(CURRENT_DIR)/requirements.txt

#format: @ Format code
format:
	@echo "> Formatting."; \
	venv/bin/autopep8 -ir main.py

#lint: @ Lint package
lint:
	@echo "> Linting."; \
	echo "Running pycodestyle."; \
	venv/bin/pycodestyle main.py; \
	echo "Running pylint."; \
	venv/bin/pylint main.py

#version.get: @ Gets the version value.
version.get:
	@venv/bin/bump2version --allow-dirty --dry-run --list patch | grep current_version | sed "s|^.*=||";