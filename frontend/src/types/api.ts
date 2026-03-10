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

// Schedule types
export type SessionType =
  | 'fp1'
  | 'fp2'
  | 'fp3'
  | 'qualifying'
  | 'sprint_qualifying'
  | 'sprint'
  | 'race'
export type SessionStatus = 'upcoming' | 'in_progress' | 'completed'

export interface Session {
  session_type: SessionType
  start_time: string
  end_time: string
  status: SessionStatus
}

export interface RaceEvent {
  round_number: number
  event_name: string
  country: string
  circuit: string
  start_date: string
  end_date: string
  sessions: Session[]
  is_sprint_weekend: boolean
}

export interface SeasonCalendar {
  year: number
  events: RaceEvent[]
}

export interface CurrentSessionInfo {
  current_session: Session | null
  current_event: RaceEvent | null
  next_session: Session | null
  next_event: RaceEvent | null
}

// Search types
export interface SearchHit {
  score: number
  source: ArticleDocument
}

export interface SearchResult {
  total: number
  hits: SearchHit[]
  took_ms: number
}
