import { NavLink } from 'react-router-dom'

export default function Header() {
  return (
    <header className="header">
      <div className="header-inner">
        <NavLink to="/" className="header-brand">
          <span className="brand-icon">🏥</span>
          <div>
            <div className="brand-name">CodeScribe</div>
            <div className="brand-tag">ICD-10-PCS Coder</div>
          </div>
        </NavLink>
        <nav className="header-nav">
          <NavLink
            to="/"
            end
            className={({ isActive }) => 'nav-link' + (isActive ? ' active' : '')}
          >
            New Note
          </NavLink>
          <NavLink
            to="/history"
            className={({ isActive }) => 'nav-link' + (isActive ? ' active' : '')}
          >
            History
          </NavLink>
        </nav>
      </div>
    </header>
  )
}
