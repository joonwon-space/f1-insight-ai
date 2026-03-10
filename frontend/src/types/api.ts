export interface ArticleDocument {
  url: string
  title: string
  content: string
  source: 'formula1.com' | 'the-race.com' | 'autosport.com'
  published_at: string | null
  author: string | null
  image_url: string | null
  tags: string[]
  teams: string[]
  drivers: string[]
  scraped_at: string
  summary_en: string | null
  summary_ko: string | null
  is_summarized: boolean
  is_tagged: boolean
}

export interface NewsListResponse {
  total: number
  page: number
  limit: number
  items: ArticleDocument[]
}
