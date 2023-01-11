#####################################################################
# THIS FILE IS AUTOMATICALLY GENERATED BY UNSTRUCTURED API TOOLS.
# DO NOT MODIFY DIRECTLY
#####################################################################

import os
from typing import List, Union
from fastapi import status, FastAPI, File, Form, Request, UploadFile, APIRouter
from slowapi.errors import RateLimitExceeded
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from fastapi.responses import PlainTextResponse
import json
from fastapi.responses import StreamingResponse
from starlette.types import Send
from base64 import b64encode
from typing import Optional, Mapping, Iterator, Tuple
import secrets
from unstructured_inference.inference.layout import (
    process_data_with_model,
    process_file_with_model,
)
import re
from unstructured.cleaners.core import clean_prefix, clean_extra_whitespace
from unstructured.cleaners.core import clean_postfix
from unstructured.cleaners.extract import extract_text_after, extract_text_before
from unstructured.cleaners.core import replace_unicode_quotes


limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
router = APIRouter()

RATE_LIMIT = os.environ.get("PIPELINE_API_RATE_LIMIT", "1/second")


# pipeline-api


def partition_oer(filename="", file=None, model=None):
    layout = (
        process_file_with_model(filename, model)
        if file is None
        else process_data_with_model(file, model)
    )

    pages = []
    for page in layout.pages:
        pages.append({"elements": [el.to_dict() for el in page.elements]})
    return {"pages": pages}


BLOCK_TITLE_PATTTERN = (
    r"c. (SIGNIFICANT DUTIES AND RESPONSIBILITIES|COMMENTS ON POTENTIAL):?"
)


SENIOR_RATER_PREFIX = (
    r"PART VI - SENIOR RATER POTENTIAL COMPARED WITH OFFICERS SENIOR RATED IN SAME GRADE "
    r"\(OVERPRINTED BY DA\) MOST QUALIFIED "
    r"\(limited to 49%\) HIGHLY QUALIFIED QUALIFIED NOT QUALIFIED b. "
)

NEXT_ASSIGNMENT_PREFIX = (
    "d. List 3 future SUCCESSIVE assignments for which this Officer is best suited: "
)


def get_senior_rater_comments(pages):
    for element in pages[1]["elements"]:
        if re.search(SENIOR_RATER_PREFIX, element["text"]):
            raw_comments = clean_prefix(element["text"], SENIOR_RATER_PREFIX)

            sr_rater_comments = extract_text_before(
                raw_comments, NEXT_ASSIGNMENT_PREFIX
            )
            sr_rater_comments = clean_postfix(sr_rater_comments, BLOCK_TITLE_PATTTERN)

            next_assigments = extract_text_after(raw_comments, NEXT_ASSIGNMENT_PREFIX)

            return {
                "comments": sr_rater_comments,
                "next_assignment": next_assigments.split(";"),
            }

    return dict()


DESCRIPTIONS = {
    "character": "Adherence to Army Values, Empathy, and Warrior Ethos/Service Ethos"
    " and Discipline. Fully supports SHARP, EO, and EEO.",
    "presence": "Military and Professional Bearing, Fitness, Confident, Resilient",
    "intellect": "Mental Agility, Sound Judgment, Innovation, Interpersonal Tact, Expertise",
    "leads": "Leads Others, Builds Trust, Extends Influence beyond the Chain of"
    " Command, Leads by Example, Communicates",
    "develops": "Creates a positive command/workplace environment/Fosters Esprit de"
    " Corps, Prepares Self, Develops Others, Stewards the Profession",
    "achieves": "Gets Results",
}

SECTION_PATTERN = r"c. [1-6]\) ({0}) :".format("|".join(list(DESCRIPTIONS.keys())))

DESCRIPTION_PATTERN = r"\(({0})\)".format("|".join(list(DESCRIPTIONS.values())))


