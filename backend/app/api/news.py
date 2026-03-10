"""News article REST API endpoints."""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.models.article import ArticleDocument
from app.services.repository import ArticleRepository

router = APIRouter(prefix="/api/news", tags=["news"])


class NewsListResponse(BaseModel):
    """Paginated news list response."""

    total: int
    page: int
    limit: int
    items: list[ArticleDocument]

    model_config = {"frozen": True}


@router.get("", response_model=NewsListResponse)
async def list_news(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    source: str | None = Query(None, description="Filter by source (e.g. formula1.com)"),
    team: str | None = Query(None, description="Filter by team name"),
    driver: str | None = Query(None, description="Filter by driver name"),
    tag: str | None = Query(None, description="Filter by tag"),
) -> NewsListResponse:
    """List news articles with optional filters and pagination."""
    filters: dict[str, str] = {}
    if source:
        filters["source"] = source
    if team:
        filters["teams"] = team
    if driver:
        filters["drivers"] = driver
    if tag:
        filters["tags"] = tag

    skip = (page - 1) * limit
    articles = await ArticleRepository.find_articles(
        filters=filters or None, skip=skip, limit=limit
    )
    total = await ArticleRepository.count_articles(filters=filters or None)

    return NewsListResponse(total=total, page=page, limit=limit, items=articles)


@router.get("/tags", response_model=dict)
async def get_tags() -> dict[str, list[str]]:
    """Return all unique tags, teams, and drivers from the articles collection."""
    return await ArticleRepository.get_distinct_tags()


@router.get("/{article_url:path}", response_model=ArticleDocument)
async def get_article(article_url: str) -> ArticleDocument:
    """Get a single news article by URL.

    The article URL is passed as a path parameter (URL-encoded).
    """
    article = await ArticleRepository.find_by_url(article_url)
    if article is None:
        raise HTTPException(status_code=404, detail=f"Article not found: {article_url}")
    return article
