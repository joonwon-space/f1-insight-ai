"""Parser for formula1.com news articles."""

import logging
from datetime import datetime
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag

from app.models.article import ArticleLink, NewsSource, RawArticle
from app.scraper.parsers.base import BaseParser

logger = logging.getLogger(__name__)

BASE_URL = "https://www.formula1.com"
NEWS_URL = f"{BASE_URL}/en/latest/all"


class Formula1Parser(BaseParser):
    """Parser for formula1.com news listing and article pages."""

    @property
    def source(self) -> NewsSource:
        return NewsSource.FORMULA1

    @property
    def news_url(self) -> str:
        return NEWS_URL

    def parse_article_list(self, html: str) -> list[ArticleLink]:
        """Extract article links from the formula1.com latest news page."""
        soup = BeautifulSoup(html, "html.parser")
        links: list[ArticleLink] = []

        # formula1.com uses various link patterns for news articles
        for anchor in soup.select("a[href*='/en/latest/']"):
            try:
                href = anchor.get("href", "")
                if not isinstance(href, str) or not href:
                    continue

                url = urljoin(BASE_URL, href)

                # Skip listing pages and non-article URLs
                if url.rstrip("/") == NEWS_URL.rstrip("/"):
                    continue

                title = self._extract_link_title(anchor)
                if not title:
                    continue

                links.append(ArticleLink(url=url, title=title, source=self.source))
            except Exception:
                logger.warning("Failed to parse article link on formula1.com", exc_info=True)
                continue

        return _deduplicate_links(links)

    def parse_article(self, html: str, url: str) -> RawArticle | None:
        """Extract article content from a formula1.com article page."""
        try:
            soup = BeautifulSoup(html, "html.parser")

            title = self._extract_title(soup)
            if not title:
                logger.warning("No title found for formula1.com article: %s", url)
                return None

            content = self._extract_content(soup)
            if not content:
                logger.warning("No content found for formula1.com article: %s", url)
                return None

            return RawArticle(
                url=url,
                title=title,
                content=content,
                source=self.source,
                published_at=self._extract_date(soup),
                author=self._extract_author(soup),
                image_url=self._extract_image(soup),
                tags=self._extract_tags(soup),
            )
        except Exception:
            logger.warning("Failed to parse formula1.com article: %s", url, exc_info=True)
            return None

    def _extract_link_title(self, anchor: Tag) -> str:
        """Extract title text from an anchor element or its children."""
        # Try direct text content
        text = anchor.get_text(strip=True)
        if text and len(text) > 10:
            return text

        # Try heading elements inside the anchor
        for heading in anchor.find_all(["h2", "h3", "h4", "span"]):
            heading_text = heading.get_text(strip=True)
            if heading_text and len(heading_text) > 10:
                return heading_text

        return text if text else ""

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract article title from the page."""
        # Try og:title meta tag first (most reliable)
        og_title = soup.find("meta", property="og:title")
        if og_title and isinstance(og_title, Tag):
            content = og_title.get("content", "")
            if isinstance(content, str) and content:
                return content.strip()

        # Try h1 tag
        h1 = soup.find("h1")
        if h1:
            return h1.get_text(strip=True)

        return ""

    def _extract_content(self, soup: BeautifulSoup) -> str:
        """Extract article body text."""
        # formula1.com article body selectors
        selectors = [
            "div.f1-article--body",
            "article .body",
            "div[class*='article-body']",
            "article",
        ]

        for selector in selectors:
            body = soup.select_one(selector)
            if body:
                # Remove script/style elements
                for tag in body.find_all(["script", "style", "nav", "aside"]):
                    tag.decompose()
                text = body.get_text(separator="\n", strip=True)
                if len(text) > 100:
                    return text

        return ""

    def _extract_date(self, soup: BeautifulSoup) -> datetime | None:
        """Extract publication date."""
        # Try meta tags
        for prop in ["article:published_time", "datePublished"]:
            meta = soup.find("meta", property=prop) or soup.find("meta", attrs={"name": prop})
            if meta and isinstance(meta, Tag):
                content = meta.get("content", "")
                if isinstance(content, str) and content:
                    return _parse_iso_date(content)

        # Try time element
        time_el = soup.find("time")
        if time_el and isinstance(time_el, Tag):
            dt_attr = time_el.get("datetime", "")
            if isinstance(dt_attr, str) and dt_attr:
                return _parse_iso_date(dt_attr)

        return None

    def _extract_author(self, soup: BeautifulSoup) -> str | None:
        """Extract author name."""
        meta = soup.find("meta", attrs={"name": "author"})
        if meta and isinstance(meta, Tag):
            content = meta.get("content", "")
            if isinstance(content, str) and content:
                return content.strip()
        return None

    def _extract_image(self, soup: BeautifulSoup) -> str | None:
        """Extract the main article image URL."""
        og_image = soup.find("meta", property="og:image")
        if og_image and isinstance(og_image, Tag):
            content = og_image.get("content", "")
            if isinstance(content, str) and content:
                return content.strip()
        return None

    def _extract_tags(self, soup: BeautifulSoup) -> list[str]:
        """Extract article tags/keywords."""
        meta = soup.find("meta", attrs={"name": "keywords"})
        if meta and isinstance(meta, Tag):
            content = meta.get("content", "")
            if isinstance(content, str) and content:
                return [t.strip() for t in content.split(",") if t.strip()]
        return []


def _parse_iso_date(date_str: str) -> datetime | None:
    """Parse an ISO 8601 date string, returning None on failure."""
    try:
        return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        logger.debug("Could not parse date: %s", date_str)
        return None


def _deduplicate_links(links: list[ArticleLink]) -> list[ArticleLink]:
    """Remove duplicate links by URL."""
    seen: set[str] = set()
    unique: list[ArticleLink] = []
    for link in links:
        normalized = link.url.rstrip("/")
        if normalized not in seen:
            seen.add(normalized)
            unique.append(link)
    return unique
