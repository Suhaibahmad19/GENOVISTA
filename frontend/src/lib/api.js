const base = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

async function request(path, options = {}) {
  const res = await fetch(`${base}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {})
    },
    ...options
  })
  const text = await res.text()
  let data
  try { data = text ? JSON.parse(text) : null } catch {
    data = text
  }
  if (!res.ok) {
    const msg = (data && (data.detail || data.message)) || res.statusText
    throw new Error(msg)
  }
  return data
}

export const api = {
  root: () => request('/'),
  listSequences: () => request('/sequences/'),
  uploadSequence: (sequence) => request('/sequences/', {
    method: 'POST',
    body: JSON.stringify({ sequence })
  }),
  getSequence: (id) => request(`/sequences/${id}`),
  updateSequence: (id, sequence) => request(`/sequences/${id}`, {
    method: 'PUT',
    body: JSON.stringify({ sequence })
  }),
  deleteSequence: (id) => request(`/sequences/${id}`, { method: 'DELETE' }),
  compress: (id) => request(`/sequences/${id}/compress`, { method: 'POST' }),
  decompress: (id) => request(`/sequences/${id}/decompress`),
  gc: (id) => request(`/sequences/${id}/gc`),
  freq: (id) => request(`/sequences/${id}/freq`),
  motif: (id, pattern, use_regex=false) => request(`/sequences/${id}/motif`, {
    method: 'POST',
    body: JSON.stringify({ pattern, use_regex })
  })
}
