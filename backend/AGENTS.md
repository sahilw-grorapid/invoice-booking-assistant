# Extend AI Platform — AGENTS.md

> Context file for AI coding assistants building on the [Extend](https://docs.extend.ai) document processing platform.

## What is Extend?

Extend is a platform for building, evaluating, and deploying AI-powered document processing. It provides APIs and SDKs for:

- **Extraction** — Pull structured data from documents using a JSON Schema
- **Classification** — Categorize documents by type
- **Splitting** — Divide multi-page documents into sections
- **Parsing** — Convert documents into clean, structured text (markdown, etc.)
- **Editing** — Detect and fill PDF form fields
- **Workflows** — Orchestrate multiple processors into pipelines with conditionals, human review, webhooks, and more

Full documentation: https://docs.extend.ai
Searchable docs index: https://docs.extend.ai/llms.txt

---

## Authentication

All API requests require Bearer token authentication and an API version header. **If using an SDK, authentication and versioning are handled automatically — the details below apply to raw HTTP requests only.**

```bash
curl -X POST "https://api.extend.ai/extract" \
  -H "Authorization: Bearer sk_YOUR_API_KEY" \
  -H "x-extend-api-version: 2026-02-09" \
  -H "Content-Type: application/json" \
  -d '{ ... }'
```

| Header | Value | Required |
|--------|-------|----------|
| `Authorization` | `Bearer sk_...` | Yes |
| `x-extend-api-version` | `2026-02-09` (latest) | Yes |
| `Content-Type` | `application/json` | For POST/PUT |

Get your API key from the [Extend dashboard](https://app.extend.ai) under Developer Settings.

**Omitting `x-extend-api-version` on raw HTTP requests returns an error.** SDKs set this automatically.

---

## API Versions

The API is versioned by date via the `x-extend-api-version` header. The latest version is `2026-02-09`. SDKs target the correct version automatically when kept up to date.

| Version | Status | Notes |
|---------|--------|-------|
| `2026-02-09` | **Current** | Resource-based endpoints, typed IDs, sync support, simplified responses |
| `2025-04-21` | Stable | Granular processor control |
| `2024-12-23` | Legacy | Separate EXCEL handling |
| `2024-07-30` | Legacy | Webhook subscriptions, processor management |

**If you are on an older version**, see the [migration guide](https://docs.extend.ai/developers/migrations/2026-02-09/overview) for breaking changes in `2026-02-09`. Key changes:

- **Dedicated endpoints** per resource type (`/extract`, `/classify`, `/split`) replace the generic `/processor_runs` endpoint
- **New ID prefixes**: extractors use `ex_`, extract runs use `exr_`, classifiers use `cl_`, splitters use `sp_`
- **Synchronous processing** support on all endpoints (new `/extract`, `/classify`, `/split` sync endpoints)
- **Simplified responses**: single objects no longer wrapped in containers; list responses standardized to `{ "object": "list", "data": [...] }`
- **Inline configuration**: pass extractor/classifier/splitter config inline without pre-creating a resource — useful for managing schemas entirely in code
- **SDK polling helpers**: `createAndPoll` / `create_and_poll` methods with exponential backoff built into updated SDKs

**Migration path**: Update your SDK to the latest version (automatically targets `2026-02-09`), then migrate endpoint-by-endpoint. The old `/processor_runs` and `/processors` endpoints still work on older API versions but are now under Legacy in the docs.

Docs: https://docs.extend.ai/developers/api-versioning

---

## SDKs

**Official SDKs** are available for TypeScript, Python, and Java.

**TypeScript:**
```bash
npm install extend-ai
```

**Python:**
```bash
pip install extend-ai
```

**Java (Gradle):**
```gradle
dependencies {
  implementation 'ai.extend:extend-java-sdk'
}
```

**Community SDK:**
- **Haskell** — maintained by Mercury Technologies: https://github.com/MercuryTechnologies/extend

All SDKs include polling helpers (`createAndPoll` / `create_and_poll`) for async operations, and webhook signature verification utilities.

Docs: https://docs.extend.ai/developers/sdks

---

## API Endpoints (2026-02-09)

> **Note on SDK method names vs REST paths:** This document describes the REST API. SDK method names follow language conventions and may differ (e.g., REST `POST /extract_runs` maps to Python `client.extract_runs.create()` and TypeScript `client.extractRuns.create()`). Always confirm exact method signatures against the SDK source or docs when writing code.

### Base URL

| Region | URL |
|--------|-----|
| US1 (default) | `https://api.extend.ai` |
| US2 | `https://api.us2.extend.app` |

SDKs accept a `baseUrl` (TypeScript) or `base_url` (Python) parameter to select the region.

### Files

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/files/upload` | Upload a file (multipart form data) |
| GET | `/files/{id}` | Get file metadata + presigned download URL |
| GET | `/files` | List files |
| DELETE | `/files/{id}` | Delete a file |

### Extract

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/extract` | Extract data (sync, 5-min timeout) |
| POST | `/extract_runs` | Extract data (async) |
| GET | `/extract_runs/{id}` | Get extract run status/output |
| GET | `/extract_runs` | List extract runs |
| DELETE | `/extract_runs/{id}` | Delete an extract run |
| POST | `/extract_runs/{id}/cancel` | Cancel an in-progress run |
| POST | `/extractors` | Create an extractor |
| GET | `/extractors/{id}` | Get extractor details |
| POST | `/extractors/{id}` | Update an extractor |
| GET | `/extractors` | List extractors |
| POST | `/extractors/{extractorId}/versions` | Publish a new version |
| GET | `/extractors/{extractorId}/versions/{versionId}` | Get a version |
| GET | `/extractors/{extractorId}/versions` | List versions |

### Classify

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/classify` | Classify a file (sync, 5-min timeout) |
| POST | `/classify_runs` | Classify a file (async) |
| GET | `/classify_runs/{id}` | Get classify run |
| GET | `/classify_runs` | List classify runs |
| DELETE | `/classify_runs/{id}` | Delete a classify run |
| POST | `/classify_runs/{id}/cancel` | Cancel an in-progress run |
| POST | `/classifiers` | Create a classifier |
| GET | `/classifiers/{id}` | Get classifier |
| POST | `/classifiers/{id}` | Update classifier |
| GET | `/classifiers` | List classifiers |
| POST | `/classifiers/{classifierId}/versions` | Publish a new version |
| GET | `/classifiers/{classifierId}/versions/{versionId}` | Get a version |
| GET | `/classifiers/{classifierId}/versions` | List versions |

### Split

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/split` | Split a file (sync, 5-min timeout) |
| POST | `/split_runs` | Split a file (async) |
| GET | `/split_runs/{id}` | Get split run |
| GET | `/split_runs` | List split runs |
| DELETE | `/split_runs/{id}` | Delete a split run |
| POST | `/split_runs/{id}/cancel` | Cancel an in-progress run |
| POST | `/splitters` | Create a splitter |
| GET | `/splitters/{id}` | Get splitter |
| POST | `/splitters/{id}` | Update splitter |
| GET | `/splitters` | List splitters |
| POST | `/splitters/{splitterId}/versions` | Publish a new version |
| GET | `/splitters/{splitterId}/versions/{versionId}` | Get a version |
| GET | `/splitters/{splitterId}/versions` | List versions |

### Parse

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/parse` | Parse a file (sync, 5-min timeout) |
| POST | `/parse_runs` | Parse a file (async) |
| GET | `/parse_runs/{id}` | Get parse run |
| DELETE | `/parse_runs/{id}` | Delete a parse run |

### Edit

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/edit` | Edit a PDF (sync, 5-min timeout) |
| POST | `/edit_runs` | Edit a PDF (async) |
| GET | `/edit_runs/{id}` | Get edit run |
| DELETE | `/edit_runs/{id}` | Delete an edit run |

### Workflows

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/workflow_runs` | Run a workflow |
| POST | `/workflow_runs/batch` | Batch run a workflow |
| GET | `/workflow_runs/{id}` | Get workflow run |
| POST | `/workflow_runs/{id}` | Update workflow run metadata |
| POST | `/workflow_runs/{id}/cancel` | Cancel a workflow run |
| DELETE | `/workflow_runs/{id}` | Delete a workflow run |
| GET | `/workflow_runs` | List workflow runs |
| POST | `/workflows` | Create a workflow |

### Evaluation Sets

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/evaluation_sets` | Create an evaluation set |
| GET | `/evaluation_sets/{id}` | Get an evaluation set |
| GET | `/evaluation_sets` | List evaluation sets |
| POST | `/evaluation_sets/{id}/items` | Create items |
| POST | `/evaluation_sets/{id}/items/bulk` | Bulk create items |
| GET | `/evaluation_sets/{id}/items/{itemId}` | Get an item |
| PATCH | `/evaluation_sets/{id}/items/{itemId}` | Update an item |
| DELETE | `/evaluation_sets/{id}/items/{itemId}` | Delete an item |
| GET | `/evaluation_sets/{id}/items` | List items |
| GET | `/evaluation_sets/{id}/runs/{runId}` | Get an eval run |

---

## Common Patterns

### Extract (sync) — Python

```python
from extend_ai import Extend

client = Extend(token="sk_...")

# Sync extract — blocks until complete (5-min timeout)
result = client.extract(
    file={"url": "https://example.com/invoice.pdf"},
    extractor={"id": "ex_..."},
)
print(result.output)
```

### Extract (async with polling) — Python

```python
result = client.extract_runs.create_and_poll(
    file={"url": "https://example.com/invoice.pdf"},
    extractor={"id": "ex_..."},
)
print(result.status)  # "PROCESSED"
print(result.output)
```

### Extract (sync) — TypeScript

```typescript
import { ExtendClient } from "extend-ai";

const client = new ExtendClient({ token: "sk_..." });

const result = await client.extract({
  file: { url: "https://example.com/invoice.pdf" },
  extractor: { id: "ex_..." },
});
console.log(result.output);
```

### Extract (async with polling) — TypeScript

```typescript
const result = await client.extractRuns.createAndPoll({
  file: { url: "https://example.com/invoice.pdf" },
  extractor: { id: "ex_..." },
});
console.log(result.status); // "PROCESSED"
console.log(result.output);
```

### Typed extraction with Zod — TypeScript

The TypeScript SDK supports inline Zod schemas with full type inference:

```typescript
import { ExtendClient, extendDate, extendCurrency } from "extend-ai";
import { z } from "zod";

const client = new ExtendClient({ token: "sk_..." });

const result = await client.extract({
  file: { url: "https://example.com/invoice.pdf" },
  config: {
    schema: z.object({
      invoice_number: z.string().nullable().describe("The invoice number"),
      invoice_date: extendDate().describe("The invoice date"),
      line_items: z.array(z.object({
        description: z.string().nullable(),
        amount: extendCurrency(),
      })).describe("Line items on the invoice"),
      total: extendCurrency().describe("Total amount due"),
    }),
  },
});

console.log(result.output.value.invoice_number); // string | null
console.log(result.output.value.total.amount);   // number | null
```

### Parse a document — Python

```python
result = client.parse(file={"url": "https://example.com/doc.pdf"})
for chunk in result.output.chunks:
    print(chunk.content)
```

### Parse (async with polling) — Python

```python
result = client.parse_runs.create_and_poll(
    file={"url": "https://example.com/doc.pdf"},
)
for chunk in result.output.chunks:
    print(chunk.content)
```

### Run a workflow — Python

```python
result = client.workflow_runs.create_and_poll(
    file={"url": "https://example.com/doc.pdf"},
    workflow={"id": "workflow_..."},
)
for step_run in result.step_runs or []:
    print(step_run.step.type)
    print(step_run.result)
```

### Run a workflow — TypeScript

```typescript
const result = await client.workflowRuns.createAndPoll({
  file: { url: "https://example.com/doc.pdf" },
  workflow: { id: "workflow_..." },
});

for (const stepRun of result.stepRuns ?? []) {
  console.log(stepRun.step.type);
  console.log(stepRun.result);
}
```

---

## Sync vs Async Processing

All processing endpoints (extract, classify, split, parse, edit) support both sync and async modes. Workflows are async-only.

- **Sync** (`POST /extract` / SDK: `client.extract()`) — Blocks until complete. Has a **5-minute timeout**. Best for testing and small files.
- **Async** (`POST /extract_runs` / SDK: `client.extractRuns.createAndPoll()` or `client.extract_runs.create_and_poll()`) — Returns immediately with a run ID. Poll with `GET /extract_runs/{id}` or use webhooks. No timeout limit.

**Use async for production workloads.** Large documents can exceed the 5-minute sync timeout. SDK `createAndPoll` / `create_and_poll` methods are the recommended approach — they handle polling automatically with built-in backoff.

SDK polling helpers use a hybrid strategy: fast polling for 30 seconds, then gradual backoff up to 30-second intervals.

Terminal statuses: `PROCESSED`, `FAILED`, `CANCELLED` (also `NEEDS_REVIEW`, `REJECTED` for workflows).

Docs: https://docs.extend.ai/developers/async-processing

---

## Extraction Schema (JSON Schema)

Extractors use JSON Schema to define output structure. Key rules:

- **Root must be `"type": "object"`**
- **All primitive fields must be nullable**: use `"type": ["string", "null"]` not `"type": "string"`
- **Objects and arrays cannot be nullable**
- **Max nesting depth**: 5 levels
- **Property names**: letters, numbers, underscores, hyphens only
- Include `"required"` arrays listing every property
- Include `"additionalProperties": false` on all objects

### Supported types

| JSON Schema Type | Notes |
|-----------------|-------|
| `["string", "null"]` | Nullable string |
| `["number", "null"]` | Nullable number |
| `["integer", "null"]` | Nullable integer |
| `["boolean", "null"]` | Nullable boolean |
| `"object"` | Nested object (not nullable) |
| `"array"` | Array of objects or scalars (not nullable) |

### Special Extend types

| Type | Usage | Output format |
|------|-------|---------------|
| `"extend:type": "date"` | Add to string fields | `yyyy-mm-dd` |
| `"extend:type": "currency"` | Object with `amount` + `iso_4217_currency_code` | Structured currency |
| `"extend:type": "signature"` | Object with `printed_name`, `signature_date`, `is_signed`, `title_or_role` | Signature detection |

### Enums

Enums must include `null` and only support string values. Use `"extend:descriptions"` for disambiguation:

```json
{
  "status": {
    "enum": ["active", "inactive", "pending", null],
    "extend:descriptions": ["Currently active", "No longer active", "Awaiting activation"]
  }
}
```

### Field descriptions

Use `"description"` to guide extraction. Use `"extend:name"` for display names without changing output keys.

### Unsupported

`anyOf`, `oneOf`, `allOf`, regex patterns, conditional schemas, `const`.

Docs: https://docs.extend.ai/product/extraction/schema

### Legacy: Fields Array schema

Extractors created before April 2025 may use the legacy "Fields Array" configuration instead of JSON Schema. Key differences:

- **Fields Array** used a `fields` array with `id`, `name`, `type`, `description` per field. Output mixed data and metadata together within each field object.
- **JSON Schema** uses a standard `schema` object. Output cleanly separates `value` (extracted data) from `metadata` (confidence, citations) using path-based keys.

**To migrate**: Open your processor in Studio, click the three-dot menu, select "Migrate to JSON Schema." This creates a new processor with the converted schema while preserving your original.

New extractors should always use JSON Schema. See the [migration guide](https://docs.extend.ai/product/migrating-to-json-schema) for full details.

---

## Webhooks

Webhooks deliver HTTP POST notifications when processing events complete.

### Setup

1. Create an endpoint in the Extend dashboard under Developers > Webhook Endpoints
2. Subscribe to events at global, workflow, or processor scope
3. Choose delivery format: JSON (default) or Signed Download URL (for large payloads)

### Key events

The table below lists common events. For the full list (including edit, lifecycle, and CRUD events for all resource types), see the [webhook events docs](https://docs.extend.ai/product/webhooks/events).

| Event | Fires when |
|-------|-----------|
| `extract_run.processed` | Extraction completes |
| `extract_run.failed` | Extraction fails |
| `classify_run.processed` | Classification completes |
| `classify_run.failed` | Classification fails |
| `split_run.processed` | Splitting completes |
| `split_run.failed` | Splitting fails |
| `parse_run.processed` | Parsing completes |
| `parse_run.failed` | Parsing fails |
| `edit_run.processed` | PDF editing completes |
| `edit_run.failed` | PDF editing fails |
| `workflow_run.completed` | Workflow completes |
| `workflow_run.failed` | Workflow fails |
| `workflow_run.needs_review` | Workflow requires human review |
| `workflow_run.step_run.processed` | Individual workflow step completes |

### Signature verification

Extend signs every webhook with HMAC-SHA256. Use the SDK's built-in verification:

**TypeScript:**
```typescript
const event = client.webhooks.verifyAndParse(body, headers, "wss_...");
```

**Python:**
```python
event = client.webhooks.verify_and_parse(body=body, headers=headers, signing_secret="wss_...")
```

For manual verification:
1. Extract `x-extend-request-timestamp` and `x-extend-request-signature` headers
2. Construct message: `v0:{timestamp}:{body}`
3. HMAC-SHA256 with your signing secret
4. Compare signatures; reject if timestamp > 5 minutes old

Docs: https://docs.extend.ai/product/webhooks/configuration

---

## Workflows

Workflows chain processors into pipelines. Built visually in the Extend Studio, triggered via API.

### Capabilities

- Extraction, classification, splitting steps
- Conditional routing based on extracted values or classification results
- Human review steps (pauses workflow for manual review)
- External data validation (call your API mid-workflow)
- Webhook response steps
- Formula calculations
- Parse step configuration
- Validation rules

### Running a workflow via API

Via SDK, use `client.workflowRuns.createAndPoll()` (TypeScript) or `client.workflow_runs.create_and_poll()` (Python) — see Common Patterns above. Raw HTTP example:

```bash
curl -X POST "https://api.extend.ai/workflow_runs" \
  -H "Authorization: Bearer sk_..." \
  -H "x-extend-api-version: 2026-02-09" \
  -H "Content-Type: application/json" \
  -d '{
    "workflowId": "workflow_...",
    "files": [{"url": "https://...", "fileName": "doc.pdf"}]
  }'
```

### Workflow run statuses

| Status | Meaning |
|--------|---------|
| `PENDING` | Queued, not yet started |
| `PROCESSING` | Currently executing |
| `PROCESSED` | Completed successfully |
| `FAILED` | Failed (check `failureReason`) |
| `NEEDS_REVIEW` | Paused for human review |
| `REJECTED` | Rejected during human review |
| `CANCELLED` | Cancelled via API |

### Retryable failure reasons

These failures are transient and safe to retry automatically:
- `INTERNAL_ERROR` — Unexpected server error
- `DOCUMENT_PROCESSOR_ERROR` — Extraction step failed after retries

Non-retryable:
- `INVALID_WORKFLOW` — Workflow configuration error
- `FAILED_TO_PROCESS_FILE` — File could not be downloaded (check your URL)

Docs: https://docs.extend.ai/product/workflows/create-a-workflow

---

## Error Handling

| Error Code | Description | Retryable |
|------------|-------------|-----------|
| `INVALID_REQUEST` | Bad request body or parameters | No |
| `UNAUTHORIZED` | Missing or invalid API key | No |
| `NOT_FOUND` | Resource doesn't exist | No |
| `RATE_LIMIT_EXCEEDED` | Too many requests — back off and retry | Yes |
| `USAGE_BLOCKED` | Out of credits | No |
| `ENDPOINT_REMOVED` | Deprecated endpoint — check error message for replacement | No |
| `INTERNAL_ERROR` | Server error | Yes |

SDKs raise typed exceptions for these errors (e.g., `RateLimitError`, `UnauthorizedError`). Error responses include a `requestId` — provide this when contacting support.

Docs: https://docs.extend.ai/developers/error-codes

---

## Rate Limits

All rate limits are per-organization. If you receive `429 Too Many Requests`, implement exponential backoff. SDK polling helpers handle backoff automatically; for other SDK calls, add your own retry logic.

Docs: https://docs.extend.ai/product/rate-limits (includes current limits by endpoint)

---

## Evaluation Sets

Evaluation sets let you benchmark processor accuracy against ground truth.

1. Create an eval set linked to an extractor
2. Add items (files + expected outputs)
3. Run the eval set against a processor version
4. Review per-field accuracy metrics

Available via both the Studio UI and the API.

Docs: https://docs.extend.ai/product/evaluation/overview

---

## Key Documentation Links

| Topic | URL |
|-------|-----|
| Getting started | https://docs.extend.ai/product/getting-started |
| Extraction quick start | https://docs.extend.ai/product/extraction/quick-start-5-minutes |
| Parsing quick start | https://docs.extend.ai/product/parsing/parse |
| JSON Schema reference | https://docs.extend.ai/product/extraction/schema |
| Extraction best practices | https://docs.extend.ai/product/extraction/best-practices/overview |
| Async processing | https://docs.extend.ai/developers/async-processing |
| Webhook setup | https://docs.extend.ai/product/webhooks/configuration |
| Webhook events | https://docs.extend.ai/product/webhooks/events |
| Workflow creation | https://docs.extend.ai/product/workflows/create-a-workflow |
| API versioning | https://docs.extend.ai/developers/api-versioning |
| 2026-02-09 migration | https://docs.extend.ai/developers/migrations/2026-02-09/overview |
| JSON Schema migration | https://docs.extend.ai/product/migrating-to-json-schema |
| SDKs | https://docs.extend.ai/developers/sdks |
| Error codes | https://docs.extend.ai/developers/error-codes |
| Rate limits | https://docs.extend.ai/product/rate-limits |
| Supported file types | https://docs.extend.ai/product/supported-file-types |
| Credits | https://docs.extend.ai/product/credits |
| Confidence scores | https://docs.extend.ai/product/extraction/confidence-scores |
| Citations | https://docs.extend.ai/product/extraction/citations |
| API reference (full) | https://docs.extend.ai/developers/api-reference |
| Searchable docs index | https://docs.extend.ai/llms.txt |
