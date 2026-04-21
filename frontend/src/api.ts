import type { BookingResponse } from './types'

// POSTs the PDF to the backend and returns the parsed booking suggestion.
export async function suggestBooking(file: File): Promise<BookingResponse> {
  const form = new FormData()
  form.append('file', file)
  const res = await fetch('/api/suggest-booking', {
    method: 'POST',
    body: form,
  })
  if (!res.ok) {
    const detail = await res
      .json()
      .then((j) => j.detail)
      .catch(() => res.statusText)
    throw new Error(detail || `Request failed with status ${res.status}`)
  }
  return (await res.json()) as BookingResponse
}
