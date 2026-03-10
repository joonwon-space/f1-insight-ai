"""Unsplash API integration for copyright-free image search.

Uses the Unsplash API to find relevant F1 images for news articles.
Images from Unsplash are free to use commercially (important for YouTube).
"""

import logging

import httpx
from pydantic import BaseModel

from app.core.config import get_settings

logger = logging.getLogger(__name__)

UNSPLASH_API_BASE = "https://api.unsplash.com"
UNSPLASH_SEARCH_PER_PAGE = 5


class UnsplashImage(BaseModel):
    """A single Unsplash image result."""

    id: str
    url: str  # Regular size URL
    thumb_url: str
    description: str | None = None
    alt_text: str | None = None
    photographer: str
    photographer_url: str
    download_location: str  # Must be called to attribute the download

    model_config = {"frozen": True}


class UnsplashSearchResult(BaseModel):
    """Paginated Unsplash search results."""

    total: int
    total_pages: int
    images: list[UnsplashImage]

    model_config = {"frozen": True}


def _build_headers() -> dict[str, str]:
    """Build Unsplash API request headers with authorization."""
    settings = get_settings()
    return {
        "Authorization": f"Client-ID {settings.unsplash_access_key}",
        "Accept-Version": "v1",
    }


async def search_images(
    query: str,
    *,
    page: int = 1,
    per_page: int = UNSPLASH_SEARCH_PER_PAGE,
    orientation: str = "landscape",
) -> UnsplashSearchResult | None:
    """Search Unsplash for images matching a query.

    Args:
        query: Search keywords (e.g. "Formula 1 race car").
        page: Page number for pagination.
        per_page: Number of results per page (max 30).
        orientation: Image orientation filter ("landscape", "portrait", "squarish").

    Returns:
        UnsplashSearchResult or None if API key is not configured / request fails.
    """
    settings = get_settings()
    if not settings.unsplash_access_key:
        logger.warning("UNSPLASH_ACCESS_KEY not configured — skipping image search")
        return None

    params = {
        "query": query,
        "page": page,
        "per_page": min(per_page, 30),
        "orientation": orientation,
        "content_filter": "high",  # family-safe content only
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{UNSPLASH_API_BASE}/search/photos",
                params=params,
                headers=_build_headers(),
            )
            response.raise_for_status()
    except httpx.HTTPError as exc:
        logger.error("Unsplash API request failed: %s", exc)
        return None

    data = response.json()
    images: list[UnsplashImage] = []

    for result in data.get("results", []):
        try:
            urls = result.get("urls", {})
            user = result.get("user", {})
            images.append(
                UnsplashImage(
                    id=result["id"],
                    url=urls.get("regular", urls.get("full", "")),
                    thumb_url=urls.get("thumb", ""),
                    description=result.get("description") or result.get("alt_description"),
                    alt_text=result.get("alt_description"),
                    photographer=user.get("name", "Unknown"),
                    photographer_url=user.get("links", {}).get("html", ""),
                    download_location=result.get("links", {}).get("download_location", ""),
                )
            )
        except (KeyError, ValueError):
            logger.debug("Skipping malformed Unsplash result: %s", result.get("id"))
            continue

    return UnsplashSearchResult(
        total=data.get("total", 0),
        total_pages=data.get("total_pages", 0),
        images=images,
    )


async def get_article_image(keywords: list[str]) -> UnsplashImage | None:
    """Get the best matching image for a news article.

    Searches Unsplash with F1-specific keywords added to improve relevance.
    Returns the first result, or None if no images found.

    Args:
        keywords: List of article-specific keywords (team, driver, topic).

    Returns:
        Best matching UnsplashImage, or None.
    """
    # Build query: combine F1 context with article keywords
    base_terms = ["Formula 1", "F1"]
    search_terms = base_terms + [k for k in keywords if k]
    query = " ".join(search_terms[:4])  # Limit to 4 terms for best results

    result = await search_images(query, per_page=3)
    if result and result.images:
        return result.images[0]

    # Fallback: search with just "Formula 1"
    fallback = await search_images("Formula 1 racing", per_page=1)
    if fallback and fallback.images:
        return fallback.images[0]

    return None
