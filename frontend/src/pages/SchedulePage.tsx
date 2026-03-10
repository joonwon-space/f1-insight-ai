import { useState, useEffect } from 'react'
import { api } from '@/lib/api'
import {
  type SeasonCalendar,
  type CurrentSessionInfo,
  type RaceEvent,
} from '@/types/api'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { Clock, MapPin, Flag, Zap } from 'lucide-react'

const SESSION_LABELS: Record<string, string> = {
  fp1: 'FP1',
  fp2: 'FP2',
  fp3: 'FP3',
  qualifying: 'Qualifying',
  sprint_qualifying: 'Sprint Q',
  sprint: 'Sprint',
  race: 'Race',
}

function formatSessionTime(isoStr: string): string {
  return new Date(isoStr).toLocaleString('en-US', {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    timeZoneName: 'short',
  })
}

function formatCountdown(targetIso: string): string {
  const now = Date.now()
  const target = new Date(targetIso).getTime()
  const diff = target - now

  if (diff <= 0) return 'Now'

  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60))
  const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))

  if (days > 0) return `${days}d ${hours}h`
  if (hours > 0) return `${hours}h ${minutes}m`
  return `${minutes}m`
}

function EventCard({
  event,
  isNext,
  isCurrent,
}: {
  event: RaceEvent
  isNext: boolean
  isCurrent: boolean
}) {
  const [expanded, setExpanded] = useState(isNext || isCurrent)
  const raceSession = event.sessions.find((s) => s.session_type === 'race')

  return (
    <div
      className={`rounded-lg border p-4 transition-colors ${
        isCurrent
          ? 'border-[#e10600] bg-red-900/10'
          : isNext
            ? 'border-gray-600 bg-gray-800/50'
            : 'border-gray-800 bg-gray-900/50'
      }`}
    >
      <button
        className="w-full text-left"
        onClick={() => setExpanded((v) => !v)}
      >
        <div className="flex items-start justify-between gap-2">
          <div className="flex-1">
            <div className="mb-1 flex items-center gap-2">
              <span className="font-mono text-xs text-gray-500">
                R{String(event.round_number).padStart(2, '0')}
              </span>
              {isCurrent && (
                <Badge variant="default" className="text-[10px]">
                  LIVE
                </Badge>
              )}
              {isNext && !isCurrent && (
                <Badge variant="secondary" className="text-[10px]">
                  NEXT
                </Badge>
              )}
              {event.is_sprint_weekend && (
                <Badge
                  variant="outline"
                  className="border-yellow-700 text-[10px] text-yellow-500"
                >
                  <Zap className="mr-1 h-2.5 w-2.5" />
                  Sprint
                </Badge>
              )}
            </div>
            <h3 className="font-semibold text-white">{event.event_name}</h3>
            <div className="mt-1 flex items-center gap-1 text-xs text-gray-400">
              <MapPin className="h-3 w-3" />
              <span>
                {event.circuit}, {event.country}
              </span>
            </div>
          </div>
          {raceSession && isNext && (
            <div className="shrink-0 text-right">
              <div className="flex items-center gap-1 text-xs text-gray-500">
                <Clock className="h-3 w-3" />
                Race in
              </div>
              <div className="font-mono text-lg font-bold text-[#e10600]">
                {formatCountdown(raceSession.start_time)}
              </div>
            </div>
          )}
        </div>
      </button>

      {expanded && (
        <div className="mt-3 space-y-1.5 border-t border-gray-800 pt-3">
          {event.sessions.map((session) => (
            <div
              key={session.session_type}
              className={`flex items-center justify-between rounded px-2 py-1 text-sm ${
                session.status === 'in_progress'
                  ? 'bg-red-900/30 text-white'
                  : session.status === 'completed'
                    ? 'text-gray-600'
                    : 'text-gray-300'
              }`}
            >
              <div className="flex items-center gap-2">
                <span
                  className={`h-1.5 w-1.5 rounded-full ${
                    session.status === 'in_progress'
                      ? 'animate-pulse bg-[#e10600]'
                      : session.status === 'completed'
                        ? 'bg-gray-700'
                        : 'bg-gray-500'
                  }`}
                />
                <span className="w-20 font-medium">
                  {SESSION_LABELS[session.session_type]}
                </span>
              </div>
              <span className="text-xs">
                {formatSessionTime(session.start_time)}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export function SchedulePage() {
  const [calendar, setCalendar] = useState<SeasonCalendar | null>(null)
  const [currentInfo, setCurrentInfo] = useState<CurrentSessionInfo | null>(
    null,
  )
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    Promise.all([
      api.get<SeasonCalendar>('/api/schedule?year=2026'),
      api.get<CurrentSessionInfo>('/api/schedule/current'),
    ])
      .then(([cal, curr]) => {
        setCalendar(cal)
        setCurrentInfo(curr)
        setLoading(false)
      })
      .catch((err) => {
        setError(
          err instanceof Error ? err.message : 'Failed to load schedule',
        )
        setLoading(false)
      })
  }, [])

  if (loading) {
    return (
      <div>
        <Skeleton className="mb-6 h-8 w-48" />
        <div className="space-y-3">
          {Array.from({ length: 8 }).map((_, i) => (
            <Skeleton key={i} className="h-16 w-full" />
          ))}
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="rounded-lg border border-red-800 bg-red-900/20 p-4 text-red-400">
        {error}
      </div>
    )
  }

  const events = calendar?.events ?? []
  const currentEventId = currentInfo?.current_event?.round_number
  const nextEventId = currentInfo?.next_event?.round_number

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold">
          <Flag className="mr-2 inline h-6 w-6 text-[#e10600]" />
          2026 Season Calendar
        </h1>
        <span className="text-sm text-gray-400">
          {events.length} Grands Prix
        </span>
      </div>

      <div className="space-y-3">
        {events.map((event) => (
          <EventCard
            key={event.round_number}
            event={event}
            isNext={event.round_number === nextEventId}
            isCurrent={event.round_number === currentEventId}
          />
        ))}
      </div>
    </div>
  )
}
