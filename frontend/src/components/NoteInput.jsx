import { useState } from 'react'

const SAMPLE = `Patient: Male, 54 years old
Date: 2026-07-06

Chief Complaint: Acute abdominal pain, right lower quadrant

Operative Note:
Patient presented to the ER with a 24-hour history of worsening right lower
quadrant pain, nausea, and low-grade fever. CT scan confirmed acute appendicitis
with no evidence of perforation. Patient was taken to the OR urgently.

Procedure performed: Laparoscopic appendectomy. Three ports were placed. The
appendix was identified, mesoappendix was divided using an endoscopic stapler,
and the appendix was ligated at its base and resected. Specimen was removed via
an endoscopic bag. No spillage occurred. Peritoneal cavity was irrigated and
inspected. All ports closed. Patient tolerated the procedure well.`

export default function NoteInput({ onSubmit, loading }) {
  const [content, setContent] = useState('')

  function handleSubmit(e) {
    e.preventDefault()
    if (content.trim()) onSubmit(content)
  }

  return (
    <div className="card">
      <div className="card-title">Doctor's Operative / Clinical Note</div>
      <form onSubmit={handleSubmit}>
        <textarea
          className="note-textarea"
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder="Paste the operative note or clinical documentation here…"
          disabled={loading}
        />
        <div className="note-actions">
          <button
            type="submit"
            className="btn btn-primary"
            disabled={loading || !content.trim()}
          >
            {loading ? 'Processing…' : 'Extract & Code'}
          </button>
          <button
            type="button"
            className="btn btn-ghost"
            onClick={() => setContent(SAMPLE)}
            disabled={loading}
          >
            Load Sample
          </button>
          {content && (
            <button
              type="button"
              className="btn btn-ghost"
              onClick={() => setContent('')}
              disabled={loading}
            >
              Clear
            </button>
          )}
          <span className="char-count">{content.length.toLocaleString()} chars</span>
        </div>
      </form>
    </div>
  )
}
