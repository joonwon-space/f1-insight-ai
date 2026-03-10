import { useState, useEffect } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { ArrowLeft, ExternalLink, Share2, Check, Clock, User } from 'lucide-react'
import { api } from '@/lib/api'
import { type ArticleDocument } from '@/types/api'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import { Skeleton } from '@/components/ui/skeleton'

function formatDate(dateStr: string | null): string {
  if (!dateStr) return 'Unknown date'
  return new Date(dateStr).toLocaleDateString('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}

function formatSource(source: string): string {
  const map: Record<string, string> = {
    'formula1.com': 'F1 Official',
    'the-race.com': 'The Race',
    'autosport.com': 'Autosport',
  }
  return map[source] || source
}

export function NewsDetailPage() {
  const { articleId } = useParams<{ articleId: string }>()
  const navigate = useNavigate()
  const [article, setArticle] = useState<ArticleDocument | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [copied, setCopied] = useState(false)

  useEffect(() => {
    if (!articleId) return
    const decodedUrl = decodeURIComponent(articleId)
    setLoading(true)
    api
      .get<ArticleDocument>(`/api/news/${encodeURIComponent(decodedUrl)}`)
      .then((data) => {
        setArticle(data)
        setLoading(false)
      })
      .catch((err) => {
        setError(err instanceof Error ? err.message : 'Failed to load article')
        setLoading(false)
      })
  }, [articleId])

  const handleShare = async () => {
    try {
      await navigator.clipboard.writeText(window.location.href)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch {
      // Clipboard not available
    }
  }

  if (loading) {
    return (
      <div className="max-w-3xl mx-auto">
        <Skeleton className="h-6 w-32 mb-6" />
        <Skeleton className="h-60 w-full mb-6" />
        <Skeleton className="h-8 w-3/4 mb-4" />
        <Skeleton className="h-4 w-1/3 mb-8" />
        <div className="space-y-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-4 w-full" />
          ))}
        </div>
      </div>
    )
  }

  if (error || !article) {
    return (
      <div className="max-w-3xl mx-auto text-center py-20">
        <p className="text-red-400 mb-4">{error || 'Article not found'}</p>
        <Button variant="outline" onClick={() => navigate('/')}>
          Back to News
        </Button>
      </div>
    )
  }

  return (
    <div className="max-w-3xl mx-auto">
      {/* Back button */}
      <Link
        to="/"
        className="inline-flex items-center gap-2 text-sm text-gray-400 hover:text-white mb-6 transition-colors"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to News
      </Link>

      {/* Hero image */}
      {article.image_url && (
        <div className="mb-6 overflow-hidden rounded-lg h-64">
          <img
            src={article.image_url}
            alt={article.title}
            className="h-full w-full object-cover"
          />
        </div>
      )}

      {/* Header */}
      <div className="mb-6">
        <div className="flex flex-wrap items-center gap-2 text-sm text-gray-400 mb-3">
          <span className="font-medium text-[#e10600]">{formatSource(article.source)}</span>
          <span>·</span>
          <Clock className="h-3.5 w-3.5" />
          <span>{formatDate(article.published_at)}</span>
          {article.author && (
            <>
              <span>·</span>
              <User className="h-3.5 w-3.5" />
              <span>{article.author}</span>
            </>
          )}
        </div>
        <h1 className="text-2xl font-bold text-white leading-snug mb-4">{article.title}</h1>

        {/* Team/Driver badges */}
        <div className="flex flex-wrap gap-2">
          {article.teams.map((team) => (
            <Badge key={team} variant="team">
              {team}
            </Badge>
          ))}
          {article.drivers.map((driver) => (
            <Badge key={driver} variant="outline">
              {driver}
            </Badge>
          ))}
        </div>
      </div>

      <Separator className="mb-6" />

      {/* English Summary */}
      {article.summary_en && (
        <div className="mb-6 rounded-lg border border-gray-700 bg-gray-900 p-5">
          <h2 className="text-xs font-semibold uppercase tracking-wider text-[#e10600] mb-3">
            Summary (EN)
          </h2>
          <p className="text-gray-200 leading-relaxed">{article.summary_en}</p>
        </div>
      )}

      {/* Korean Translation */}
      {article.summary_ko && (
        <div className="mb-6 rounded-lg border border-gray-700 bg-gray-900 p-5">
          <h2 className="text-xs font-semibold uppercase tracking-wider text-blue-400 mb-3">
            요약 (KR)
          </h2>
          <p className="text-gray-200 leading-relaxed">{article.summary_ko}</p>
        </div>
      )}

      {/* Full content fallback */}
      {!article.summary_en && (
        <div className="mb-6">
          <h2 className="text-xs font-semibold uppercase tracking-wider text-gray-500 mb-3">
            Content
          </h2>
          <p className="text-gray-300 leading-relaxed whitespace-pre-line">{article.content}</p>
        </div>
      )}

      <Separator className="mb-6" />

      {/* Tags */}
      {article.tags.length > 0 && (
        <div className="mb-6">
          <h3 className="text-xs text-gray-500 uppercase tracking-wider mb-2">Tags</h3>
          <div className="flex flex-wrap gap-2">
            {article.tags.map((tag) => (
              <Badge key={tag} variant="secondary">
                #{tag}
              </Badge>
            ))}
          </div>
        </div>
      )}

      {/* Action buttons */}
      <div className="flex gap-3">
        <Button variant="outline" size="sm" onClick={handleShare}>
          {copied ? (
            <>
              <Check className="h-4 w-4 mr-2 text-green-400" />
              Copied!
            </>
          ) : (
            <>
              <Share2 className="h-4 w-4 mr-2" />
              Share
            </>
          )}
        </Button>
        <Button variant="ghost" size="sm" asChild>
          <a href={article.url} target="_blank" rel="noopener noreferrer">
            <ExternalLink className="h-4 w-4 mr-2" />
            Read Original
          </a>
        </Button>
      </div>
    </div>
  )
}
