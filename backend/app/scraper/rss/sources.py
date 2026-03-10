"""RSS feed source definitions for F1 news collection."""

from app.models.article import NewsSource

# RSS feed URLs indexed by NewsSource
RSS_FEEDS: dict[NewsSource, list[str]] = {
    NewsSource.FORMULA1: [
        "https://www.formula1.com/en/latest/all.xml",
    ],
    NewsSource.THE_RACE: [
        "https://the-race.com/feed/",
    ],
    NewsSource.AUTOSPORT: [
        "https://www.autosport.com/rss/feed/f1",
    ],
}

# User-Agent string for RSS feed requests (identify as RSS reader, not scraper)
RSS_USER_AGENT = "F1InsightAI/1.0 RSS Reader (compatible; Feedparser)"
