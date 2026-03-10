import { useState, useEffect, useCallback } from 'react'
import { useOutletContext } from 'react-router-dom'
import { api } from '@/lib/api'
import { type ArticleDocument, type NewsListResponse } from '@/types/api'
import { NewsCard } from '@/components/news/NewsCard'
import { NewsCardSkeleton } from '@/components/news/NewsCardSkeleton'
import { Pagination } from '@/components/news/Pagination'

interface OutletContext {
  selectedTeams: string[]
}

const PAGE_SIZE = 12

export function NewsPage() {
  const { selectedTeams } = useOutletContext<OutletContext>()
  const [articles, setArticles] = useState<ArticleDocument[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchArticles = useCallback(async (currentPage: number, teams: string[]) => {
    setLoading(true)
    setError(null)
    try {
      const params = new URLSearchParams({
        page: String(currentPage),
        limit: String(PAGE_SIZE),
      })
      if (teams.length > 0) {
        params.set('team', teams[0])
      }
      const data = await api.get<NewsListResponse>(`/api/news?${params}`)
      setArticles(data.items)
      setTotal(data.total)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load news')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    setPage(1)
    fetchArticles(1, selectedTeams)
  }, [selectedTeams, fetchArticles])

  const handlePageChange = (newPage: number) => {
    setPage(newPage)
    fetchArticles(newPage, selectedTeams)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  const totalPages = Math.ceil(total / PAGE_SIZE)

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold">Latest F1 News</h1>
        {!loading && total > 0 && (
          <span className="text-sm text-gray-400">{total} articles</span>
        )}
      </div>

      {error && (
        <div className="mb-4 rounded-lg border border-red-800 bg-red-900/20 p-4 text-red-400 text-sm">
          {error}
        </div>
      )}

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {loading
          ? Array.from({ length: PAGE_SIZE }).map((_, i) => <NewsCardSkeleton key={i} />)
          : articles.map((article) => <NewsCard key={article.url} article={article} />)}
      </div>

      {!loading && articles.length === 0 && !error && (
        <div className="py-20 text-center text-gray-500">
          <p className="text-lg">No articles found</p>
          {selectedTeams.length > 0 && (
            <p className="text-sm mt-2">Try clearing the team filter</p>
          )}
        </div>
      )}

      <Pagination page={page} totalPages={totalPages} onPageChange={handlePageChange} />
    </div>
  )
}
