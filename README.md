<h3 align="center">
  <img src="img/unstructured_logo.png" height="200">
</h3>

<h3 align="center">
  <p>Pre-Processing Pipeline for OERs</p>
</h3>


This repo implements a document pre-processing pipeline for Army Officer Evaluation Reports (OERs).
The pipeline assumes the OERs are in PDF format and include both pages.
The API is hosted at `https://api.unstructured.io`.

## Developer Quick Start

* Using `pyenv` to manage virtualenv's is recommended
	* Mac install instructions. See [here](https://github.com/Unstructured-IO/community#mac--homebrew) for more detailed instructions.
		* `brew install pyenv-virtualenv`
	  * `pyenv install 3.8.13`
  * Linux instructions are available [here](https://github.com/Unstructured-IO/community#linux).

	Create a virtualenv to work in and activate it, e.g. for one named `sec-filings`:

	`pyenv  virtualenv 3.8.13 sec-filings` <br />
	`pyenv activate sec-filings`

* Run `make install`
* Start a local jupyter notebook server with `make run-jupyter` <br />
	**OR** <br />
	just start the fast-API locally with `make run-web-app`

#### Extracting Structured Text from an OER PDF document
After API starts, you can extract the elements of OER files with the command:
```
curl -X 'POST' \
  'http://localhost:8000/oer/v0.0.1/comments' \
  -F 'files=@<your_oer_pdf_file>' \
  | jq -C . | less -R
```

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
