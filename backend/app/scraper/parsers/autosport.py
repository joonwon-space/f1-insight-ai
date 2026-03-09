"""Parser for autosport.com news articles."""

import logging
from datetime import datetime
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag

from app.models.article import ArticleLink, NewsSource, RawArticle
from app.scraper.parsers.base import BaseParser

logger = logging.getLogger(__name__)

BASE_URL = "https://www.autosport.com"
NEWS_URL = f"{BASE_URL}/f1/news"


class AutosportParser(BaseParser):
    """Parser for autosport.com F1 news pages."""

    @property
    def source(self) -> NewsSource:
        return NewsSource.AUTOSPORT

    @property
    def news_url(self) -> str:
        return NEWS_URL

    def parse_article_list(self, html: str) -> list[ArticleLink]:
        """Extract article links from the autosport.com F1 news page."""
        soup = BeautifulSoup(html, "html.parser")
        links: list[ArticleLink] = []

        # autosport.com uses article cards and listing links
        for anchor in soup.select("a[href*='/f1/news/'], a[href*='/news/'], article a[href]"):
            try:
                href = anchor.get("href", "")
                if not isinstance(href, str) or not href:
                    continue

                url = urljoin(BASE_URL, href)

                # Only include URLs that look like articles
                if "/news/" not in url:
                    continue

                # Skip the listing page itself
                if url.rstrip("/") == NEWS_URL.rstrip("/"):
                    continue

                title = _extract_link_title(anchor)
                if not title:
                    continue

                links.append(ArticleLink(url=url, title=title, source=self.source))
            except Exception:
                logger.warning("Failed to parse article link on autosport.com", exc_info=True)
                continue

        return _deduplicate_links(links)

    def parse_article(self, html: str, url: str) -> RawArticle | None:
        """Extract article content from an autosport.com article page."""
        try:
            soup = BeautifulSoup(html, "html.parser")

            title = self._extract_title(soup)
            if not title:
                logger.warning("No title found for autosport.com article: %s", url)
                return None

            content = self._extract_content(soup)
            if not content:
                logger.warning("No content found for autosport.com article: %s", url)
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
            logger.warning("Failed to parse autosport.com article: %s", url, exc_info=True)
            return None

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract article title."""
        og_title = soup.find("meta", property="og:title")
        if og_title and isinstance(og_title, Tag):
            content = og_title.get("content", "")
            if isinstance(content, str) and content:
                return content.strip()

        h1 = soup.find("h1")
        if h1:
            return h1.get_text(strip=True)

        return ""

    def _extract_content(self, soup: BeautifulSoup) -> str:
        """Extract article body text."""
        selectors = [
            "div.article-body",
            "div.ms-article-body",
            "div[class*='ArticleBody']",
            "div.entry-content",
            "article .content",
            "article",
        ]

        for selector in selectors:
            body = soup.select_one(selector)
            if body:
                for tag in body.find_all(["script", "style", "nav", "aside", "figure"]):
                    tag.decompose()
                text = body.get_text(separator="\n", strip=True)
                if len(text) > 100:
                    return text

        return ""

    def _extract_date(self, soup: BeautifulSoup) -> datetime | None:
        """Extract publication date."""
        for prop in ["article:published_time", "datePublished"]:
            meta = soup.find("meta", property=prop) or soup.find("meta", attrs={"name": prop})
            if meta and isinstance(meta, Tag):
                content = meta.get("content", "")
                if isinstance(content, str) and content:
                    return _parse_iso_date(content)

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

        author_el = soup.select_one(".author-name, [rel='author'], .byline")
        if author_el:
            return author_el.get_text(strip=True) or None

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


def _extract_link_title(anchor: Tag) -> str:
    """Extract title text from an anchor tag."""
    text = anchor.get_text(strip=True)
    if text and len(text) > 10:
        return text

    for heading in anchor.find_all(["h2", "h3", "h4", "span"]):
        heading_text = heading.get_text(strip=True)
        if heading_text and len(heading_text) > 10:
            return heading_text

    return text if text else ""


def _parse_iso_date(date_str: str) -> datetime | None:
    """Parse an ISO 8601 date string."""
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
