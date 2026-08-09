export default function LoadingSpinner({ text = 'Loading…' }) {
  return (
    <div className="spinner-wrap">
      <div className="spinner" />
      <span className="spinner-text">{text}</span>
    </div>
  )
}
