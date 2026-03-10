import { useState } from 'react'
import { ChevronDown } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'

const F1_TEAMS = [
  { id: 'mercedes', name: 'Mercedes', color: '#00D2BE' },
  { id: 'ferrari', name: 'Ferrari', color: '#DC0000' },
  { id: 'mclaren', name: 'McLaren', color: '#FF8000' },
  { id: 'red-bull', name: 'Red Bull', color: '#3671C6' },
  { id: 'alpine', name: 'Alpine', color: '#FF87BC' },
  { id: 'williams', name: 'Williams', color: '#64C4FF' },
  { id: 'vcarb', name: 'VCARB', color: '#6692FF' },
  { id: 'aston-martin', name: 'Aston Martin', color: '#358C75' },
  { id: 'haas', name: 'Haas', color: '#B6BABD' },
  { id: 'audi', name: 'Audi', color: '#e5e5e5' },
  { id: 'cadillac', name: 'Cadillac', color: '#ffffff' },
]

interface SidebarProps {
  selectedTeams?: string[]
  onTeamChange?: (teams: string[]) => void
}

export function Sidebar({ selectedTeams = [], onTeamChange }: SidebarProps) {
  const [teamsExpanded, setTeamsExpanded] = useState(true)

  const handleTeamToggle = (teamId: string) => {
    const next = selectedTeams.includes(teamId)
      ? selectedTeams.filter((t) => t !== teamId)
      : [...selectedTeams, teamId]
    onTeamChange?.(next)
  }

  return (
    <aside className="hidden w-56 shrink-0 border-r border-gray-800 bg-[#15151e] p-4 lg:block">
      {/* Teams filter */}
      <div>
        <button
          onClick={() => setTeamsExpanded((v) => !v)}
          className="mb-3 flex w-full items-center justify-between text-sm font-medium text-gray-300 hover:text-white"
        >
          Teams
          <ChevronDown
            className={`h-4 w-4 transition-transform ${teamsExpanded ? 'rotate-180' : ''}`}
          />
        </button>

        {teamsExpanded && (
          <div className="space-y-1">
            {F1_TEAMS.map((team) => {
              const selected = selectedTeams.includes(team.id)
              return (
                <button
                  key={team.id}
                  onClick={() => handleTeamToggle(team.id)}
                  className={`flex w-full items-center gap-2 rounded px-2 py-1 text-xs transition-colors ${
                    selected ? 'text-white' : 'text-gray-500 hover:text-gray-300'
                  }`}
                >
                  <span
                    className="h-2 w-2 shrink-0 rounded-full"
                    style={{ backgroundColor: team.color }}
                  />
                  {team.name}
                  {selected && (
                    <Badge variant="secondary" className="ml-auto px-1 py-0 text-[10px]">
                      ✓
                    </Badge>
                  )}
                </button>
              )
            })}
          </div>
        )}
      </div>

      <Separator className="my-4" />

      {selectedTeams.length > 0 && (
        <button
          onClick={() => onTeamChange?.([])}
          className="w-full text-left text-xs text-gray-500 hover:text-gray-300"
        >
          Clear filters
        </button>
      )}
    </aside>
  )
}
