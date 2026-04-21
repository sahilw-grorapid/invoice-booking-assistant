import { useMemo, useState } from 'react'
import { suggestBooking } from './api'
import type { BookingResponse, FinalBookingJSON, PriorBookingRef } from './types'
import { UploadZone } from './components/UploadZone'
import { BookingForm, type FormState } from './components/BookingForm'
import { PriorBookingsPanel } from './components/PriorBookingsPanel'
import { ConfidenceBadge } from './components/ConfidenceBadge'
import { SubmitResult } from './components/SubmitResult'
import './App.css'

// Flattens the backend response into a flat form-state object the user can edit.
function initialFormState(r: BookingResponse): FormState {
  return {
    invoice_number: r.invoice.invoice_number,
    invoice_date: r.invoice.invoice_date,
    vendor_name: r.invoice.vendor_name,
    line_items: r.invoice.line_items,
    amount_net: String(r.invoice.amount_net),
    amount_gross: String(r.invoice.amount_gross),
    vat_rate: String(r.invoice.vat_rate),
    gegenkonto: r.suggestion.gegenkonto.value,
    konto: r.suggestion.konto.value,
    kostenstelle: r.suggestion.kostenstelle.value,
    buchungstext: r.suggestion.buchungstext.value,
  }
}

export default function App() {
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [response, setResponse] = useState<BookingResponse | null>(null)
  const [state, setState] = useState<FormState | null>(null)
  const [submitted, setSubmitted] = useState<FinalBookingJSON | null>(null)
  const [reasoningOpen, setReasoningOpen] = useState(true)

  const initial = useMemo(() => (response ? initialFormState(response) : null), [response])

  // Uploads the PDF, clears any prior state, and populates the form with the suggestion.
  const upload = async (file: File) => {
    setBusy(true)
    setError(null)
    setResponse(null)
    setState(null)
    setSubmitted(null)
    try {
      const r = await suggestBooking(file)
      setResponse(r)
      setState(initialFormState(r))
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Something went wrong.')
    } finally {
      setBusy(false)
    }
  }

  const reset = () => {
    setResponse(null)
    setState(null)
    setSubmitted(null)
    setError(null)
  }

  // Copies a cited prior booking's fields into the form — the "use this" button action.
  const applyPrior = (b: PriorBookingRef) => {
    if (!state) return
    setState({
      ...state,
      konto: b.konto,
      gegenkonto: b.gegenkonto,
      kostenstelle: b.kostenstelle,
      buchungstext: b.buchungstext,
    })
  }

  const onSubmit = (final: FinalBookingJSON) => {
    console.log('[invoice-booking] Submitted booking:', final)
    setSubmitted(final)
  }

  return (
    <div className="app">
      <header className="app__header">
        <h1>Invoice Booking Assistant</h1>
        <p className="muted">Upload a PDF invoice — get a Datev booking suggestion with evidence.</p>
      </header>

      {!response && !submitted && <UploadZone onFile={upload} busy={busy} />}
      {error && <div className="error">{error}</div>}

      {response && state && initial && !submitted && (
        <div className="result">
          <div className="result__header">
            <div className="result__confidence">
              <ConfidenceBadge level={response.confidence} />
              <span className="muted">score {response.confidence_score.toFixed(2)}</span>
            </div>
            <button className="link" onClick={reset}>
              Upload a different PDF
            </button>
          </div>

          <div className="panel panel--reasoning">
            <button className="panel__toggle" onClick={() => setReasoningOpen((o) => !o)}>
              {reasoningOpen ? '▾' : '▸'} Why this suggestion?
            </button>
            {reasoningOpen && <p className="reasoning">{response.reasoning}</p>}
          </div>

          <PriorBookingsPanel bookings={response.prior_bookings_used} onApply={applyPrior} />

          <BookingForm
            state={state}
            initial={initial}
            suggestion={response}
            onChange={(patch) => setState({ ...state, ...patch })}
            onSubmit={onSubmit}
          />
        </div>
      )}

      {submitted && <SubmitResult json={submitted} onReset={reset} />}
    </div>
  )
}
