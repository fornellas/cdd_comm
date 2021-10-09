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

DEV?=0
ifeq ($(DEV),0)
TESTSLIDE_OPTS = --fail-if-focused
else
TESTSLIDE_OPTS = --focus --fail-fast
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
	$(Q) mypy --warn-unused-configs --show-error-codes ${SRCS_PATH}

.PHONY: mypy-clean
mypy-clean:
	@printf "${TERM_BRIGHT}MYPY CLEAN${TERM_NONE}\n"
	$(Q) rm -rf .mypy_cache/
clean: mypy-clean

# lint

.PHONY: lint
lint: black isort mypy

##
## test
##

# testslide

.PHONY: testslide
testslide: coverage-erase
	@printf "${TERM_BRIGHT}TESTSLIDE${TERM_NONE}\n"
	${Q} coverage run -m testslide.cli \
		--format $(TESTSLIDE_FORMAT) \
		$(TESTSLIDE_OPTS) \
		$(TESTS_SRCS_PATH)/*_testslide.py

# coverage

.PHONY: coverage-erase
coverage-erase:
	@printf "${TERM_BRIGHT}COVERAGE ERASE\n${TERM_NONE}"
	${Q} coverage erase

.PHONY: coverage-combine
coverage-combine: testslide
	@printf "${TERM_BRIGHT}COVERAGE COMBINE\n${TERM_NONE}"
	${Q} coverage combine

.PHONY: coverage-report
coverage-report: coverage-combine
	@printf "${TERM_BRIGHT}COVERAGE REPORT\n${TERM_NONE}"
	${Q} coverage report

.PHONY: coverage-html
coverage-html: coverage-combine
	@printf "${TERM_BRIGHT}COVERAGE HTML\n${TERM_NONE}"
	${Q} coverage html

.PHONY: coverage-clean
coverage-clean:
	@printf "${TERM_BRIGHT}COVERAGE CLEAN\n${TERM_NONE}"
	${Q} rm -rf htmlcov/ .coverage .coverage.*
clean: coverage-clean

# test

.PHONY: test
test: coverage-report

##
## clean
##

# pycache

.PHONY: pycache-clean
pycache-clean:
	@printf "${TERM_BRIGHT}PYCACHE CLEAN\n${TERM_NONE}"
	$(Q) rm -rf $$(find . -type d -name __pycache__)
clean: pycache-clean

# clean

.PHONY: clean
clean: