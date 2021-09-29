# TODO coverage

TESTSLIDE_FORMAT ?= documentation

TERM_BRIGHT := $(shell tput bold)
TERM_NONE := $(shell tput sgr0)

TESTS_SRCS_PATH = tests
SRCS_PATH = $(TESTS_SRCS_PATH) cdd_comm

# Verbose output: make V=1
V?=0
ifeq ($(V),0)
Q := @./util/run_silent_if_successful.py
else
Q :=
endif

test:

##
## format
##

.PHONY: format-black
format-black:
	@printf "${TERM_BRIGHT}BLACK${TERM_NONE}\n"
	$(Q) black $(SRCS_PATH)

.PHONY: format-isort
format-isort: format-black
	@printf "${TERM_BRIGHT}ISORT${TERM_NONE}\n"
	$(Q) isort --profile black $(SRCS_PATH)

.PHONY: format
format: format-black format-isort

##
## lint
##

# black

.PHONY: black
black:
	@printf "${TERM_BRIGHT}BLACK CHECK${TERM_NONE}\n"
	$(Q) black --check $(SRCS_PATH)

# isort

.PHONY: isort
isort: black
	@printf "${TERM_BRIGHT}ISORT CHECK${TERM_NONE}\n"
	$(Q) isort --check-only --profile black $(SRCS_PATH)

# flake8
.PHONY: flake8
flake8: isort
	@printf "${TERM_BRIGHT}FLAKE8${TERM_NONE}\n"
	$(Q) flake8 --select=F,C90 $(SRCS_PATH)

# mypy

.PHONY: mypy
mypy: flake8
	@printf "${TERM_BRIGHT}MYPY${TERM_NONE}\n"
	$(Q) mypy --warn-unused-configs ${SRCS_PATH}

.PHONY: mypy-clean
mypy-clean:
	@printf "${TERM_BRIGHT}MYPY CLEAN${TERM_NONE}\n"
	$(Q) rm -rf .mypy-cache/

# lint

.PHONY: lint
lint: black isort mypy

##
## test
##

.PHONY: testslide
testslide:
	@printf "${TERM_BRIGHT}TESTSLIDE${TERM_NONE}\n"
	$(Q) testslide \
		--format $(TESTSLIDE_FORMAT) \
		--fail-fast \
		--fail-if-focused \
		$(TESTS_SRCS_PATH)/*_testslide.py

.PHONY: test
test: testslide

##
## clean
##

.PHONY: clean
clean: