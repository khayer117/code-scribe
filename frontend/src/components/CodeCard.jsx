export default function CodeCard({ suggestion, index }) {
  const topClass = index < 3 ? ` top-${index + 1}` : ''
  return (
    <div className={`code-card${topClass}`}>
      <div className="code-rank">#{suggestion.rank}</div>
      <div className="code-badge">{suggestion.code}</div>
      <div className="code-body">
        <div className="code-description">{suggestion.description}</div>
      </div>
      {suggestion.similarity_score != null && (
        <div className="code-score">
          {suggestion.similarity_score.toFixed(3)}
        </div>
      )}
    </div>
  )
}
