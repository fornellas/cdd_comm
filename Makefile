# TODO test
# TODO flake8
# TODO coverage

SRCS_PATHS = cdd_comm

##
## format
##

.PHONY: format-black
format-black:
	black $(SRCS_PATHS)

.PHONY: format-isort
format-isort: format-black
	isort --profile black $(SRCS_PATHS)

.PHONY: format
format: format-black format-isort

##
## lint
##

# black

.PHONY: black
black:
	black --check $(SRCS_PATHS)

# isort

.PHONY: isort
isort: black
	isort --check-only --profile black $(SRCS_PATHS)

# mypy

.PHONY: mypy
mypy: isort
	mypy ${SRCS_PATHS}

.PHONY: mypy-clean
mypy-clean:
	rm -rf .mypy-cache/

# lint

.PHONY: lint
lint: black isort mypy

##
## clean
##

.PHONY: clean
clean: