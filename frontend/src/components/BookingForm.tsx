import { useState } from 'react'
import type { BookingResponse, Confidence, FinalBookingJSON, LineItem } from '../types'
import { ConfidenceBadge } from './ConfidenceBadge'

interface FormState {
  invoice_number: string
  invoice_date: string
  vendor_name: string
  line_items: LineItem[]
  amount_net: string
  amount_gross: string
  vat_rate: string
  gegenkonto: string
  konto: string
  kostenstelle: string
  buchungstext: string
}

interface Props {
  state: FormState
  initial: FormState
  suggestion: BookingResponse
  onChange: (patch: Partial<FormState>) => void
  onSubmit: (final: FinalBookingJSON) => void
}

type BookingFieldKey = 'konto' | 'gegenkonto' | 'kostenstelle' | 'buchungstext'

const REQUIRED_BOOKING_FIELDS: { key: BookingFieldKey; label: string }[] = [
  { key: 'konto', label: 'Konto' },
  { key: 'gegenkonto', label: 'Gegenkonto' },
  { key: 'kostenstelle', label: 'Kostenstelle' },
  { key: 'buchungstext', label: 'Buchungstext' },
]

function fieldConfidence(s: BookingResponse, key: 'konto' | 'gegenkonto' | 'kostenstelle' | 'buchungstext'): Confidence {
  return s.suggestion[key].confidence
}

function numberOrNull(value: string): number | null {
  return value === '' ? null : Number(value)
}

