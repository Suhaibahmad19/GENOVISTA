import React, { useState } from 'react'
import { api } from '../lib/api'

export default function FreqCard({ seqId }) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)

  const run = async () => {
    setError('')
    setResult(null)
    if (!seqId) { setError('Upload or select a sequence first.'); return }
    try {
      setLoading(true)
      const data = await api.freq(seqId)
      setResult(data)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="card">
      <h2>Nucleotide Frequency</h2>
      <button className="btn" onClick={run} disabled={loading || !seqId}>
        {loading ? 'Calculating...' : 'Calculate'}
      </button>
      {error && <div className="error">{error}</div>}
      {result && (
        <div className="success">
          <div>A: {result.counts.A} ({result.percentages.A}%)</div>
          <div>T: {result.counts.T} ({result.percentages.T}%)</div>
          <div>C: {result.counts.C} ({result.percentages.C}%)</div>
          <div>G: {result.counts.G} ({result.percentages.G}%)</div>
        </div>
      )}
    </div>
  )
}
