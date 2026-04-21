# Invoice Booking Assistant

Small web app for German accountants: upload a PDF invoice, get a pre-filled Datev booking form back with per-field confidence and the prior bookings used as evidence. Review, edit, submit.

## Stack

- **Backend** — FastAPI (Python 3.11) with the OpenAI SDK. Keeps the API key server-side.
- **Frontend** — Vite + React + TypeScript. Plain CSS, no UI framework.
- **LLM** — OpenAI `gpt-5-mini` (default; overridable via `OPENAI_MODEL`). Chosen because:
  - Native PDF input support — one call does extraction *and* reasoning, no separate PDF parser.
  - Strict JSON-schema structured outputs (`response_format: json_schema, strict: true`) give us a typed, validated payload without post-processing hacks.
  - Good cost/quality balance for a well-defined workflow that still needs multimodal extraction, category inference, and confidence calibration.
- **AI shape** — Single structured call, no agent loop. With 39 prior bookings the whole ledger fits comfortably in the prompt, so retrieval/tools would be overhead. If the ledger grew to thousands of rows I'd move to a tool-using agent with `search_prior_bookings` and `get_vendor_history` tools.

## Run it

Prereqs: Python 3.11 (3.12/3.13 also fine), Node 22 (pinned via `.nvmrc`), an OpenAI API key.

```bash
# one-time setup
nvm use                       # reads .nvmrc → Node 22
npm run install:all
cp backend/.env.example backend/.env
# edit backend/.env and set OPENAI_API_KEY

# dev
npm run dev
```

Frontend on http://localhost:5173, backend on http://localhost:8000. Vite proxies `/api/*` to the backend.

## How it works

1. **Upload** — `UploadZone` accepts a PDF (drag-drop or click). `POST /api/suggest-booking` as multipart form data.
2. **Parse + suggest** — backend reads the CSV ledger once at startup (`ledger.py`), then on each request base64-encodes the PDF and sends it to the model alongside the full 39-row ledger and the cost-center lookup. The model returns a JSON-schema-validated response with:
   - extracted invoice metadata, including line items
   - per-field suggestion (Konto, Gegenkonto, Kostenstelle, Buchungstext) each with a `high | medium | low` confidence
   - overall confidence + numeric score + reasoning
   - the subset of prior bookings it actually cited as evidence
3. **Review** — the frontend pre-fills every field, shows per-field confidence badges, highlights low-confidence fields with a red left-border and a "please confirm" hint, and exposes the model's reasoning + cited prior bookings. Each prior-booking row has a **use this** button to copy its values into the form.
4. **Submit** — produces the booking JSON with extracted invoice data, line items, booking fields, `confidence`, `reasoning`, `prior_bookings_used` count, and `user_modified`. The JSON is shown in the UI and also `console.log`'d.

## Confidence UX — the important bit

- Every AI-suggested field carries a visible confidence badge. No silent guessing.
- Low-confidence fields get an "unconfirmed" visual treatment (red left-border + helper text) so the user's eye lands there first.
- Reasoning is one click away, open by default — never buried behind a modal.
- Prior bookings are shown as **evidence**, not just a count. The user can see *why* we suggested what we did and one-click apply a historical row if they prefer.
- New-vendor case: if the model cites zero prior bookings, the evidence panel is replaced by a yellow/red banner telling the user to verify Konto/Kostenstelle manually.

## Project layout

```
backend/
  app/
    main.py          FastAPI routes, CORS
    config.py        env + paths
    ledger.py        CSV loader + cost-center lookup
    prompts.py       system prompt + user prompt + JSON schema
    suggest.py       OpenAI call, schema-validated parsing
    schemas.py       Pydantic models (response validation)
  data/buchungsstapel.csv
  requirements.txt
  .env.example
frontend/
  src/
    App.tsx                         page orchestration
    api.ts                          fetch wrapper
    types.ts                        TS mirrors of backend schemas
    components/
      UploadZone.tsx                drag-drop + file picker
      BookingForm.tsx               pre-filled editable form, tracks user_modified
      ConfidenceBadge.tsx           green/amber/red badge
      PriorBookingsPanel.tsx        evidence table with one-click "use this"
      SubmitResult.tsx              final JSON display
    App.css
  vite.config.ts                    proxy /api → localhost:8000
```

## CSV format note

The assignment PDF describes the Buchungsstapel as delimiter `;` with decimal comma. The actual attached file is comma-delimited with decimal points (e.g. `595.00`). The loader parses what's actually in the file.

## Tradeoffs given the 4–6h budget

- **No unit tests.** Time went into the confidence UX and prompt shape. The whole pipeline is small enough to verify end-to-end by uploading the 5 test PDFs.
- **No OCR fallback** for scanned image-only PDFs. Modern OpenAI models handle most real invoices; if a PDF is pure image and the model fails, the form still opens with blanks — user can fill it manually.
- **No auth / persistence.** Single-user local tool.
- **Full SKR03 field support is out of scope** — I stick to the four booking fields the assignment calls out: Konto, Gegenkonto, Kostenstelle, and Buchungstext.

## Verifying the five test scenarios

Upload each PDF and check:

| # | Vendor | Expected UX |
|---|--------|-------------|
| 01 | Slack GmbH 595 € | `high` confidence, prior bookings cited, all fields green |
| 02 | AWS EMEA SARL 401.30 € | `medium` confidence, reasoning mentions amount-delta vs prior AWS bookings |
| 03 | Steuerberater Müller 2 380 € | `medium` confidence, Buchungstext left generic, reasoning notes description varies |
| 04 | Google Workspace 714 € | `medium` confidence, Konto 4980 / KST 1100 inferred from SaaS pattern |
| 05 | Architekturbüro Kern 8 925 € | `low` confidence, evidence panel shows warning, user asked to confirm Konto |
