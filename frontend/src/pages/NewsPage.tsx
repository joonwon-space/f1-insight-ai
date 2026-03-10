import { Skeleton } from '@/components/ui/skeleton'

export function NewsPage() {
  return (
    <div>
      <h1 className="mb-6 text-2xl font-bold">Latest F1 News</h1>
      {/* Skeleton loading placeholders */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className="space-y-3 rounded-lg border border-gray-800 p-4">
            <Skeleton className="h-40 w-full" />
            <Skeleton className="h-4 w-3/4" />
            <Skeleton className="h-3 w-1/2" />
          </div>
        ))}
      </div>
    </div>
  )
}
