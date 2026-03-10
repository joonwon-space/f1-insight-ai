"""F1 news scraper package.

Provides two collection strategies:
- RSS (primary): feedparser-based, lower footprint, official feeds
- HTML scraping (secondary): BeautifulSoup-based, full article content
"""

from app.scraper.rss.service import RSSService
from app.scraper.service import ScraperService

__all__ = ["RSSService", "ScraperService"]
