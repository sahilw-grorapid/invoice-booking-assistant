import type { Confidence } from '../types'

const LABEL: Record<Confidence, string> = {
  high: 'High',
  medium: 'Medium',
  low: 'Low',
}

export function ConfidenceBadge({ level }: { level: Confidence }) {
  return <span className={`badge badge--${level}`}>{LABEL[level]} confidence</span>
}
