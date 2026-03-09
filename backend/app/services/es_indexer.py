"""Elasticsearch document indexing — index ArticleDocuments into ES."""

import hashlib
import logging
from typing import Any

from elasticsearch.helpers import async_bulk

from app.core.elasticsearch import get_elasticsearch
from app.models.article import ArticleDocument
from app.services.es_indexes import F1_ARTICLES_INDEX

logger = logging.getLogger(__name__)


def generate_fingerprint(title: str, source: str) -> str:
    """Generate a deduplication fingerprint from title and source.

    Uses SHA-256 truncated to 16 hex characters for compact storage
    while retaining sufficient collision resistance.
    """
    raw = f"{title.strip().lower()}|{source.strip().lower()}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def _article_to_es_doc(article: ArticleDocument) -> dict[str, Any]:
    """Flatten an ArticleDocument into the Elasticsearch document format."""
    return {
        "url": article.url,
        "title": article.title,
        "title_kr": None,  # populated later by translation pipeline
        "content": article.content,
        "content_kr": None,
        "summary_en": article.summary_en,
        "summary_kr": article.summary_ko,
        "source": str(article.source),
        "author": article.author,
        "published_at": (article.published_at.isoformat() if article.published_at else None),
        "created_at": article.scraped_at.isoformat(),
        "tags": article.tags,
        "teams": article.teams,
        "drivers": article.drivers,
        "image_url": str(article.image_url) if article.image_url else None,
        "fingerprint": generate_fingerprint(article.title, str(article.source)),
    }


async def index_article(article: ArticleDocument) -> None:
    """Index a single article into Elasticsearch.

    Uses the fingerprint as the document ID so re-indexing the same
    article overwrites rather than duplicates.
    """
    es = get_elasticsearch()
    doc = _article_to_es_doc(article)
    doc_id = doc["fingerprint"]

    await es.index(index=F1_ARTICLES_INDEX, id=doc_id, document=doc)
    logger.debug("Indexed article '%s' (id=%s)", article.title[:60], doc_id)


async def bulk_index_articles(articles: list[ArticleDocument]) -> int:
    """Bulk-index multiple articles into Elasticsearch.

    Returns the number of successfully indexed documents.
    """
    if not articles:
        return 0

    es = get_elasticsearch()

    actions: list[dict[str, Any]] = []
    for article in articles:
        doc = _article_to_es_doc(article)
        actions.append(
            {
                "_index": F1_ARTICLES_INDEX,
                "_id": doc["fingerprint"],
                "_source": doc,
            }
        )

    success_count, errors = await async_bulk(es, actions, raise_on_error=False)
    if errors:
        logger.warning("Bulk indexing completed with %d error(s)", len(errors))
        for err in errors[:5]:
            logger.warning("  Bulk error: %s", err)
    else:
        logger.info("Bulk-indexed %d articles into '%s'", success_count, F1_ARTICLES_INDEX)

    return success_count
