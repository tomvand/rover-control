SHELL := /bin/bash

TTY_IN ?= /dev/ttyPPRZ0
TTY_OUT ?= /dev/ttyArduino0
TTY_CAM ?= /dev/ttyCAM0

all: venv pprzlink/pprzlink
.PHONY: all

run: all
	source venv/bin/activate && python -m rover_control.rover_control $(TTY_IN) $(TTY_OUT)
.PHONY: run

run-record:
	source venv/bin/activate && python -m uart_record.uart_record $(TTY_CAM)
.PHONY: run

freeze:
	source venv/bin/activate && pip freeze --local | grep -v "pkg-resources" > requirements.txt
.PHONY: freeze

venv:
	virtualenv -p python3 venv
	source venv/bin/activate && pip install -r requirements.txt
	touch venv

pprzlink: pprzlink/messages.xml
	$(MAKE) -C $@/pprzlink MESSAGES_XML=../messages.xml all pymessages
	touch $@