// Editable booking form. Diffs current state against `initial` to flag `user_modified`,
// then emits the spec-shaped FinalBookingJSON on submit.
export function BookingForm({ state, initial, suggestion, onChange, onSubmit }: Props) {
  const [submitAttempted, setSubmitAttempted] = useState(false)
  const userModified = JSON.stringify(state) !== JSON.stringify(initial)
  const missingBookingFields = REQUIRED_BOOKING_FIELDS.filter(({ key }) => state[key].trim() === '')
  const fieldErrors = Object.fromEntries(
    missingBookingFields.map(({ key, label }) => [key, `${label} is required.`]),
  ) as Partial<Record<BookingFieldKey, string>>

  const updateLineItem = (index: number, patch: Partial<LineItem>) => {
    onChange({
      line_items: state.line_items.map((item, i) => (i === index ? { ...item, ...patch } : item)),
    })
  }

  const submit = () => {
    setSubmitAttempted(true)
    if (missingBookingFields.length > 0) {
      return
    }

    const final: FinalBookingJSON = {
      invoice_number: state.invoice_number,
      invoice_date: state.invoice_date,
      vendor_name: state.vendor_name,
      vendor_creditor_account: state.gegenkonto,
      amount_net: Number(state.amount_net) || 0,
      amount_gross: Number(state.amount_gross) || 0,
      vat_rate: Number(state.vat_rate) || 0,
      konto: state.konto,
      kostenstelle: state.kostenstelle,
      buchungstext: state.buchungstext,
      confidence: suggestion.confidence,
      confidence_score: suggestion.confidence_score,
      reasoning: suggestion.reasoning,
      prior_bookings_used: suggestion.prior_bookings_used.length,
      user_modified: userModified,
    }
    onSubmit(final)
  }

  return (
    <form
      className="form"
      onSubmit={(e) => {
        e.preventDefault()
        submit()
      }}
    >
      <h3>Invoice</h3>
      <div className="grid">
        <Field label="Vendor">
          <input value={state.vendor_name} onChange={(e) => onChange({ vendor_name: e.target.value })} />
        </Field>
        <Field label="Invoice number">
          <input value={state.invoice_number} onChange={(e) => onChange({ invoice_number: e.target.value })} />
        </Field>
        <Field label="Invoice date (yyyy-mm-dd)">
          <input value={state.invoice_date} onChange={(e) => onChange({ invoice_date: e.target.value })} />
        </Field>
        <Field label="Amount net (EUR)">
          <input
            type="number"
            step="0.01"
            value={state.amount_net}
            onChange={(e) => onChange({ amount_net: e.target.value })}
          />
        </Field>
        <Field label="Amount gross (EUR)">
          <input
            type="number"
            step="0.01"
            value={state.amount_gross}
            onChange={(e) => onChange({ amount_gross: e.target.value })}
          />
        </Field>
        <Field label="VAT rate %">
          <input
            type="number"
            step="0.1"
            value={state.vat_rate}
            onChange={(e) => onChange({ vat_rate: e.target.value })}
          />
        </Field>
      </div>

      <h3>Line items</h3>
      <div className="line-items">
        {state.line_items.length === 0 ? (
          <p className="muted">No line items extracted.</p>
        ) : (
          state.line_items.map((item, index) => (
            <div className="line-item" key={index}>
              <Field label="Description">
                <input
                  value={item.description}
                  onChange={(e) => updateLineItem(index, { description: e.target.value })}
                />
              </Field>
              <Field label="Quantity">
                <input value={item.quantity} onChange={(e) => updateLineItem(index, { quantity: e.target.value })} />
              </Field>
              <Field label="Unit price net (EUR)">
                <input
                  type="number"
                  step="0.01"
                  value={item.unit_price_net ?? ''}
                  onChange={(e) => updateLineItem(index, { unit_price_net: numberOrNull(e.target.value) })}
                />
              </Field>
              <Field label="Amount net (EUR)">
                <input
                  type="number"
                  step="0.01"
                  value={item.amount_net ?? ''}
                  onChange={(e) => updateLineItem(index, { amount_net: numberOrNull(e.target.value) })}
                />
              </Field>
            </div>
          ))
        )}
      </div>

      <h3>Booking</h3>
      <div className="grid">
        <SuggestedField
          label="Konto (SKR03)"
          level={fieldConfidence(suggestion, 'konto')}
          value={state.konto}
          onChange={(v) => onChange({ konto: v })}
          required
          error={submitAttempted ? fieldErrors.konto : undefined}
        />
        <SuggestedField
          label="Gegenkonto (creditor)"
          level={fieldConfidence(suggestion, 'gegenkonto')}
          value={state.gegenkonto}
          onChange={(v) => onChange({ gegenkonto: v })}
          required
          error={submitAttempted ? fieldErrors.gegenkonto : undefined}
        />
        <SuggestedField
          label="Kostenstelle"
          level={fieldConfidence(suggestion, 'kostenstelle')}
          value={state.kostenstelle}
          onChange={(v) => onChange({ kostenstelle: v })}
          required
          error={submitAttempted ? fieldErrors.kostenstelle : undefined}
        />
        <SuggestedField
          label="Buchungstext"
          level={fieldConfidence(suggestion, 'buchungstext')}
          value={state.buchungstext}
          onChange={(v) => onChange({ buchungstext: v })}
          required
          error={submitAttempted ? fieldErrors.buchungstext : undefined}
          wide
        />
      </div>

      <div className="actions">
        <button type="submit" className="submit">
          Submit booking
        </button>
        <span className="hint">{userModified ? 'You have edits — will be flagged in JSON.' : 'No edits yet.'}</span>
      </div>
    </form>
  )
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label className="field">
      <span className="field__label">{label}</span>
      {children}
    </label>
  )
}

function SuggestedField({
  label,
  level,
  value,
  onChange,
  required,
  error,
  wide,
}: {
  label: string
  level: Confidence
  value: string
  onChange: (v: string) => void
  required?: boolean
  error?: string
  wide?: boolean
}) {
  return (
    <label className={`field field--suggest field--${level} ${error ? 'field--error' : ''} ${wide ? 'field--wide' : ''}`}>
      <span className="field__label">
        {label} <ConfidenceBadge level={level} />
      </span>
      <input
        value={value}
        onChange={(e) => onChange(e.target.value)}
        required={required}
        aria-invalid={Boolean(error)}
      />
      {error ? (
        <span className="field__error">{error}</span>
      ) : (
        level === 'low' && <span className="field__hint">Please confirm — low confidence.</span>
      )}
    </label>
  )
}

export type { FormState }
