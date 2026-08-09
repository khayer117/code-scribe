import { useEffect, useState } from 'react'
import api from '../api/client'
import ExtractedInfo from '../components/ExtractedInfo'
import CodeCard from '../components/CodeCard'
import LoadingSpinner from '../components/LoadingSpinner'

function fmtDate(iso) {
  return new Date(iso).toLocaleString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export default function HistoryPage() {
  const [notes, setNotes] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [expanded, setExpanded] = useState(null)

  useEffect(() => {
    api
      .get('/notes')
      .then((r) => setNotes(r.data))
      .catch((e) => setError(e.response?.data?.detail || 'Failed to load history'))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <LoadingSpinner text="Loading history…" />
  if (error) return <div className="error-box">{error}</div>

  return (
    <div>
      <div className="page-header">
        <h1>Coding History</h1>
        <p>{notes.length} note{notes.length !== 1 ? 's' : ''} processed — click any card to expand.</p>
      </div>

      {notes.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">📋</div>
          <p>No notes yet. Submit one from the home page.</p>
        </div>
      ) : (
        <div className="history-list">
          {notes.map((note) => {
            const session = note.sessions?.[0]
            const isOpen = expanded === note.id
            const pills = session?.suggestions?.slice(0, 5) ?? []

            return (
              <div key={note.id}>
                <div
                  className="history-card"
                  onClick={() => setExpanded(isOpen ? null : note.id)}
                >
                  <div className="history-card-header">
                    <span className="history-id">Note #{note.id}</span>
                    <span className="history-date">{fmtDate(note.created_at)}</span>
                  </div>
                  <div className="history-preview">
                    {note.content.replace(/\s+/g, ' ').substring(0, 130)}…
                  </div>
                  {pills.length > 0 && (
                    <div className="history-pills">
                      {pills.map((s) => (
                        <span key={s.code} className="code-pill">
                          {s.code}
                        </span>
                      ))}
                      {(session?.suggestions?.length ?? 0) > 5 && (
                        <span className="code-pill">
                          +{session.suggestions.length - 5}
                        </span>
                      )}
                    </div>
                  )}
                </div>

                {isOpen && session && (
                  <div className="history-detail">
                    <ExtractedInfo info={session.extracted_info} />
                    <div className="detail-section-title">
                      Suggested Codes ({session.suggestions.length})
                    </div>
                    <div className="codes-list">
                      {session.suggestions.map((s, i) => (
                        <CodeCard key={s.id} suggestion={s} index={i} />
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
