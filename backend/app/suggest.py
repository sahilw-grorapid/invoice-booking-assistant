from __future__ import annotations

from openai import OpenAI

from . import config
from .ledger import Booking
from .prompts import SYSTEM_PROMPT, build_user_prompt
from .schemas import BookingResponse, BookingSuggestionResponse, InvoiceExtract


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


# Send the extracted invoice + prior bookings to the LLM via the Responses API
# and return a strictly-validated BookingResponse. The invoice data has already
# been extracted by Extend; the model only fills in booking recommendations.
def suggest_booking(invoice: InvoiceExtract, bookings: list[Booking]) -> BookingResponse:
    client = _get_client()

    # The LLM only sees structured invoice data, not the uploaded PDF bytes.
    response = client.responses.parse(
        model=config.OPENAI_MODEL,
        instructions=SYSTEM_PROMPT,
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": build_user_prompt(invoice, bookings)},
                ],
            }
        ],
        # text_format=<Pydantic model> generates a strict JSON schema from the model
        # and parses the response back into a typed instance
        text_format=BookingSuggestionResponse,
    )

    if response.output_parsed is None:
        raise RuntimeError("Model returned no parseable output")
    parsed = response.output_parsed
    return BookingResponse(
        invoice=invoice,
        suggestion=parsed.suggestion,
        confidence=parsed.confidence,
        confidence_score=parsed.confidence_score,
        reasoning=parsed.reasoning,
        prior_bookings_used=parsed.prior_bookings_used,
    )
