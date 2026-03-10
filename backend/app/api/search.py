"""Full-text search API endpoints (Elasticsearch-backed)."""

from fastapi import APIRouter, Query

from app.services.es_search import SearchFilters, SearchResult, search_articles

router = APIRouter(prefix="/api/search", tags=["search"])


@router.get("", response_model=SearchResult)
async def full_text_search(
    q: str | None = Query(None, description="Free-text search query"),
    source: str | None = Query(None, description="Filter by source"),
    team: str | None = Query(None, description="Filter by team name"),
    driver: str | None = Query(None, description="Filter by driver name"),
    tag: str | None = Query(None, description="Filter by tag"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
) -> SearchResult:
    """Search articles using Elasticsearch full-text search with optional filters."""
    filters = SearchFilters(
        source=source,
        teams=[team] if team else None,
        drivers=[driver] if driver else None,
        tags=[tag] if tag else None,
    )
    skip = (page - 1) * limit
    return await search_articles(query=q, filters=filters, skip=skip, limit=limit)
