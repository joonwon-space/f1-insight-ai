"""RSS feed parser using feedparser library.

Converts RSS/Atom feed entries to RawArticle objects.
feedparser handles the XML parsing, date normalization, and encoding.
"""

import logging
import re
import time
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

import feedparser

from app.models.article import NewsSource, RawArticle

logger = logging.getLogger(__name__)

# Maximum content length to store from RSS description (characters)
MAX_CONTENT_LENGTH = 2000


def _parse_date(entry: feedparser.FeedParserDict) -> datetime | None:
    """Extract and parse the publication date from a feed entry.

    Tries published_parsed, updated_parsed, then raw string fields.
    Always returns timezone-aware UTC datetime or None.
    """
    # feedparser normalizes dates to time.struct_time in UTC
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        try:
            ts = time.mktime(entry.published_parsed)
            return datetime.fromtimestamp(ts, tz=timezone.utc)
        except Exception:
            pass

    if hasattr(entry, "updated_parsed") and entry.updated_parsed:
        try:
            ts = time.mktime(entry.updated_parsed)
            return datetime.fromtimestamp(ts, tz=timezone.utc)
        except Exception:
            pass

    # Try raw string date
    for field in ("published", "updated"):
        raw = getattr(entry, field, None)
        if raw:
            try:
                return parsedate_to_datetime(raw)
            except Exception:
                pass

    return None


def _strip_html(text: str) -> str:
    """Remove HTML tags and normalize whitespace."""
    clean = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", clean).strip()


def _extract_content(entry: feedparser.FeedParserDict) -> str:
    """Extract the best available content from a feed entry.

    Priority: content[0].value > summary > title
    Strips HTML tags using simple regex after feedparser sanitization.
    """
    # feedparser may provide content with HTML
    content_list = getattr(entry, "content", [])
    if content_list:
        raw = content_list[0].get("value", "")
        if raw:
            return _strip_html(raw)[:MAX_CONTENT_LENGTH]

    # Fall back to summary
    summary = getattr(entry, "summary", "") or ""
    if summary:
        return _strip_html(summary)[:MAX_CONTENT_LENGTH]

    # Last resort: title only
    return getattr(entry, "title", "") or ""


def _extract_image_url(entry: feedparser.FeedParserDict) -> str | None:
    """Extract the first image URL from a feed entry if available."""
    # Check media:content (common in F1 official feed)
    media_content = getattr(entry, "media_content", [])
    if media_content:
        for media in media_content:
            url = media.get("url", "")
            if url and any(url.lower().endswith(ext) for ext in (".jpg", ".jpeg", ".png", ".webp")):
                return url

    # Check enclosures
    enclosures = getattr(entry, "enclosures", [])
    for enc in enclosures:
        mime = enc.get("type", "")
        if mime.startswith("image/"):
            return enc.get("href") or enc.get("url")

    return None


def parse_feed(feed_url: str, source: NewsSource, raw_feed: str) -> list[RawArticle]:
    """Parse a raw RSS/Atom feed string into RawArticle objects.

    Args:
        feed_url: The URL the feed was fetched from (for logging).
        source: The NewsSource enum value.
        raw_feed: The raw XML/RSS content as a string.

    Returns:
        List of RawArticle objects parsed from the feed entries.
    """
    parsed = feedparser.parse(raw_feed)

    if parsed.bozo:
        # bozo flag = feed has errors, but feedparser may still parse it
        logger.warning("Feed %s has format issues (bozo): %s", feed_url, parsed.bozo_exception)

    articles: list[RawArticle] = []

    for entry in parsed.entries:
        # URL is the unique identifier
        url = getattr(entry, "link", None) or getattr(entry, "id", None)
        if not url:
            logger.debug("Skipping RSS entry with no URL from %s", feed_url)
            continue

        title = getattr(entry, "title", "").strip()
        if not title:
            logger.debug("Skipping RSS entry with no title from %s", feed_url)
            continue

        content = _extract_content(entry)
        published_at = _parse_date(entry)
        image_url = _extract_image_url(entry)

        # Extract author
        author: str | None = None
        author_detail = getattr(entry, "author_detail", None)
        if author_detail:
            author = author_detail.get("name")
        if not author:
            author = getattr(entry, "author", None)

        # Extract tags from categories
        tags: list[str] = []
        for tag_obj in getattr(entry, "tags", []):
            term = tag_obj.get("term", "")
            if term:
                tags.append(term.lower().strip())

        try:
            article = RawArticle(
                url=url,
                title=title,
                content=content,
                source=source,
                published_at=published_at,
                author=author,
                image_url=image_url,
                tags=tags,
            )
            articles.append(article)
        except Exception:
            logger.warning("Failed to create RawArticle from RSS entry: %s", url, exc_info=True)
            continue

    logger.info("Parsed %d articles from RSS feed %s", len(articles), feed_url)
    return articles
