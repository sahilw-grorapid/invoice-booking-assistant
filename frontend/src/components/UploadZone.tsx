import { useCallback, useRef, useState } from 'react'

interface Props {
  onFile: (file: File) => void
  busy: boolean
}

// Drag-drop + file-picker for a single PDF. Calls `onFile` once a valid PDF is chosen.
export function UploadZone({ onFile, busy }: Props) {
  const inputRef = useRef<HTMLInputElement>(null)
  const [dragging, setDragging] = useState(false)

  const handleFile = useCallback(
    (file: File | undefined) => {
      if (!file) return
      if (!file.name.toLowerCase().endsWith('.pdf') && file.type !== 'application/pdf') {
        alert('Please upload a PDF file.')
        return
      }
      onFile(file)
    },
    [onFile],
  )

  return (
    <div
      className={`upload ${dragging ? 'upload--dragging' : ''} ${busy ? 'upload--busy' : ''}`}
      onDragOver={(e) => {
        e.preventDefault()
        if (!busy) setDragging(true)
      }}
      onDragLeave={() => setDragging(false)}
      onDrop={(e) => {
        e.preventDefault()
        setDragging(false)
        if (busy) return
        handleFile(e.dataTransfer.files?.[0])
      }}
      onClick={() => !busy && inputRef.current?.click()}
    >
      <input
        ref={inputRef}
        type="file"
        accept="application/pdf,.pdf"
        hidden
        onChange={(e) => handleFile(e.target.files?.[0] ?? undefined)}
      />
      {busy ? (
        <div className="upload__busy">
          <div className="spinner" />
          <p>Parsing invoice and looking up similar bookings…</p>
        </div>
      ) : (
        <>
          <div className="upload__icon">↑</div>
          <p className="upload__title">Drop a PDF invoice here</p>
          <p className="upload__sub">or click to browse</p>
        </>
      )}
    </div>
  )
}
