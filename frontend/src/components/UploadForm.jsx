import React, { useEffect, useState } from 'react'
import { api } from '../lib/api'

export default function UploadForm({ mode = 'create', editId = '', initialSequence = '', onUploaded, onUpdated, onCancel }) {
  const [sequence, setSequence] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)

  useEffect(() => {
    if (mode === 'update') setSequence(initialSequence || '')
    else setSequence('')
    setResult(null)
    setError('')
  }, [mode, initialSequence, editId])

  const submit = async (e) => {
    e.preventDefault()
    setError('')
    setResult(null)

    const seq = sequence.replace(/\s+/g, '').toUpperCase()
    if (!seq) { setError('Sequence cannot be empty.'); return }
    if (!/^[-ATCG]+$/.test(seq)) {
      setError('Only A, T, C, G are allowed.')
      return
    }

    try {
      setLoading(true)
      if (mode === 'update' && editId) {
        const data = await api.updateSequence(editId, seq)
        setResult(data)
        onUpdated?.(editId, seq)
      } else {
        const data = await api.uploadSequence(seq)
        setResult(data)
        const preview = seq.slice(0,20) + (seq.length > 20 ? '...' : '')
        onUploaded?.(data.id, preview)
        setSequence('')
      }
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="card" style={{minWidth: 440}}>
      <div style={{display:'flex',alignItems:'center',justifyContent:'space-between'}}>
        <h2 style={{margin:0}}>{mode === 'update' ? 'Update Sequence' : 'Upload Sequence'}</h2>
        {mode === 'update' && (
          <button type="button" className="btn" onClick={onCancel} disabled={loading}>Cancel</button>
        )}
      </div>
      <form onSubmit={submit} className="form">
        <div className="field">
          <label>Sequence (A/T/C/G)</label>
          <textarea rows={4} value={sequence} onChange={(e) => setSequence(e.target.value)} placeholder="ATCG..." />
        </div>
        <button className="btn" disabled={loading}>{loading ? (mode==='update'?'Updating...':'Uploading...') : (mode==='update'?'Update':'Upload')}</button>
        {error && <div className="error">{error}</div>}
        {result && (
          <div className="success">{mode==='update' ? 'Updated Successfully' : 'Uploaded Successfully'}</div>
        )}
      </form>
    </div>
  )
}
