"""Deduplication logic for scraped articles.

Uses URL-based exact matching and title similarity (Jaccard) to detect duplicates.
"""

import re

from app.models.article import ArticleLink, RawArticle

# Minimum Jaccard similarity threshold to consider two titles as duplicates
TITLE_SIMILARITY_THRESHOLD: float = 0.7


def normalize_url(url: str) -> str:
    """Normalize a URL for deduplication comparison.

    Strips trailing slashes, fragments, and common tracking parameters.

    Args:
        url: The URL to normalize.

    Returns:
        Normalized URL string.
    """
    # Remove fragment
    url = url.split("#")[0]
    # Remove trailing slash
    url = url.rstrip("/")
    # Lowercase for comparison
    return url.lower()


def _tokenize(text: str) -> set[str]:
    """Tokenize a title into lowercase word tokens.

    Strips punctuation and common stop words to focus on meaningful terms.
    """
    # Remove punctuation, lowercase, split into words
    words = re.findall(r"[a-z0-9]+", text.lower())
    # Remove very short tokens that add noise
    return {w for w in words if len(w) > 2}


def jaccard_similarity(title_a: str, title_b: str) -> float:
    """Compute Jaccard similarity between two title strings.

    Args:
        title_a: First title.
        title_b: Second title.

    Returns:
        Jaccard similarity score between 0.0 and 1.0.
    """
    tokens_a = _tokenize(title_a)
    tokens_b = _tokenize(title_b)

    if not tokens_a or not tokens_b:
        return 0.0

    intersection = tokens_a & tokens_b
    union = tokens_a | tokens_b
    return len(intersection) / len(union)


def is_duplicate_title(
    title: str,
    existing_titles: list[str],
    threshold: float = TITLE_SIMILARITY_THRESHOLD,
) -> bool:
    """Check if a title is similar to any existing title.

    Args:
        title: The new title to check.
        existing_titles: List of already-seen titles.
        threshold: Jaccard similarity threshold (default 0.7).

    Returns:
        True if the title is considered a duplicate.
    """
    for existing in existing_titles:
        if jaccard_similarity(title, existing) >= threshold:
            return True
    return False


def deduplicate_links(
    new_links: list[ArticleLink],
    existing_urls: set[str],
) -> list[ArticleLink]:
    """Filter out article links whose URLs are already known.

    Args:
        new_links: Newly scraped article links.
        existing_urls: Set of already-known normalized URLs.

    Returns:
        List of links not present in existing_urls.
    """
    unique: list[ArticleLink] = []
    seen: set[str] = set()

    for link in new_links:
        normalized = normalize_url(link.url)
        if normalized not in existing_urls and normalized not in seen:
            seen.add(normalized)
            unique.append(link)

    return unique


def deduplicate_articles(
    articles: list[RawArticle],
    existing_urls: set[str],
    existing_titles: list[str],
    *,
    title_threshold: float = TITLE_SIMILARITY_THRESHOLD,
) -> list[RawArticle]:
    """Remove duplicate articles by URL and title similarity.

    Args:
        articles: List of newly scraped articles.
        existing_urls: Set of already-known normalized URLs.
        existing_titles: List of already-known article titles.
        title_threshold: Jaccard similarity threshold for title matching.

    Returns:
        List of non-duplicate articles.
    """
    unique: list[RawArticle] = []
    seen_urls: set[str] = set()
    all_titles = list(existing_titles)

    for article in articles:
        normalized_url = normalize_url(article.url)

        # URL-based dedup
        if normalized_url in existing_urls or normalized_url in seen_urls:
            continue

        # Title similarity dedup
        if is_duplicate_title(article.title, all_titles, threshold=title_threshold):
            continue

        seen_urls.add(normalized_url)
        all_titles.append(article.title)
        unique.append(article)

    return unique