def get_rater_sections(pages):
    """Extracts the Character, Presence, Intellect, Leads, Develops, and Achieves blocks
    from the rater comments and converts them to a dictionary."""
    rater_sections = dict()
    for element in pages[1]["elements"]:
        if re.search(SECTION_PATTERN, element["text"], flags=re.IGNORECASE):
            section_split = re.split(
                SECTION_PATTERN, element["text"], flags=re.IGNORECASE
            )
            for chunk in section_split:
                for key, description in DESCRIPTIONS.items():
                    if description in chunk:
                        comments = clean_postfix(chunk.strip(), DESCRIPTION_PATTERN)
                        rater_sections[key] = replace_unicode_quotes(comments)
    return rater_sections


def structure_oer(pages):
    """Creates a dictionary with the extracted elements of the OER.
    Input is a list of dictionaries,
    each dictionary contains raw information of a page as extracted from PDF parsing.
    Output is a dictionary that includes structured extracted information from the OER.
    """
    if len(pages) < 2:
        raise ValueError(f"Pages length is {len(pages)}. " "Expected 2 pages.")

    structured_oer = dict()

    first_page = [
        element for element in pages[0]["elements"] if element["type"] == "Text"
    ]
    if len(first_page) < 2:
        raise ValueError(
            f"Number of narrative text elements on the "
            f"first page is {len(first_page)}. "
            "Expected at least two."
        )

    duty_description = first_page[0]["text"]
    duty_description = clean_prefix(duty_description, BLOCK_TITLE_PATTTERN)
    structured_oer["duty_description"] = clean_extra_whitespace(duty_description)
    structured_oer["rater"] = {
        "comments": first_page[-1]["text"],
        "sections": get_rater_sections(pages),
    }
    structured_oer["senior_rater"] = get_senior_rater_comments(pages)

    second_page = [
        element for element in pages[1]["elements"] if element["type"] == "Text"
    ]
    structured_oer["intermediate_rater"] = {"comments": second_page[-2]["text"]}

    return structured_oer


box_centers = [
    {
        (56.905, 360.375): ("referred", "Referred"),
        (132.379, 360.375): ("comments", "Yes, comments are attached"),
        (244.392, 360.375): ("comments", "No"),
        (153.943, 382.075): ("supplementary_review", "Yes"),
        (189.284, 382.075): ("supplementary_review", "No"),
        (367.786, 674.25): ("completed_form_received", "Yes"),
        (397.736, 674.25): ("completed_form_received", "No"),
        (80.266, 697.5): ("performance", "EXCELS"),
        (177.304, 697.5): ("performance", "PROFICIENT"),
        (274.342, 697.5): ("performance", "CAPABLE"),
        (371.979, 697.5): ("performance", "UNSATISFACTORY"),
    },
    {
        (46.123, 577.375): ("potential", "MOST QUALIFIED"),
        (46.123, 609.15): ("potential", "HIGHLY QUALIFIED"),
        (46.123, 642.475): ("potential", "QUALIFIED"),
        (46.123, 674.25): ("potential", "NOT QUALIFIED"),
    },
]


def point_in_box(point, box):
    x1, y1 = box[0]
    x2, y2 = box[2]
    x, y = point
    return (x1 <= x <= x2) and (y1 <= y <= y2)


def structure_checkboxes(checkbox_pages):
    """Creates a dictionary with the information extracted from the checkboxes"""
    if len(checkbox_pages) < 2:
        raise ValueError(f"Pages length is {len(checkbox_pages)}. " "Expected 2 pages.")
    checkbox_indicator = dict()
    for page, centers in zip(checkbox_pages, box_centers):
        for box in page["elements"]:
            for center, (category, text) in centers.items():
                if point_in_box(center, box["coordinates"]):
                    if category not in checkbox_indicator:
                        checkbox_indicator[category] = {}
                    checkbox_indicator[category][text] = box["type"] == "Checked"

    structured_checkboxes = dict()
    for category, boxes in checkbox_indicator.items():
        if category != "referred":
            for text, checked in boxes.items():
                if checked:
                    if category in structured_checkboxes:
                        del structured_checkboxes[category]
                        break
                    structured_checkboxes[category] = text
    structured_checkboxes["referred"] = (
        "Yes" if checkbox_indicator["referred"]["Referred"] else "No"
    )

    return structured_checkboxes


