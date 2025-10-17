import React, { useState } from 'react'
import { api } from '../lib/api'

export default function CompressCard({ seqId }) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)

  const doCompress = async () => {
    setError('')
    setResult(null)
    if (!seqId) { setError('Upload or select a sequence first.'); return }
    try {
      setLoading(true)
      const data = await api.compress(seqId)
      setResult(data)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="card">
      <h2>Compress</h2>
      <button className="btn" onClick={doCompress} disabled={loading || !seqId}>
        {loading ? 'Compressing...' : 'Compress .txt → .gz'}
      </button>
      {error && <div className="error">{error}</div>}
      {result && (
        <div className="success">
          Ratio: {result.compression_ratio} • {result.compressed_file}
        </div>
      )}
    </div>
  )
}
