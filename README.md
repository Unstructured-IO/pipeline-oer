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
	  * `pyenv install 3.8.15`
  * Linux instructions are available [here](https://github.com/Unstructured-IO/community#linux).

  * Create a virtualenv to work in and activate it, e.g. for one named `oer`:

	`pyenv  virtualenv 3.8.15 oer` <br />
	`pyenv activate oer`

* Run `make install`
* Start a local jupyter notebook server with `make run-jupyter` <br />
	**OR** <br />
	just start the fast-API locally with `make run-web-app`
	
## Quick Tour

You can run this [Colab notebook](https://colab.research.google.com/drive/1sedVOvsg0PRV74C1TIoFxSFfrPoiH005) to see how [pipeline-raters.ipynb](/pipeline-notebooks/pipeline-raters.ipynb) extracts the the elements of OER files and defines an API.


## Extracting Structured Text from an OER PDF document
After API starts, you can extract the elements of OER files with the command:
```
curl -X 'POST' \
  'http://localhost:8000/oer/v0.0.1/raters' \
  -F 'files=@<your_oer_pdf_file>' \
  | jq -C . | less -R
```

Using the example fake OER in the `sample-docs` folder, you can run:

```
curl -X 'POST' \
  'http://localhost:8000/oer/v0.0.1/raters' \
    -F 'files=@fake-oer.pdf' | jq -C | less -R
```

and get the following JSON as the output:

```json
{
  "duty_description": "Personnel and Administration Officer (S1) for a training battalion in the U.S. Army reserve. Principal staff assistant to the battalion commander. Exercise staff supervisor in matters pertaining to strength management, personnel qualifications and evaluations, personnel assignment, clearance, recruiting, retention, and battalion administration. Responsible for the overall supervision of the battalion Personnel Administration Center (PAC) and its activities. Serves as commander of Headquarters and Headquarters Detachment. Additional duties include; Battalion Safety Officer, Equal Opportunity Officer, Records Management Officer, and Retention Officer.",
  "rater": {
    "comments": "1LT X performed flawlessly in the execution of an overseas detention and area security mission at Guantanamo Bay, Cuba. Exceptional performance during this limited rating period by CPT X.",
    "sections": {
      "achieves": "Developed AAR reporting template that standardized information across the battalion and ensured compliance with Army Regulations. She consistently presented appropriate and useful monthly reports on security clearances, weather effects, and threat assessments.",
      "develops": "Absolute professional and squared away for duty; current on all applicable skills, knowledge, and mental toughness by engaging in engages in continual self-development. Using his extensive experience, 1LT X works well after normal duty hours, provides coaching, and counseling and mentoring.",
      "leads": "1LT X demonstrates the full range of required influence techniques enabling him to speak, lead and motivate every person in his unit. 1LT X works with the Alameda County Sheriff’s office, as well as other outside agencies, in order to build positive relationships established that have enhanced unit training.",
      "intellect": "1LT X is able to analyze a situation and introduce new ideas when opportunities exist, approaching challenging circumstances with creativity and intellect. 1LT X is highly proficient in interacting with others, effectively adjusting behaviors when interacting with superiors, peers, and subordinates.",
      "presence": "1LT X maintains an excellent fitness level and sets the standard for his Soldiers, with a score of 275 on his last APFT. 1LT X models the composure, outward calm, and control over his emotions that you want to see in a leader during adverse conditions.",
      "character": "1LT X’s exceptional command presence and resilience lends itself to consistent mission accomplishment, good order and discipline, and a positive climate. 1LT X’s outstanding attitude and thirst for knowledge exceeds those around him which contributes to his overall exceptional character."
    },
    "referred": "No",
    "performance": "PROFICIENT",
    "name": "RAYMOND, BRIAN",
    "position": "EXECUTIVE OFFICER"
  },
  "senior_rater": {
    "comments": "I currently senior rate Army Officers in this grade. 1LT X is #4 of the 44 Lieutenants I senior rated. 1LT X is an intelligent and creative Officer with the potential to progress in rank as a leader. 1LT X is ready for positions of increased responsibilities; he will excel as a Staff Officer followed by Company Command if given the opportunity. Select for Military Police Captains Career Course and promote to captain when eligible.",
    "next_assignment": [
      "Battalion FDO",
      " Battalion AS3",
      " Battalion S4"
    ],
    "potential": "HIGHLY QUALIFIED",
    "name": "BERTL, ALAN",
    "position": "BATTALION COMMANDER"
  },
  "intermediate_rater": {
    "comments": "1LT X is #2 of the 20 Lieutenants I intermediate rated. He is an asset for the future and will progress further in his military career. Keep assigning him to demanding position and select him for the Military Police Captains Career Course now. Promote ahead of peers to Captain and select him for the next Company Command.",
    "name": "WOLFE, CRAG",
    "position": ""
  },
  "rated_name": "ROBINSON, MATTHEW W",
  "rated_position": ""
}
```

You can also run the extraction code with Python directly using the following commands
from the `pipeline-oer` directory:

```python
from prepline_oer.api.raters import pipeline_api

filename = "sample-docs/fake-oer.pdf"

with open(filename, "rb") as f:
    pipeline_api(file=f, filename=filename)
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
