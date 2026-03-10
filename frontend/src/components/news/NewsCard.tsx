import { Clock } from 'lucide-react'
import { Link } from 'react-router-dom'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'
import { type ArticleDocument } from '@/types/api'

interface NewsCardProps {
  article: ArticleDocument
}

function formatDate(dateStr: string | null): string {
  if (!dateStr) return 'Unknown date'
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
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

export function NewsCard({ article }: NewsCardProps) {
  const preview = article.summary_en || article.content.slice(0, 150) + '...'
  const articleId = encodeURIComponent(article.url)

  return (
    <Card className="flex flex-col overflow-hidden transition-colors hover:border-gray-600 group">
      {/* Image */}
      {article.image_url ? (
        <div className="h-40 overflow-hidden bg-gray-800">
          <img
            src={article.image_url}
            alt={article.title}
            className="h-full w-full object-cover transition-transform group-hover:scale-105"
            loading="lazy"
          />
        </div>
      ) : (
        <div className="h-40 bg-gray-800 flex items-center justify-center">
          <span className="text-4xl font-bold text-[#e10600] opacity-30">F1</span>
        </div>
      )}

      <CardContent className="flex flex-1 flex-col gap-3 p-4">
        {/* Source + Date */}
        <div className="flex items-center gap-2 text-xs text-gray-500">
          <span className="font-medium text-[#e10600]">{formatSource(article.source)}</span>
          <span>·</span>
          <Clock className="h-3 w-3" />
          <span>{formatDate(article.published_at)}</span>
        </div>

        {/* Title */}
        <Link
          to={`/news/${articleId}`}
          className="font-semibold text-white leading-snug hover:text-[#e10600] transition-colors line-clamp-2"
        >
          {article.title}
        </Link>

        {/* Summary preview */}
        <p className="text-sm text-gray-400 line-clamp-3 flex-1">{preview}</p>

        {/* Teams */}
        {article.teams.length > 0 && (
          <div className="flex flex-wrap gap-1">
            {article.teams.slice(0, 3).map((team) => (
              <Badge key={team} variant="team" className="text-[10px]">
                {team}
              </Badge>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
