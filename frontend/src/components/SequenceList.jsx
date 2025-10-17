import React from 'react'

export default function SequenceList({ items, selectedId, onSelect, onRefresh, onViewUpdate, onDelete }) {
  return (
    <div className="card" style={{minWidth: 440}}>
      <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',marginBottom:8}}>
        <h2 style={{margin:0}}>Sequences</h2>
        <button className="btn" onClick={onRefresh}>Refresh</button>
      </div>
      <div className="muted" style={{marginBottom:8}}>{items.length} items</div>
      <div style={{display:'grid',gap:8}}>
        {items.map(it => (
          <div key={it.id} className="btn" onClick={() => onSelect(it)} style={{
            display:'grid', gridTemplateColumns:'1fr auto', alignItems:'center', gap:8,
            background: selectedId===it.id ? 'linear-gradient(180deg,#152140,#101a33)' : undefined
          }}>
            <div>
              <div style={{fontFamily:'ui-monospace, SFMono-Regular, Menlo, monospace', whiteSpace:'nowrap', overflow:'hidden', textOverflow:'ellipsis'}}>
                {it.preview || '(empty)'}
              </div>
              <div className="muted" style={{fontSize:12}}>{it.length ?? '?'} bp {it.compressed ? '• gz' : ''}</div>
            </div>
            <div style={{display:'flex', gap:6}} onClick={(e)=>e.stopPropagation()}>
              <button className="btn" onClick={()=>onViewUpdate?.(it)}>Edit</button>
              <button className="btn" onClick={()=>onDelete?.(it)}>Delete</button>
            </div>
          </div>
        ))}
        {items.length===0 && <div className="muted">No sequences yet.</div>}
      </div>
    </div>
  )
}
