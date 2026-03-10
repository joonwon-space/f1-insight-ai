import { Outlet } from 'react-router-dom'
import { useState } from 'react'
import { Header } from './Header'
import { Sidebar } from './Sidebar'

export function RootLayout() {
  const [selectedTeams, setSelectedTeams] = useState<string[]>([])

  return (
    <div className="flex min-h-screen flex-col bg-[#15151e] text-white">
      <Header />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar selectedTeams={selectedTeams} onTeamChange={setSelectedTeams} />
        <main className="flex-1 overflow-y-auto p-4 md:p-6">
          <Outlet context={{ selectedTeams }} />
        </main>
      </div>
    </div>
  )
}
