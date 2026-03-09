"""Elasticsearch search service — full-text search with filters."""

import logging
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.core.elasticsearch import get_elasticsearch
from app.services.es_indexes import F1_ARTICLES_INDEX

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


class SearchFilters(BaseModel):
    """Optional structured filters for article search."""

    source: str | None = None
    tags: list[str] | None = None
    teams: list[str] | None = None
    drivers: list[str] | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None

    model_config = {"frozen": True}


class SearchHit(BaseModel):
    """A single search result with relevance score."""

    score: float
    source: dict[str, Any] = Field(description="The ES document _source")

    model_config = {"frozen": True}


class SearchResult(BaseModel):
    """Paginated search result envelope."""

    total: int
    hits: list[SearchHit]
    took_ms: int

    model_config = {"frozen": True}


# ---------------------------------------------------------------------------
# Query builder
# ---------------------------------------------------------------------------

# Fields searched for full-text queries, with boosting weights.
_TEXT_FIELDS = [
    "title^3",
    "title_kr^3",
    "content",
    "content_kr",
    "summary_en^2",
    "summary_kr^2",
]


def _build_query(
    query: str | None,
    filters: SearchFilters | None,
) -> dict[str, Any]:
    """Build an Elasticsearch bool query from text query and filters."""
    must: list[dict[str, Any]] = []
    filter_clauses: list[dict[str, Any]] = []

    # Full-text search
    if query:
        must.append(
            {
                "multi_match": {
                    "query": query,
                    "fields": _TEXT_FIELDS,
                    "type": "best_fields",
                    "fuzziness": "AUTO",
                },
            }
        )

    # Structured filters
    if filters:
        if filters.source:
            filter_clauses.append({"term": {"source": filters.source}})
        if filters.tags:
            filter_clauses.append({"terms": {"tags": filters.tags}})
        if filters.teams:
            filter_clauses.append({"terms": {"teams": filters.teams}})
        if filters.drivers:
            filter_clauses.append({"terms": {"drivers": filters.drivers}})
        if filters.date_from or filters.date_to:
            date_range: dict[str, str] = {}
            if filters.date_from:
                date_range["gte"] = filters.date_from.isoformat()
            if filters.date_to:
                date_range["lte"] = filters.date_to.isoformat()
            filter_clauses.append({"range": {"published_at": date_range}})

    # Assemble the bool query
    bool_query: dict[str, Any] = {}
    if must:
        bool_query["must"] = must
    if filter_clauses:
        bool_query["filter"] = filter_clauses

    # If neither text query nor filters are provided, match everything.
    if not bool_query:
        return {"match_all": {}}

    return {"bool": bool_query}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


async def search_articles(
    query: str | None = None,
    filters: SearchFilters | None = None,
    skip: int = 0,
    limit: int = 20,
) -> SearchResult:
    """Search articles in Elasticsearch.

    Args:
        query: Free-text search string (searches title, content, summary fields).
        filters: Optional structured filters (source, tags, teams, drivers, date range).
        skip: Number of results to skip (for pagination).
        limit: Maximum number of results to return.

    Returns:
        SearchResult with total count, matched articles, and query duration.
    """
    es = get_elasticsearch()

    es_query = _build_query(query, filters)

    # Default sort: by relevance when a text query is present,
    # by published_at descending otherwise.
    sort: list[dict[str, Any]] | None = None
    if not query:
        sort = [{"published_at": {"order": "desc", "missing": "_last"}}]

    body: dict[str, Any] = {
        "query": es_query,
        "from": skip,
        "size": limit,
    }
    if sort:
        body["sort"] = sort

    response = await es.search(index=F1_ARTICLES_INDEX, body=body)

    total_value = response["hits"]["total"]
    total = total_value["value"] if isinstance(total_value, dict) else total_value

    hits = [
        SearchHit(score=hit.get("_score", 0.0) or 0.0, source=hit["_source"])
        for hit in response["hits"]["hits"]
    ]

    return SearchResult(
        total=total,
        hits=hits,
        took_ms=response.get("took", 0),
    )
