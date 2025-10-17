import React, { useEffect, useState } from 'react'
import UploadForm from './components/UploadForm'
import SequenceList from './components/SequenceList'
import CompressCard from './components/CompressCard'
import DecompressCard from './components/DecompressCard'
import GCContentCard from './components/GCContentCard'
import FreqCard from './components/FreqCard'
import MotifSearchCard from './components/MotifSearchCard'
import { api } from './lib/api'

export default function App() {
  const [seqId, setSeqId] = useState('')
  const [seqPreview, setSeqPreview] = useState('')
  const [seqFull, setSeqFull] = useState('')
  const [seqFullLoading, setSeqFullLoading] = useState(false)
  const [editState, setEditState] = useState({ mode: 'create' })
  const [items, setItems] = useState([])
  const [loadingList, setLoadingList] = useState(false)

  const loadList = async () => {
    setLoadingList(true)
    try {
      const data = await api.listSequences()
      setItems(data.items || [])
      // keep selection if still exists
      if (seqId && !(data.items || []).some(x => x.id === seqId)) { setSeqId(''); setSeqPreview(''); setSeqFull('') }
    } finally {
      setLoadingList(false)
    }
  }

  useEffect(() => { loadList() }, [])

  const selectSequence = async (it) => {
    setSeqId(it.id)
    setSeqPreview(it.preview || '')
    setSeqFull('')
    setSeqFullLoading(true)
    try {
      const data = await api.getSequence(it.id)
      setSeqFull(data.sequence || '')
    } finally {
      setSeqFullLoading(false)
    }
  }

  return (
    <div className="container">
      <header className="header">
        <h1>GENOVISTA</h1>
        <p className="subtitle">Genomic Compression & Analysis</p>
      </header>

      <section className="main-grid">
        <div>
          <UploadForm onUploaded={() => { setSeqId(''); setSeqPreview(''); setSeqFull(''); loadList() }} />
          <div className="notice" style={{marginTop:12}}>
            {loadingList ? 'Loading sequences...' : 'Select a sequence to operate on.'}
          </div>
          <div style={{marginTop:12}}>
            <SequenceList
              items={items}
              selectedId={seqId}
              onSelect={selectSequence}
              onRefresh={loadList}
              onViewUpdate={async (it)=>{
                // enter edit mode: fetch full DNA, prefill form
                setSeqId(''); setSeqPreview(''); setSeqFull('')
                const data = await api.getSequence(it.id)
                setEditState({ mode:'update', id: it.id, sequence: data.sequence || '' })
              }}
              onDelete={async (it)=>{
                await api.deleteSequence(it.id)
                if (seqId === it.id) { setSeqId(''); setSeqPreview(''); setSeqFull('') }
                loadList()
              }}
            />
          </div>
        </div>
        <div>
          {editState.mode==='update' ? (
            <UploadForm
              mode="update"
              editId={editState.id}
              initialSequence={editState.sequence}
              onUpdated={() => { setEditState({mode:'create'}); loadList() }}
              onCancel={() => setEditState({mode:'create'})}
            />
          ) : seqId ? (
            <>
              <div className="notice">Active DNA: <strong style={{fontFamily:'ui-monospace, SFMono-Regular, Menlo, monospace', wordBreak:'break-all'}}>{seqFullLoading ? 'Loading…' : (seqFull || seqPreview || '(empty)')}</strong></div>
              <div className="grid" style={{marginTop:12}}>
                <CompressCard seqId={seqId} />
                <DecompressCard seqId={seqId} />
                <GCContentCard seqId={seqId} />
                <FreqCard seqId={seqId} />
                <MotifSearchCard seqId={seqId} />
              </div>
            </>
          ) : (
            <div className="card"><div className="muted">No sequence selected.</div></div>
          )}
        </div>
      </section>

      <footer className="footer">Backend base URL is configurable via VITE_API_BASE</footer>
    </div>
  )
}
