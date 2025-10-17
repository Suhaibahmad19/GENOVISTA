import React, { useState } from 'react'
import { api } from '../lib/api'

export default function GCContentCard({ seqId }) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)

  const run = async () => {
    setError('')
    setResult(null)
    if (!seqId) { setError('Upload or select a sequence first.'); return }
    try {
      setLoading(true)
      const data = await api.gc(seqId)
      setResult(data)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="card">
      <h2>GC Content</h2>
      <button className="btn" onClick={run} disabled={loading || !seqId}>
        {loading ? 'Calculating...' : 'Calculate'}
      </button>
      {error && <div className="error">{error}</div>}
      {result && (
        <div className="success">
          GC%: {result.GC_percent} • G: {result.G_count} • C: {result.C_count}
        </div>
      )}
    </div>
  )
}
