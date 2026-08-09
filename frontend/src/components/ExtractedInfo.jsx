const FIELDS = [
  ['procedure_name', 'Procedure'],
  ['body_site', 'Body Site'],
  ['approach', 'Approach'],
  ['device', 'Device'],
  ['qualifier', 'Qualifier'],
  ['query', 'Search Query'],
]

export default function ExtractedInfo({ info }) {
  if (!info) return null
  const visible = FIELDS.filter(
    ([key]) => info[key] && String(info[key]).toLowerCase() !== 'none'
  )
  if (visible.length === 0) return null

  return (
    <div className="extracted-info">
      <div className="card-title">Extracted Procedure Information</div>
      <div className="extracted-grid">
        {visible.map(([key, label]) => (
          <div className="extracted-field" key={key}>
            <label>{label}</label>
            <span>{info[key]}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
