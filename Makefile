# TODO test
# TODO flake8
# TODO black
# TODO isort
# TODO coverage

SRCS_PATHS = cdd_comm

.PHONY: mypy
mypy:
	mypy ${SRCS_PATHS}

.PHONY: mypy-clean
mypy-clean:
	rm -rf .mypy-cache/

.PHONY: clean
clean: