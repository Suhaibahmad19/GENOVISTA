import React, { useState } from 'react'
import { api } from '../lib/api'

export default function MotifSearchCard({ seqId }) {
  const [pattern, setPattern] = useState('ATG')
  const [useRegex, setUseRegex] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)

  const run = async () => {
    setError('')
    setResult(null)
    if (!seqId) { setError('Upload or select a sequence first.'); return }
    try {
      setLoading(true)
      const data = await api.motif(seqId, pattern, useRegex)
      setResult(data)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="card">
      <h2>Motif Search</h2>
      <div className="field">
        <label>Pattern {useRegex ? '(regex)' : '(literal)'}</label>
        <input value={pattern} onChange={(e) => setPattern(e.target.value)} placeholder="ATG|GTG" />
      </div>
      <div className="field row">
        <label className="checkbox">
          <input type="checkbox" checked={useRegex} onChange={(e) => setUseRegex(e.target.checked)} /> Use regex
        </label>
      </div>
      <button className="btn" onClick={run} disabled={loading || !seqId}>
        {loading ? 'Searching...' : 'Search'}
      </button>
      {error && <div className="error">{error}</div>}
      {result && (
        <div className="success">
          Total matches: {result.total_matches}
          <div className="muted" style={{maxHeight: 140, overflow: 'auto'}}>
            {result.matches.map((m, i) => (
              <div key={i}>[{m.start}-{m.end}] {m.match}</div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
