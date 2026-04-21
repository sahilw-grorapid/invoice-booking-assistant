# Invoice Booking Assistant

Small web app for German accountants: upload a PDF invoice, get a pre-filled Datev booking form back with per-field confidence and the prior bookings used as evidence. Review, edit, submit.

## Stack

- **Backend** — FastAPI (Python 3.11) with the OpenAI SDK. Keeps the API key server-side.
- **Frontend** — Vite + React + TypeScript. Plain CSS, no UI framework.
- **LLM** — OpenAI `gpt-5-mini` (default; overridable via `OPENAI_MODEL`). Chosen because:
  - Native PDF input support — one call does extraction _and_ reasoning, no separate PDF parser.
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
- Prior bookings are shown as **evidence**, not just a count. The user can see _why_ we suggested what we did and one-click apply a historical row if they prefer.
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

## Some assumptions and tradeoffs

- **Single LLM call vs. agent loop** — I use one structured model call because the assignment timebox is 4–6 hours and the data is tiny. In a production level application, Agent loop would make more sense.
- **Sending the PDF directly to the LLM** — The model handles PDF extraction and booking reasoning in the same request, which avoids a separate parser pipeline. For production, I would add a deterministic extraction layer.
- **Full CSV in every request vs. caching/pre-indexing** — The full Buchungsstapel is only 39 rows, so sending it in the prompt is simpler and transparent. With thousands of rows, I would pre-index vendor/category history and retrieve only relevant rows.
- **No unit tests** — I prioritized end-to-end behavior and UX within the timebox. The five provided sample PDFs act as the main acceptance tests for known recurring, variable, irregular, new-known-category, and new-unknown-category cases.
- **No persistent storage** — The app is a local review tool: it displays/logs the submitted JSON but does not store invoices or bookings.
- **Model choice: `gpt-5-mini`** — It is a good cost/quality fit since I used my personal API Key.
- **English reasoning and explanations** — User-facing reasoning is forced to English for consistency and for my understanding of the English Language in the demo. Extracted invoice text, vendor names, and Datev-style booking text can still preserve the original German wording.
