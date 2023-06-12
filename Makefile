LINTER=.venv/bin/ruff


all: help


venv:  ## Create and initialize a local virtual env
	rm -rf venv .venv
	python -m venv .venv
	.venv/bin/pip install -U --disable-pip-version-check pip
	.venv/bin/pip install -r requirements-dev.txt


lint:  ## Perform code sanity checks if needed
	test -z "$$(git status --porcelain -s -- .)" || (git diff --cached --name-only | grep -E '.py$$' | xargs ${LINTER})


lint-all:  ## Perform full codebase sanity checks
	${LINTER} prose


clean:  ## Purge temporary files
	rm -rf coverage.xml *.egg-info build/ .eggs/ tmp/ htmlcov/ test-reports/
	find . -name '.ropeproject' -exec rm -rf {} \;
	find . -name '*,cover' -delete
	find . -name '*.pyc' -delete
	find . -name '__pycache__' -delete


clean-all: clean  ## Fully purge environment
	rm -rf .venv dist


help:  ## Show this help.
	@grep -E "^[^._][a-zA-Z_-]*:" Makefile | awk -F '[:#]' '{print $$1, ":", $$NF}' | sort | column -t -s:


.SILENT: venv lint lint-all clean clean-all help
.PHONY: venv lint lint-all clean clean-all help
