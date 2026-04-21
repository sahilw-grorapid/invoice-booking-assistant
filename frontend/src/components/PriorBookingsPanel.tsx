import { useState } from 'react'
import type { PriorBookingRef } from '../types'

interface Props {
  bookings: PriorBookingRef[]
  onApply: (row: PriorBookingRef) => void
}

// Shows the prior bookings the model cited as evidence. Empty list → new-vendor warning banner.
export function PriorBookingsPanel({ bookings, onApply }: Props) {
  const [open, setOpen] = useState(true)

  if (bookings.length === 0) {
    return (
      <div className="panel panel--warning">
        <strong>No prior bookings for this vendor.</strong>
        <p>Please verify Konto and Kostenstelle manually before submitting.</p>
      </div>
    )
  }

  return (
    <div className="panel">
      <button className="panel__toggle" onClick={() => setOpen((o) => !o)}>
        {open ? '▾' : '▸'} Prior bookings used as evidence ({bookings.length})
      </button>
      {open && (
        <table className="priors">
          <thead>
            <tr>
              <th>Amount</th>
              <th>Konto</th>
              <th>Gegenkonto</th>
              <th>KSt</th>
              <th>Buchungstext</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {bookings.map((b, index) => (
              <tr key={`${b.gegenkonto}-${b.konto}-${b.amount}-${index}`}>
                <td className="right">{b.amount.toFixed(2)} €</td>
                <td>{b.konto}</td>
                <td>{b.gegenkonto}</td>
                <td>{b.kostenstelle}</td>
                <td>{b.buchungstext}</td>
                <td>
                  <button className="link" onClick={() => onApply(b)}>
                    use this
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}
