import { useState, useCallback } from 'react'
import { Search, Clock } from 'lucide-react'
import { Link } from 'react-router-dom'
import { api } from '@/lib/api'
import { type SearchResult, type ArticleDocument } from '@/types/api'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'

function formatDate(dateStr: string | null): string {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}

function SearchResultItem({ article }: { article: ArticleDocument }) {
  const articleId = encodeURIComponent(article.url)
  const preview = article.summary_en || article.content.slice(0, 200)

  return (
    <div className="py-4">
      <div className="mb-1 flex items-center gap-2 text-xs text-gray-500">
        <span className="font-medium text-[#e10600]">{article.source}</span>
        {article.published_at && (
          <>
            <span>·</span>
            <Clock className="h-3 w-3" />
            <span>{formatDate(article.published_at)}</span>
          </>
        )}
      </div>
      <Link
        to={`/news/${articleId}`}
        className="line-clamp-2 text-base font-semibold text-white transition-colors hover:text-[#e10600]"
      >
        {article.title}
      </Link>
      <p className="mt-1 line-clamp-2 text-sm text-gray-400">{preview}</p>
      <div className="mt-2 flex flex-wrap gap-1">
        {article.teams.slice(0, 2).map((team) => (
          <Badge key={team} variant="team" className="text-[10px]">
            {team}
          </Badge>
        ))}
        {article.tags.slice(0, 3).map((tag) => (
          <Badge key={tag} variant="outline" className="text-[10px]">
            #{tag}
          </Badge>
        ))}
      </div>
    </div>
  )
}

export function SearchPage() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<ArticleDocument[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(false)
  const [searched, setSearched] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSearch = useCallback(async (q: string) => {
    if (!q.trim()) return
    setLoading(true)
    setError(null)
    try {
      const params = new URLSearchParams({ q: q.trim(), limit: '20' })
      const data = await api.get<SearchResult>(`/api/search?${params}`)
      setResults(data.hits.map((hit) => hit.source))
      setTotal(data.total)
      setSearched(true)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Search failed')
    } finally {
      setLoading(false)
    }
  }, [])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    handleSearch(query)
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      handleSearch(query)
    }
  }

  return (
    <div className="max-w-3xl">
      <h1 className="mb-6 text-2xl font-bold">Search</h1>

      {/* Search input */}
      <form onSubmit={handleSubmit} className="mb-8 flex gap-2">
        <div className="relative flex-1">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-500" />
          <Input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Search F1 news, drivers, teams..."
            className="pl-9"
            autoFocus
          />
        </div>
        <Button type="submit" disabled={loading || !query.trim()}>
          {loading ? 'Searching...' : 'Search'}
        </Button>
      </form>

      {/* Error */}
      {error && (
        <div className="mb-4 rounded-lg border border-red-800 bg-red-900/20 p-3 text-sm text-red-400">
          {error}
        </div>
      )}

      {/* Loading skeleton */}
      {loading && (
        <div className="space-y-4">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="space-y-2 py-4">
              <Skeleton className="h-3 w-32" />
              <Skeleton className="h-5 w-3/4" />
              <Skeleton className="h-4 w-full" />
            </div>
          ))}
        </div>
      )}

      {/* Results */}
      {!loading && searched && (
        <>
          <div className="mb-4 text-sm text-gray-400">
            {total === 0 ? (
              <span>
                No results for &quot;<span className="text-white">{query}</span>
                &quot;
              </span>
            ) : (
              <span>
                {total} result{total !== 1 ? 's' : ''} for &quot;
                <span className="text-white">{query}</span>&quot;
              </span>
            )}
          </div>

          <div className="divide-y divide-gray-800">
            {results.map((article) => (
              <SearchResultItem key={article.url} article={article} />
            ))}
          </div>
        </>
      )}

      {/* Initial state */}
      {!loading && !searched && (
        <div className="py-16 text-center text-gray-600">
          <Search className="mx-auto mb-3 h-12 w-12 opacity-30" />
          <p>Search across all F1 news articles</p>
          <p className="mt-1 text-sm">
            Try: &quot;Verstappen&quot;, &quot;McLaren qualifying&quot;,
            &quot;strategy&quot;
          </p>
        </div>
      )}
    </div>
  )
}
