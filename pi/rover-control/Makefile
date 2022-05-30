SHELL := /bin/bash

all: venv
.PHONY: all

run: all
	(source venv/bin/activate || true) && python -m rover_control.rover_control
.PHONY: run

freeze:
	(source venv/bin/activate || true) && pip freeze --local | grep -v "pkg-resources" > requirements.txt
.PHONY: freeze

venv:
	virtualenv -p python3 venv
	source venv/bin/activate && pip install -r requirements.txt
	touch venv
