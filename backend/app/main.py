from __future__ import annotations

import logging

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from . import config
from .invoice_parser import extract_invoice
from .ledger import load_ledger
from .schemas import BookingResponse
from .suggest import suggest_booking

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("invoice-booking")

app = FastAPI(title="Invoice Booking Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the ledger once at startup
BOOKINGS = load_ledger(config.CSV_PATH)
log.info("Loaded %d prior bookings from %s", len(BOOKINGS), config.CSV_PATH)


# Health check endpoint
@app.get("/api/health")
def health() -> dict:
    return {"ok": True, "bookings_loaded": len(BOOKINGS), "model": config.OPENAI_MODEL}


# Accept an uploaded PDF and return an AI-suggested Datev booking with evidence.
@app.post("/api/suggest-booking", response_model=BookingResponse)
async def suggest(file: UploadFile = File(...)) -> BookingResponse:
    # Guard against the common cases before we spend tokens on the model call.
    if file.content_type != "application/pdf" and not (file.filename or "").lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF uploads are supported.")

    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    if len(data) > config.MAX_PDF_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"PDF too large (max {config.MAX_PDF_BYTES // (1024 * 1024)} MB).",
        )

    try:
        filename = file.filename or "invoice.pdf"
        invoice = extract_invoice(data, filename)
        print("Extracted invoice data:", invoice)
        return suggest_booking(invoice, BOOKINGS)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception:
        log.exception("Booking suggestion failed")
        raise HTTPException(status_code=500, detail="Failed to generate booking suggestion.")
