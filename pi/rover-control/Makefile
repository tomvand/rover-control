SHELL := /bin/bash


freeze:
	(source venv/bin/activate || true) && pip freeze --local | grep -v "pkg-resources" > requirements.txt
.PHONY: freeze
