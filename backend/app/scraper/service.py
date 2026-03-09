"""Main scraper service orchestrating fetching, parsing, and deduplication."""

import logging

from app.models.article import ArticleLink, NewsSource, RawArticle
from app.scraper.dedup import deduplicate_articles, deduplicate_links, normalize_url
from app.scraper.http_client import ScraperHttpClient
from app.scraper.parsers import PARSER_REGISTRY
from app.scraper.parsers.base import BaseParser

logger = logging.getLogger(__name__)


class ScraperService:
    """Orchestrates scraping from all configured F1 news sources.

    Handles fetching listing pages, discovering article links, fetching
    individual articles, parsing content, and deduplicating results.
    """

    def __init__(
        self,
        *,
        http_client: ScraperHttpClient | None = None,
        sources: list[NewsSource] | None = None,
    ) -> None:
        """Initialize the scraper service.

        Args:
            http_client: Optional custom HTTP client (created if not provided).
            sources: Optional list of sources to scrape (defaults to all registered).
        """
        self._http_client = http_client or ScraperHttpClient()
        self._sources = sources or list(PARSER_REGISTRY.keys())

    async def scrape_all(
        self,
        *,
        existing_urls: set[str] | None = None,
        existing_titles: list[str] | None = None,
        max_articles_per_source: int = 20,
    ) -> list[RawArticle]:
        """Scrape articles from all configured sources.

        Args:
            existing_urls: Set of known article URLs for deduplication.
            existing_titles: List of known article titles for deduplication.
            max_articles_per_source: Maximum articles to fetch per source.

        Returns:
            List of new, deduplicated articles from all sources.
        """
        known_urls = {normalize_url(u) for u in (existing_urls or set())}
        known_titles = list(existing_titles or [])

        all_articles: list[RawArticle] = []

        for source in self._sources:
            try:
                articles = await self._scrape_source(
                    source=source,
                    existing_urls=known_urls,
                    max_articles=max_articles_per_source,
                )
                all_articles.extend(articles)
                logger.info("Scraped %d articles from %s", len(articles), source.value)
            except Exception:
                logger.error("Failed to scrape source %s", source.value, exc_info=True)
                continue

        # Cross-source deduplication
        unique_articles = deduplicate_articles(
            all_articles,
            existing_urls=known_urls,
            existing_titles=known_titles,
        )

        logger.info(
            "Scraping complete: %d total articles, %d unique after dedup",
            len(all_articles),
            len(unique_articles),
        )

        return unique_articles

    async def _scrape_source(
        self,
        *,
        source: NewsSource,
        existing_urls: set[str],
        max_articles: int,
    ) -> list[RawArticle]:
        """Scrape articles from a single source.

        Args:
            source: The news source to scrape.
            existing_urls: Set of known URLs for filtering.
            max_articles: Maximum number of articles to fetch.

        Returns:
            List of parsed articles from this source.
        """
        parser = PARSER_REGISTRY[source]

        # Fetch and parse the listing page
        links = await self._fetch_article_links(parser)
        if not links:
            logger.warning("No article links found for %s", source.value)
            return []

        # Filter out known URLs
        new_links = deduplicate_links(links, existing_urls)
        logger.info(
            "Found %d links for %s, %d are new",
            len(links),
            source.value,
            len(new_links),
        )

        # Limit the number of articles to fetch
        links_to_fetch = new_links[:max_articles]

        # Fetch and parse individual articles
        articles: list[RawArticle] = []
        for link in links_to_fetch:
            article = await self._fetch_article(parser, link)
            if article:
                articles.append(article)

        return articles

    async def _fetch_article_links(self, parser: BaseParser) -> list[ArticleLink]:
        """Fetch and parse the listing page for a parser's source.

        Args:
            parser: The parser whose listing page to fetch.

        Returns:
            List of discovered article links.
        """
        try:
            html = await self._http_client.fetch(parser.news_url)
            return parser.parse_article_list(html)
        except Exception:
            logger.error(
                "Failed to fetch listing page for %s: %s",
                parser.source.value,
                parser.news_url,
                exc_info=True,
            )
            return []

    async def _fetch_article(self, parser: BaseParser, link: ArticleLink) -> RawArticle | None:
        """Fetch and parse a single article.

        Args:
            parser: The parser to use for extraction.
            link: The article link to fetch.

        Returns:
            Parsed article, or None if fetching/parsing failed.
        """
        try:
            html = await self._http_client.fetch(link.url)
            return parser.parse_article(html, link.url)
        except Exception:
            logger.warning("Failed to fetch article %s", link.url, exc_info=True)
            return None

    async def close(self) -> None:
        """Close the HTTP client and release resources."""
        await self._http_client.close()
