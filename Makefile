PIPELINE_FAMILY := oer
PIPELINE_PACKAGE := oer
PACKAGE_NAME := prepline_${PIPELINE_PACKAGE}
PIP_VERSION := 22.1.2

.PHONY: help
help: Makefile
	@sed -n 's/^\(## \)\([a-zA-Z]\)/\2/p' $<


###########
# Install #
###########

## install-base:                installs minimum requirements to run the API
.PHONY: install-base
install-base: install-base-pip-packages install-nltk-models install-detectron2

## install:                     installs all test and dev requirements
.PHONY: install
install: install-base install-test install-dev

.PHONY: install-base-pip-packages
install-base-pip-packages:
	python3 -m pip install pip==${PIP_VERSION}
	pip install -r requirements/base.txt

.PHONY: install-detectron2
install-detectron2: install-pdf
	pip install "detectron2@git+https://github.com/facebookresearch/detectron2.git@v0.6#egg=detectron2"

.PHONY: install-nltk-models
install-nltk-models:
	python -c "import nltk; nltk.download('punkt')"
	python -c "import nltk; nltk.download('averaged_perceptron_tagger')"

.PHONY: install-test
install-test:
	pip install -r requirements/test.txt

.PHONY: install-dev
install-dev:
	pip install -r requirements/dev.txt

.PHONY: install-ci
install-ci: install-base install-test

## pip-compile:                 compiles all base/dev/test requirements
.PHONY: pip-compile
pip-compile:
	pip-compile requirements/base.in
	pip-compile requirements/dev.in
	pip-compile requirements/test.in


#########
# Build #
#########

## docker-build:                builds the docker container for the pipeline
.PHONY: docker-build
docker-build:
	BUILD_TYPE="" PIP_VERSION=${PIP_VERSION} PIPELINE_FAMILY=${PIPELINE_FAMILY} ./scripts/docker-build.sh

## generate-api:                generates the FastAPI python APIs from notebooks
.PHONY: generate-api
generate-api:
	PYTHONPATH=. unstructured_api_tools convert-pipeline-notebooks \
		--input-directory ./pipeline-notebooks \
		--output-directory ./${PACKAGE_NAME}/api

#########
# Local #
########

## run-notebooks-local:         runs the container as a docker compose file
.PHONY: run-notebooks-local
run-notebooks-local:
	docker-compose -p ${PIPELINE_FAMILY} -f docker/docker-compose-notebook.yaml up

## stop-notebooks-local:        stops the container
.PHONY: stop-notebooks-local
stop-notebooks-local:
	docker-compose -p ${PIPELINE_FAMILY} stop

## start-app-local:             runs FastAPI in the container with hot reloading
.PHONY: start-app-local
start-app-local:
	docker-compose -p ${PIPELINE_FAMILY}-api -f docker/docker-compose-api.yaml up

## stop-app-local:              stops the container
.PHONY: stop-app-local
stop-app-local:
	docker-compose -p ${PIPELINE_FAMILY}-api stop

## run-app-dev:                 runs the FastAPI api with hot reloading
.PHONY: run-app-dev
run-app-dev:
	 PYTHONPATH=. uvicorn ${PACKAGE_NAME}.api.section:app --reload

#################
# Test and Lint #
#################

## test:                        runs core tests
.PHONY: test
test:
	PYTHONPATH=. pytest test_${PIPELINE_PACKAGE} --cov=${PACKAGE_NAME} --cov-report term-missing

.PHONY: check-coverage
check-coverage:
	coverage report --fail-under=95

## test-integration:            runs integration tests
.PHONY: test-integration
test-integration:
	PYTHONPATH=. pytest test_${PIPELINE_PACKAGE}_integration

## api-check:                   verifies auto-generated pipeline APIs match the existing ones
.PHONY: api-check
api-check:
	PYTHONPATH=. PACKAGE_NAME=${PACKAGE_NAME} ./scripts/test-doc-pipeline-apis-consistent.sh

## check:                       runs linters (includes tests)
.PHONY: check
check: check-src check-tests

## check-src:                   runs linters (source only, no tests)
.PHONY: check-src
check-src:
	black --line-length 100 ${PACKAGE_NAME} --check --exclude ${PACKAGE_NAME}/api
	flake8 ${PACKAGE_NAME}
	mypy ${PACKAGE_NAME} --ignore-missing-imports --install-types --non-interactive

.PHONY: check-tests
check-tests:
	black --line-length 100 test_${PIPELINE_PACKAGE} --check
	flake8 test_${PIPELINE_PACKAGE}

## tidy:                        run black
.PHONY: tidy
tidy:
	black --line-length 100 ${PACKAGE_NAME}
	black --line-length 100 test_${PIPELINE_PACKAGE}
