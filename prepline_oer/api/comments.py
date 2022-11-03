#####################################################################
# THIS FILE IS AUTOMATICALLY GENERATED BY UNSTRUCTURED API TOOLS.
# DO NOT MODIFY DIRECTLY
#####################################################################

import os
from typing import List, Union

from fastapi import status, FastAPI, File, Form, Request, UploadFile
from slowapi.errors import RateLimitExceeded
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from fastapi.responses import PlainTextResponse

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

RATE_LIMIT = os.environ.get("PIPELINE_API_RATE_LIMIT", "1/second")

# pipeline-api
import requests


def partition_oer(filename, include_elems=["Text", "Title"]):
    response = requests.post(
        "https://dev.ml.unstructured.io/layout/pdf",
        files={
            "file": (filename, open(filename, "rb")),
        },
        data={"include_elems": include_elems},
    )
    # NOTE(yuming): return the result from post request as a dictionary
    partition_result = json.loads(response.content.decode("utf-8"))
    return partition_result


import re


BLOCK_TITLE_RE = re.compile(
    r"c. (SIGNIFICANT DUTIES AND RESPONSIBILITIES" r"|COMMENTS ON POTENTIAL)"
)


def clean_block_titles(narrative: str) -> str:
    """Cleans the name of the block from the extracted narrative text"""
    return BLOCK_TITLE_RE.sub("", narrative).strip()


COMMENT_BLOCKS = [
    "character",
    "presence",
    "intellect",
    "leads",
    "develops",
    "achieves",
]


def structure_oer(pages):
    """Creates a dictionary with the extracted elements of the OER"""
    if len(pages) < 2:
        raise ValueError(f"Pages length is {len(pages)}). " "Expected 2 pages.")

    structured_oer = dict()

    first_page = pages[0]["elements"]
    if len(first_page) < 2:
        raise ValueError(
            f"Number of narrative text elements on the "
            f"first page is {len(first_page)}. "
            "Expected at least two."
        )

    duty_description = clean_block_titles(first_page[0]["text"])
    structured_oer["duty_description"] = duty_description
    structured_oer["rater_comments"] = first_page[-1]["text"]

    second_page = pages[1]["elements"]
    num_sections = len(COMMENT_BLOCKS)

    if len(first_page) < 2:
        raise ValueError(
            f"Number of narrative text elements on the "
            f"second page is {len(second_page)}. "
            f"Expected at least {num_sections}."
        )

    for i, section in enumerate(second_page[:num_sections]):
        key = COMMENT_BLOCKS[i]
        structured_oer[key] = section["text"]

    structured_oer["intermediate_rater"] = second_page[-2]["text"]

    return structured_oer


def pipeline_api(file, file_content_type=None, filename=None):
    pages = partition_oer(filename)["pages"]

    return structure_oer(pages)


import json
from fastapi.responses import StreamingResponse
from starlette.types import Send
from base64 import b64encode
from typing import Optional, Mapping, Iterator, Tuple
import secrets


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


@app.post("/oer/v0.0.1/comments")
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