def pipeline_api(
    file,
    file_content_type=None,
    filename=None,
):
    pages = partition_oer(file=file)["pages"]
    narrative = structure_oer(pages)

    file.seek(0)
    checkbox_pages = partition_oer(file=file, model="checkbox")["pages"]

    checkbox = structure_checkboxes(checkbox_pages)
    for key in ["referred", "comments", "supplementary_review", "performance"]:
        if "rater" in narrative and key in checkbox:
            narrative["rater"][key] = checkbox[key]
    if "senior_rater" in narrative and "potential" in checkbox:
        narrative["senior_rater"]["potential"] = checkbox["potential"]

    return narrative


class MultipartMixedResponse(StreamingResponse):
    CRLF = b"\r\n"

    def __init__(self, *args, content_type: str = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.content_type = content_type

    def init_headers(self, headers: Optional[Mapping[str, str]] = None) -> None:
        super().init_headers(headers)
        self.boundary_value = secrets.token_hex(16)
        content_type = f'multipart/mixed; boundary="{self.boundary_value}"'
        self.raw_headers.append((b"content-type", content_type.encode("latin-1")))

    @property
    def boundary(self):
        return b"--" + self.boundary_value.encode()

    def _build_part_headers(self, headers: dict) -> bytes:
        header_bytes = b""
        for header, value in headers.items():
            header_bytes += f"{header}: {value}".encode() + self.CRLF
        return header_bytes

    def build_part(self, chunk: bytes) -> bytes:
        part = self.boundary + self.CRLF
        part_headers = {
            "Content-Length": len(chunk),
            "Content-Transfer-Encoding": "base64",
        }
        if self.content_type is not None:
            part_headers["Content-Type"] = self.content_type
        part += self._build_part_headers(part_headers)
        part += self.CRLF + chunk + self.CRLF
        return part

    async def stream_response(self, send: Send) -> None:
        await send(
            {
                "type": "http.response.start",
                "status": self.status_code,
                "headers": self.raw_headers,
            }
        )
        async for chunk in self.body_iterator:
            if not isinstance(chunk, bytes):
                chunk = chunk.encode(self.charset)
                chunk = b64encode(chunk)
            await send(
                {
                    "type": "http.response.body",
                    "body": self.build_part(chunk),
                    "more_body": True,
                }
            )

        await send({"type": "http.response.body", "body": b"", "more_body": False})


@router.post("/oer/v0.0.1/raters")
@limiter.limit(RATE_LIMIT)
async def pipeline_1(
    request: Request,
    files: Union[List[UploadFile], None] = File(default=None),
):
    content_type = request.headers.get("Accept")

    if isinstance(files, list) and len(files):
        if len(files) > 1:
            if content_type and content_type not in ["*/*", "multipart/mixed"]:
                return PlainTextResponse(
                    content=(
                        f"Conflict in media type {content_type}"
                        ' with response type "multipart/mixed".\n'
                    ),
                    status_code=status.HTTP_406_NOT_ACCEPTABLE,
                )

            def response_generator():
                for file in files:

                    _file = file.file

                    response = pipeline_api(
                        _file,
                        filename=file.filename,
                        file_content_type=file.content_type,
                    )
                    if type(response) not in [str, bytes]:
                        response = json.dumps(response)
                    yield response

            return MultipartMixedResponse(
                response_generator(),
            )
        else:

            file = files[0]
            _file = file.file

            response = pipeline_api(
                _file,
                filename=file.filename,
                file_content_type=file.content_type,
            )

            return response

    else:
        return PlainTextResponse(
            content='Request parameter "files" is required.\n',
            status_code=status.HTTP_400_BAD_REQUEST,
        )


@app.get("/healthcheck", status_code=status.HTTP_200_OK)
async def healthcheck(request: Request):
    return {"healthcheck": "HEALTHCHECK STATUS: EVERYTHING OK!"}


app.include_router(router)
