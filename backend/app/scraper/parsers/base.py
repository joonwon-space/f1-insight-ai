"""Abstract base class for news site parsers."""

from abc import ABC, abstractmethod

from app.models.article import ArticleLink, NewsSource, RawArticle


class BaseParser(ABC):
    """Base parser interface for F1 news sites.

    Each news source must implement a concrete parser that extracts
    article links from listing pages and article content from detail pages.
    """

    @property
    @abstractmethod
    def source(self) -> NewsSource:
        """The news source this parser handles."""

    @property
    @abstractmethod
    def news_url(self) -> str:
        """The URL of the news listing page to scrape."""

    @abstractmethod
    def parse_article_list(self, html: str) -> list[ArticleLink]:
        """Extract article links from a news listing page.

        Args:
            html: Raw HTML of the listing page.

        Returns:
            List of article links found on the page.
        """

    @abstractmethod
    def parse_article(self, html: str, url: str) -> RawArticle | None:
        """Extract article content from an individual article page.

        Args:
            html: Raw HTML of the article page.
            url: The URL the HTML was fetched from.

        Returns:
            Parsed article, or None if parsing failed.
        """
