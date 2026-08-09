import { useState } from 'react'
import api from '../api/client'
import NoteInput from '../components/NoteInput'
import ExtractedInfo from '../components/ExtractedInfo'
import CodeCard from '../components/CodeCard'
import LoadingSpinner from '../components/LoadingSpinner'

export default function HomePage() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [result, setResult] = useState(null)

  async function handleSubmit(content) {
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const { data } = await api.post('/notes', { content })
      setResult(data)
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Unexpected error')
    } finally {
      setLoading(false)
    }
  }

  const suggestions = result?.session?.suggestions ?? []

  return (
    <div>
      <div className="page-header">
        <h1>ICD-10-PCS Code Suggestions</h1>
        <p>
          Paste an operative note — the AI extracts the procedure, then searches
          78 000+ codes and reranks the best matches.
        </p>
      </div>

      <NoteInput onSubmit={handleSubmit} loading={loading} />

      {loading && (
        <LoadingSpinner text="Sending to Ollama, embedding, and reranking…" />
      )}

      {error && <div className="error-box">{error}</div>}

      {result && !loading && (
        <div className="results-section">
          <ExtractedInfo info={result.session.extracted_info} />

          <div className="results-header">
            <h2>Suggested Codes</h2>
            <span className="results-count">{suggestions.length} results</span>
          </div>

          {suggestions.length === 0 ? (
            <div className="empty-state">
              <div className="empty-icon">🔍</div>
              <p>No matching codes found. Try a more detailed note.</p>
            </div>
          ) : (
            <div className="codes-list">
              {suggestions.map((s, i) => (
                <CodeCard key={s.id} suggestion={s} index={i} />
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
