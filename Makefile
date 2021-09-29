# TODO test
# TODO flake8
# TODO black
# TODO isort
# TODO coverage

SRCS_PATHS = cdd_comm

##
## lint
##

# black

.PHONY: black
black:
	black --check $(SRCS_PATHS)

# mypy

.PHONY: mypy
mypy:
	mypy ${SRCS_PATHS}

.PHONY: mypy-clean
mypy-clean:
	rm -rf .mypy-cache/

# lint

.PHONY: lint
lint: black mypy

##
## format
##

.PHONY: format-black
format-black:
	black $(SRCS_PATHS)

.PHONY: format
format: format-black

##
## clean
##

.PHONY: clean
clean: