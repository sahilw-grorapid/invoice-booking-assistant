import type { FinalBookingJSON } from '../types'

export function SubmitResult({ json, onReset }: { json: FinalBookingJSON; onReset: () => void }) {
  return (
    <div className="submitted">
      <div className="submitted__head">
        <h3>Booking JSON</h3>
        <button className="link" onClick={onReset}>
          Book another invoice
        </button>
      </div>
      <pre>{JSON.stringify(json, null, 2)}</pre>
    </div>
  )
}
