# Pydantic models for the backend's response. Also double as the JSON schema
# OpenAI's Responses API enforces — so one source of truth, no hand-written schema.
# Strict-mode compatible: no defaults, `extra="forbid"` on every model.
from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, ConfigDict

Confidence = Literal["high", "medium", "low"]

_strict = ConfigDict(extra="forbid")


# A single suggested field plus how confident the model is in it.
class FieldSuggestion(BaseModel):
    model_config = _strict
    value: str
    confidence: Confidence


class LineItem(BaseModel):
    model_config = _strict
    description: str
    quantity: str
    unit_price_net: float | None
    amount_net: float | None


# Fields the model extracted from the PDF itself (vendor, line items, amounts, dates).
class InvoiceExtract(BaseModel):
    model_config = _strict
    invoice_number: str
    invoice_date: str  # ISO yyyy-mm-dd
    vendor_name: str
    line_items: list[LineItem]
    amount_net: float
    amount_gross: float
    vat_rate: float


# The booking fields the model wants to fill in, each with its own confidence.
class Suggestion(BaseModel):
    model_config = _strict
    konto: FieldSuggestion
    gegenkonto: FieldSuggestion
    kostenstelle: FieldSuggestion
    buchungstext: FieldSuggestion


# A prior booking the model cited as evidence — shown in the UI's evidence panel.
class PriorBookingRef(BaseModel):
    model_config = _strict
    buchungstext: str
    konto: str
    gegenkonto: str
    kostenstelle: str
    amount: float


# Full backend response — what the frontend consumes from /api/suggest-booking.
class BookingResponse(BaseModel):
    model_config = _strict
    invoice: InvoiceExtract
    suggestion: Suggestion
    confidence: Confidence
    confidence_score: float
    reasoning: str
    prior_bookings_used: list[PriorBookingRef]
