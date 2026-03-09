"""Elasticsearch index management — called once on application startup."""

import logging

from elasticsearch import AsyncElasticsearch

from app.core.elasticsearch import get_elasticsearch

logger = logging.getLogger(__name__)

F1_ARTICLES_INDEX = "f1_articles"

# ---------------------------------------------------------------------------
# Index settings & mappings
# ---------------------------------------------------------------------------

F1_ARTICLES_SETTINGS: dict = {
    "number_of_shards": 1,
    "number_of_replicas": 0,
    "analysis": {
        "analyzer": {
            "korean": {
                "type": "custom",
                "tokenizer": "nori_tokenizer",
                "filter": ["lowercase"],
            },
        },
    },
}

# Fallback settings when the nori plugin is not installed.
F1_ARTICLES_SETTINGS_FALLBACK: dict = {
    "number_of_shards": 1,
    "number_of_replicas": 0,
}

F1_ARTICLES_MAPPINGS: dict = {
    "properties": {
        "title": {
            "type": "text",
            "analyzer": "english",
            "fields": {"keyword": {"type": "keyword", "ignore_above": 512}},
        },
        "title_kr": {"type": "text", "analyzer": "korean"},
        "content": {"type": "text", "analyzer": "english"},
        "content_kr": {"type": "text", "analyzer": "korean"},
        "summary_en": {"type": "text", "analyzer": "english"},
        "summary_kr": {"type": "text", "analyzer": "korean"},
        "source": {"type": "keyword"},
        "author": {"type": "keyword"},
        "url": {"type": "keyword"},
        "published_at": {"type": "date"},
        "created_at": {"type": "date"},
        "tags": {"type": "keyword"},
        "teams": {"type": "keyword"},
        "drivers": {"type": "keyword"},
        "image_url": {"type": "keyword", "index": False, "doc_values": False},
        "fingerprint": {"type": "keyword"},
    },
}

# Fallback mappings using standard analyzer instead of nori for Korean fields.
F1_ARTICLES_MAPPINGS_FALLBACK: dict = {
    "properties": {
        **F1_ARTICLES_MAPPINGS["properties"],
        "title_kr": {"type": "text", "analyzer": "standard"},
        "content_kr": {"type": "text", "analyzer": "standard"},
        "summary_kr": {"type": "text", "analyzer": "standard"},
    },
}


# ---------------------------------------------------------------------------
# Public functions
# ---------------------------------------------------------------------------


async def _nori_available(es: AsyncElasticsearch) -> bool:
    """Check whether the nori analysis plugin is installed."""
    try:
        plugins = await es.cat.plugins(format="json")
        return any(p.get("component") == "analysis-nori" for p in plugins)
    except Exception:
        return False


async def ensure_es_indexes() -> None:
    """Create the f1_articles index if it does not already exist.

    Safe to call multiple times — skips creation when the index is present.
    Uses the nori analyzer for Korean fields when the plugin is available,
    otherwise falls back to the standard analyzer.
    """
    es = get_elasticsearch()

    exists = await es.indices.exists(index=F1_ARTICLES_INDEX)
    if exists:
        logger.info("Elasticsearch index '%s' already exists — skipping", F1_ARTICLES_INDEX)
        return

    use_nori = await _nori_available(es)
    if use_nori:
        settings = F1_ARTICLES_SETTINGS
        mappings = F1_ARTICLES_MAPPINGS
        logger.info("Nori plugin detected — using Korean analyzer for '%s'", F1_ARTICLES_INDEX)
    else:
        settings = F1_ARTICLES_SETTINGS_FALLBACK
        mappings = F1_ARTICLES_MAPPINGS_FALLBACK
        logger.warning(
            "Nori plugin not found — falling back to standard analyzer for Korean fields"
        )

    await es.indices.create(
        index=F1_ARTICLES_INDEX,
        settings=settings,
        mappings=mappings,
    )
    logger.info("Created Elasticsearch index '%s'", F1_ARTICLES_INDEX)


async def delete_es_index(index_name: str) -> None:
    """Delete an Elasticsearch index by name. For admin/testing use."""
    es = get_elasticsearch()
    exists = await es.indices.exists(index=index_name)
    if not exists:
        logger.warning("Index '%s' does not exist — nothing to delete", index_name)
        return
    await es.indices.delete(index=index_name)
    logger.info("Deleted Elasticsearch index '%s'", index_name)
