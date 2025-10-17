import React, { useState } from 'react'
import { api } from '../lib/api'

export default function DecompressCard({ seqId }) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)

  const doDecompress = async () => {
    setError('')
    setResult(null)
    if (!seqId) { setError('Upload or select a sequence first.'); return }
    try {
      setLoading(true)
      const data = await api.decompress(seqId)
      setResult(data)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="card">
      <h2>Decompress & Verify</h2>
      <button className="btn" onClick={doDecompress} disabled={loading || !seqId}>
        {loading ? 'Decompressing...' : 'Decompress .gz'}
      </button>
      {error && <div className="error">{error}</div>}
      {result && (
        <div className="success">
          Length: {result.length} • Lossless: {String(result.lossless_verification)}
          <div className="muted">{result.sequence_preview}</div>
        </div>
      )}
    </div>
  )
}
