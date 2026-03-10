"""RSS feed collection service.

Primary data collection method -- fetches RSS feeds using feedparser,
converts entries to RawArticle objects, and deduplicates against known articles.

RSS is preferred over HTML scraping because:
- Lower server load (structured data, no parsing overhead)
- More reliable (official feed format)
- Avoids IP blocking risk
- Faster collection cycle
"""

import asyncio
import logging

import httpx

from app.models.article import NewsSource, RawArticle
from app.scraper.dedup import deduplicate_articles, normalize_url
from app.scraper.rss.parser import parse_feed
from app.scraper.rss.sources import RSS_FEEDS, RSS_USER_AGENT

logger = logging.getLogger(__name__)

# Seconds between RSS fetch requests (polite rate limiting)
RSS_FETCH_DELAY: float = 1.0
RSS_TIMEOUT_SECONDS: float = 30.0


class RSSService:
    """Fetches and parses RSS feeds from configured F1 news sources.

    This is the primary data collection pipeline. Results should be stored
    in MongoDB via ArticleRepository and indexed in Elasticsearch.
    """

    def __init__(
        self,
        *,
        sources: list[NewsSource] | None = None,
        fetch_delay: float = RSS_FETCH_DELAY,
    ) -> None:
        """Initialize the RSS service.

        Args:
            sources: Sources to collect from. Defaults to all configured RSS sources.
            fetch_delay: Seconds to wait between feed requests.
        """
        self._sources = sources or list(RSS_FEEDS.keys())
        self._fetch_delay = fetch_delay
        self._client: httpx.AsyncClient | None = None

    async def _ensure_client(self) -> httpx.AsyncClient:
        """Lazily create the async HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(RSS_TIMEOUT_SECONDS),
                follow_redirects=True,
                headers={
                    "User-Agent": RSS_USER_AGENT,
                    "Accept": (
                        "application/rss+xml, application/atom+xml, application/xml, text/xml"
                    ),
                },
            )
        return self._client

    async def _fetch_feed(self, feed_url: str) -> str | None:
        """Fetch a single RSS feed URL.

        Args:
            feed_url: The RSS feed URL.

        Returns:
            Raw feed XML content, or None on error.
        """
        client = await self._ensure_client()
        try:
            response = await client.get(feed_url)
            response.raise_for_status()
            return response.text
        except httpx.HTTPError as exc:
            logger.error("Failed to fetch RSS feed %s: %s", feed_url, exc)
            return None

    async def collect_all(
        self,
        *,
        existing_urls: set[str] | None = None,
        existing_titles: list[str] | None = None,
    ) -> list[RawArticle]:
        """Collect articles from all configured RSS sources.

        Args:
            existing_urls: Set of known article URLs (for deduplication).
            existing_titles: List of known article titles (for deduplication).

        Returns:
            List of new, unique articles collected from all RSS feeds.
        """
        known_urls = {normalize_url(u) for u in (existing_urls or set())}
        known_titles = list(existing_titles or [])
        all_articles: list[RawArticle] = []

        for source in self._sources:
            feed_urls = RSS_FEEDS.get(source, [])
            for feed_url in feed_urls:
                articles = await self._collect_feed(source, feed_url)
                all_articles.extend(articles)
                if self._fetch_delay > 0:
                    await asyncio.sleep(self._fetch_delay)

        # Deduplicate against known articles and within current batch
        unique = deduplicate_articles(
            all_articles,
            existing_urls=known_urls,
            existing_titles=known_titles,
        )

        logger.info(
            "RSS collection complete: %d raw articles, %d unique after dedup",
            len(all_articles),
            len(unique),
        )
        return unique

    async def collect_source(
        self,
        source: NewsSource,
        *,
        existing_urls: set[str] | None = None,
        existing_titles: list[str] | None = None,
    ) -> list[RawArticle]:
        """Collect articles from a single RSS source.

        Args:
            source: The news source to collect from.
            existing_urls: Known URLs for deduplication.
            existing_titles: Known titles for deduplication.

        Returns:
            New articles from this source.
        """
        known_urls = {normalize_url(u) for u in (existing_urls or set())}
        known_titles = list(existing_titles or [])
        feed_urls = RSS_FEEDS.get(source, [])
        all_articles: list[RawArticle] = []

        for feed_url in feed_urls:
            articles = await self._collect_feed(source, feed_url)
            all_articles.extend(articles)

        return deduplicate_articles(
            all_articles,
            existing_urls=known_urls,
            existing_titles=known_titles,
        )

    async def _collect_feed(self, source: NewsSource, feed_url: str) -> list[RawArticle]:
        """Fetch and parse a single RSS feed.

        Args:
            source: The news source this feed belongs to.
            feed_url: The RSS feed URL.

        Returns:
            List of articles parsed from the feed.
        """
        raw_content = await self._fetch_feed(feed_url)
        if not raw_content:
            return []
        return parse_feed(feed_url, source, raw_content)

    async def close(self) -> None:
        """Close the HTTP client and release resources."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None
