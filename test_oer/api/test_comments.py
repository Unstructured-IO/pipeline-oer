import os
from pathlib import Path
import pytest
import json
from fastapi.testclient import TestClient

from prepline_oer.api.comments import app, structure_oer
from unstructured_api_tools.pipelines.api_conventions import get_pipeline_path

DIRECTORY = Path(__file__).absolute().parent

SAMPLE_DOCS_DIRECTORY = os.path.join(DIRECTORY, "..", "..", "sample-docs")


COMMENTS_ROUTE = get_pipeline_path("comments", pipeline_family="oer", semver="0.0.1")


@pytest.fixture
def fake_structured_oer():
    return {
        "duty_description": "Personnel and Administration Officer (S1) for a training battalion in the U.S. Army reserve. Principal staff assistant to the battalion commander. Exercise staff supervisor in matters pertaining to strength management, personnel qualifications and evaluations, personnel assignment, clearance, recruiting, retention, and battalion administration. Responsible for the overall supervision of the battalion Personnel Administration Center (PAC) and its activities. Serves as commander of Headquarters and Headquarters Detachment. Additional duties include; Battalion Safety Officer, Equal Opportunity Officer, Records Management Officer, and Retention Officer.",  # noqa: E501
        "rater_comments": "1LT X performed flawlessly in the execution of an overseas detention and area security mission at Guantanamo Bay, Cuba. Exceptional performance during this limited rating period by CPT X.",  # noqa: E501
        "rater_sections": {
            "achieves": "Developed AAR reporting template that standardized information across the battalion and ensured compliance with Army Regulations. She consistently presented appropriate and useful monthly reports on security clearances, weather effects, and threat assessments.",  # noqa: E501
            "develops": "Absolute professional and squared away for duty; current on all applicable skills, knowledge, and mental toughness by engaging in engages in continual self-development. Using his extensive experience, 1LT X works well after normal duty hours, provides coaching, and counseling and mentoring.",  # noqa: E501
            "leads": "1LT X demonstrates the full range of required influence techniques enabling him to speak, lead and motivate every person in his unit. 1LT X works with the Alameda County Sheriff\u2019s office, as well as other outside agencies, in order to build positive relationships established that have enhanced unit training.",  # noqa: E501
            "intellect": "1LT X is able to analyze a situation and introduce new ideas when opportunities exist, approaching challenging circumstances with creativity and intellect. 1LT X is highly proficient in interacting with others, effectively adjusting behaviors when interacting with superiors, peers, and subordinates.",  # noqa: E501
            "presence": "1LT X maintains an excellent fitness level and sets the standard for his Soldiers, with a score of 275 on his last APFT. 1LT X models the composure, outward calm, and control over his emotions that you want to see in a leader during adverse conditions.",  # noqa: E501
            "character": "1LT X\u2019s exceptional command presence and resilience lends itself to consistent mission accomplishment, good order and discipline, and a positive climate. 1LT X\u2019s outstanding attitude and thirst for knowledge exceeds those around him which contributes to his overall exceptional character.",  # noqa: E501
        },
        "senior_rater_comments": {
            "comments": "I currently senior rate Army Officers in this grade. 1LT X is #4 of the 44 Lieutenants I senior rated. 1LT X is an intelligent and creative Officer with the potential to progress in rank as a leader. 1LT X is ready for positions of increased responsibilities; he will excel as a Staff Officer followed by Company Command if given the opportunity. Select for Military Police Captains Career Course and promote to captain when eligible.",  # noqa: E501
            "next_assignment": ["Battalion FDO", " Battalion AS3", " Battalion S4"],
        },
        "intermediate_rater": "1LT X is #2 of the 20 Lieutenants I intermediate rated. He is an asset for the future and will progress further in his military career. Keep assigning him to demanding position and select him for the Military Police Captains Career Course now. Promote ahead of peers to Captain and select him for the next Company Command.",  # noqa: E501
    }


@pytest.mark.parametrize(
    "invalid_pages, exception_message",
    [
        ({}, "Pages length is 0. Expected 2 pages."),
        (
            [{"elements": []}, {"elements": []}],
            "Number of narrative text elements on the first page is 0. Expected at least two.",
        ),
    ],
)
def test_structure_oer_with_invalid_pages(invalid_pages, exception_message):
    with pytest.raises(ValueError) as validation_exception:
        structure_oer(invalid_pages)
    assert str(validation_exception.value) == exception_message


def test_section_narrative_api(fake_structured_oer):
    filename = os.path.join(SAMPLE_DOCS_DIRECTORY, "fake-oer.pdf")
    app.state.limiter.reset()
    client = TestClient(app)
    response = client.post(
        COMMENTS_ROUTE,
        files={
            "files": (
                filename,
                open(filename, "rb"),
            )
        },
    )

    assert response.status_code == 200
    assert json.loads(response.content.decode("utf-8")) == fake_structured_oer


def test_section_narrative_api_with_no_file():
    app.state.limiter.reset()
    client = TestClient(app)
    response = client.post(
        COMMENTS_ROUTE,
    )

    assert response.status_code == 400


def test_section_narrative_api_with_conflict_in_media_type():
    filename = os.path.join(SAMPLE_DOCS_DIRECTORY, "fake-oer.pdf")
    app.state.limiter.reset()
    client = TestClient(app)
    response = client.post(
        COMMENTS_ROUTE,
        headers={"Accept": "application/pdf"},
        files=[
            ("files", (filename, open(filename, "rb"), "application/pdf")),
            ("files", (filename, open(filename, "rb"), "application/pdf")),
        ],
    )

    assert response.status_code == 406


def test_section_narrative_api_with_multiple_files():
    filename = os.path.join(SAMPLE_DOCS_DIRECTORY, "fake-oer.pdf")
    app.state.limiter.reset()
    client = TestClient(app)
    response = client.post(
        COMMENTS_ROUTE,
        headers={"Accept": "multipart/mixed"},
        files=[
            ("files", (filename, open(filename, "rb"), "application/pdf")),
            ("files", (filename, open(filename, "rb"), "application/pdf")),
        ],
    )

    assert response.status_code == 200


def test_section_narrative_api_health_check():
    client = TestClient(app)
    response = client.get("/healthcheck")

    assert response.status_code == 200
