<h3 align="center">
  <img src="img/unstructured_logo.png" height="200">
</h3>

<h3 align="center">
  <p>Pre-Processing Pipeline for OERs</p>
</h3>


This repo implements a document pre-processing pipeline for Army Officer Evaluation Reports (OERs).
The pipeline assumes the OERs are in PDF format and include both pages.
The API is hosted at `https://api.unstructured.io`.

## Getting Started

To view the most common `Makefile` targets, run `make`. The `Makefile` targets include several
options for installing and/or running the pipeline. The PDF parsing capabilities rely on the
`poppler` package. Before installing the package, run `brew install poppler` on a Mac or
`sudo apt-get install poppler-utils` on Debian to install the `poppler` dependencies.

To install all of the dependencies for the pipeline, run `make install`. The pipeline is intended
to be run from the base directory of this repo. If you want to run the pipeline from another
directory, ensure the base directory of the repo is added to your Python path. You can do that
by running `export PYTHONPATH=${PWD}:${PYTHONPATH}` from this directory.

To build the Docker container, run `make docker-build`. After that, there are two
`docker-compose` files for local usage, one for notebooks and one for the API.
To run the notebooks with `docker-compose`, use `make run-notebooks-local`.
You can stop the notebook container with `stop-notebooks-local`. You can view the notebooks
at `http://127.0.0.1:8888`.

To run the API locally, use `make start-app-local`.
You can stop the API with `make stop-app-local`.
If you are an API developer, use `make run-app-dev` instead of `make start-app-local` to
start the API with hot reloading.
The API will run at `http:/127.0.0.1:5000`.
You can view the swagger documentation at `http://127.0.0.1/docs`.

### Generating Python files from the pipeline notebooks

You can generate the FastAPI APIs from your pipeline notebooks by running `make generate-api`.

## Security Policy

See our [security policy](https://github.com/Unstructured-IO/pipeline-oer/security/policy) for
information on how to report security vulnerabilities.

## Learn more

| Section | Description |
|-|-|
| [Company Website](https://unstructured.io) | Unstructured.io product and company info |
| [Fillable OER Form](https://armypubs.army.mil/pub/eforms/DR_a/pdf/ARN17085_A67_10_1_FINAL.pdf) | Blank OER from Army pubs that you can fill in. |
| [OER Narrative Guide](https://juniorofficer.army.mil/oer-company-grade-narrative-guide-and-examples/) | Example OER narratives to use for training data. |
