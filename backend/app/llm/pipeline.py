"""Summary pipeline — orchestrates batch summarization, persistence, and indexing."""

from __future__ import annotations

import logging

from pydantic import BaseModel

from app.llm.summarizer import summarize_batch
from app.models.article import ArticleDocument
from app.services.es_indexer import index_article
from app.services.repository import ArticleRepository

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Result model
# ---------------------------------------------------------------------------


class PipelineSummaryResult(BaseModel):
    """Statistics returned after a summary pipeline run."""

    total: int = 0
    succeeded: int = 0
    failed: int = 0
    skipped: int = 0

    model_config = {"frozen": True}


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------


async def run_summary_pipeline(
    limit: int = 50,
    concurrency: int = 3,
) -> PipelineSummaryResult:
    """Fetch unsummarized articles, generate summaries, and persist results.

    Steps:
      1. Query MongoDB for articles missing ``summary_en``.
      2. Run batch summarization via :func:`summarize_batch`.
      3. Save each successful summary back to MongoDB.
      4. Re-index updated articles into Elasticsearch.
      5. Return aggregate statistics.
    """
    # 1. Fetch articles that need summarization
    articles = await ArticleRepository.find_articles(
        filters={"summary_en": None},
        limit=limit,
    )

    if not articles:
        logger.info("No unsummarized articles found")
        return PipelineSummaryResult()

    logger.info("Starting summary pipeline for %d article(s)", len(articles))

    # 2. Generate summaries in batch
    results = await summarize_batch(articles, concurrency=concurrency)

    # Build a lookup from URL to article for later re-indexing
    article_by_url: dict[str, ArticleDocument] = {a.url: a for a in articles}

    succeeded = 0
    failed = 0
    skipped = 0

    # 3 & 4. Persist and index
    for url, summary in results:
        if summary is None:
            failed += 1
            continue

        article = article_by_url.get(url)
        if article is None:
            skipped += 1
            continue

        # 3. Update MongoDB
        try:
            await ArticleRepository.update_article(
                url=url,
                update_fields={
                    "summary_en": summary,
                    "is_summarized": True,
                },
            )
        except Exception:
            logger.exception("Failed to update article in MongoDB: %s", url)
            failed += 1
            continue

        # 4. Re-index into Elasticsearch with the new summary
        updated_article = article.model_copy(
            update={"summary_en": summary, "is_summarized": True},
        )
        try:
            await index_article(updated_article)
        except Exception:
            logger.exception("Failed to index article in ES: %s", url)
            # The MongoDB write succeeded, so still count as succeeded
            succeeded += 1
            continue

        succeeded += 1

    result = PipelineSummaryResult(
        total=len(articles),
        succeeded=succeeded,
        failed=failed,
        skipped=skipped,
    )
    logger.info(
        "Summary pipeline complete — total=%d succeeded=%d failed=%d skipped=%d",
        result.total,
        result.succeeded,
        result.failed,
        result.skipped,
    )
    return result
