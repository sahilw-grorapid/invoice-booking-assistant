from __future__ import annotations

import base64

from openai import OpenAI

from . import config
from .ledger import Booking
from .prompts import SYSTEM_PROMPT, build_user_prompt
from .schemas import BookingResponse


# Lazily-initialised singleton — we only pay the cost of constructing the
# OpenAI client once, and only if someone actually hits the suggestion endpoint.
_client: OpenAI | None = None


# Return a cached OpenAI client and throw error if API key isn't set.
def _get_client() -> OpenAI:
    global _client
    if _client is None:
        if not config.OPENAI_API_KEY:
            raise RuntimeError(
                "OPENAI_API_KEY is not set. Copy backend/.env.example to backend/.env and fill it in."
            )
        _client = OpenAI(api_key=config.OPENAI_API_KEY)
    return _client


# Send the PDF + prior bookings to the LLM via the Responses API and return a
# strictly-validated BookingResponse. The Pydantic model doubles as the JSON schema
# the model must fill in.
def suggest_booking(pdf_bytes: bytes, filename: str, bookings: list[Booking]) -> BookingResponse:
    client = _get_client()
    # OpenAI's file input wants the PDF as a base64 data URL, not raw bytes.
    pdf_b64 = base64.standard_b64encode(pdf_bytes).decode("ascii")

    # One multimodal call does both: extract fields from the PDF and pick the booking
    # based on the prior-bookings table we put in the text part of the user message.
    response = client.responses.parse(
        model=config.OPENAI_MODEL,
        instructions=SYSTEM_PROMPT,
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_file",
                        "filename": filename or "invoice.pdf",
                        "file_data": f"data:application/pdf;base64,{pdf_b64}",
                    },
                    {"type": "input_text", "text": build_user_prompt(bookings)},
                ],
            }
        ],
        # text_format=<Pydantic model> generates a strict JSON schema from the model
        # and parses the response back into a typed instance
        text_format=BookingResponse,
    )

    if response.output_parsed is None:
        raise RuntimeError("Model returned no parseable output")
    print(f"LLM response parsed successfully: {response.output_parsed}")
    return response.output_parsed
