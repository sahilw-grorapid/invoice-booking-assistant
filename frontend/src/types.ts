export type Confidence = 'high' | 'medium' | 'low'

export interface FieldSuggestion {
  value: string
  confidence: Confidence
}

export interface LineItem {
  description: string
  quantity: string
  unit_price_net: number | null
  amount_net: number | null
}

export interface InvoiceExtract {
  invoice_number: string
  invoice_date: string
  vendor_name: string
  line_items: LineItem[]
  amount_net: number
  amount_gross: number
  vat_rate: number
}

export interface Suggestion {
  konto: FieldSuggestion
  gegenkonto: FieldSuggestion
  kostenstelle: FieldSuggestion
  buchungstext: FieldSuggestion
}

export interface PriorBookingRef {
  buchungstext: string
  konto: string
  gegenkonto: string
  kostenstelle: string
  amount: number
}

export interface BookingResponse {
  invoice: InvoiceExtract
  suggestion: Suggestion
  confidence: Confidence
  confidence_score: number
  reasoning: string
  prior_bookings_used: PriorBookingRef[]
}

export interface FinalBookingJSON {
  invoice_number: string
  invoice_date: string
  vendor_name: string
  vendor_creditor_account: string
  amount_net: number
  amount_gross: number
  vat_rate: number
  konto: string
  kostenstelle: string
  buchungstext: string
  belegfeld_1: string
  belegdatum: string
  confidence: Confidence
  confidence_score: number
  reasoning: string
  prior_bookings_used: number
  user_modified: boolean
}
