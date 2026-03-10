import { Skeleton } from '@/components/ui/skeleton'

export function SchedulePage() {
  return (
    <div>
      <h1 className="mb-6 text-2xl font-bold">2026 Season Calendar</h1>
      <div className="space-y-3">
        {Array.from({ length: 8 }).map((_, i) => (
          <Skeleton key={i} className="h-16 w-full" />
        ))}
      </div>
    </div>
  )
}
