import { Link } from 'react-router-dom'

export function Header() {
  return (
    <header className="border-b border-gray-800 bg-[#15151e] px-6 py-4">
      <div className="flex items-center justify-between">
        <Link to="/" className="text-xl font-bold text-[#e10600]">
          F1 Insight AI
        </Link>
        <nav className="flex gap-6 text-sm text-gray-400">
          <Link to="/" className="hover:text-white transition-colors">News</Link>
          <Link to="/schedule" className="hover:text-white transition-colors">Schedule</Link>
          <Link to="/search" className="hover:text-white transition-colors">Search</Link>
        </nav>
      </div>
    </header>
  )
}
