"""Pipelines — orchestrate batch summarization, translation, persistence, and indexing."""

from __future__ import annotations

import logging

from pydantic import BaseModel

from app.llm.summarizer import summarize_batch
from app.llm.translator import translate_batch
from app.models.article import ArticleDocument
from app.services.es_indexer import index_article
from app.services.repository import ArticleRepository

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Result models
# ---------------------------------------------------------------------------


class PipelineSummaryResult(BaseModel):
    """Statistics returned after a summary pipeline run."""

    total: int = 0
    succeeded: int = 0
    failed: int = 0
    skipped: int = 0

    model_config = {"frozen": True}


class PipelineTranslationResult(BaseModel):
    """Statistics returned after a translation pipeline run."""

    total: int = 0
    succeeded: int = 0
    failed: int = 0
    skipped: int = 0

    model_config = {"frozen": True}


class PipelineFullResult(BaseModel):
    """Combined statistics from running both summary and translation pipelines."""

    summary: PipelineSummaryResult
    translation: PipelineTranslationResult

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


# ---------------------------------------------------------------------------
# Translation pipeline
# ---------------------------------------------------------------------------


async def run_translation_pipeline(
    limit: int = 50,
    concurrency: int = 3,
) -> PipelineTranslationResult:
    """Fetch articles with English summaries but no Korean translation, translate, and persist.

    Steps:
      1. Query MongoDB for articles that have ``summary_en`` but missing ``summary_ko``.
      2. Run batch translation via :func:`translate_batch`.
      3. Save each successful translation back to MongoDB.
      4. Re-index updated articles into Elasticsearch.
      5. Return aggregate statistics.
    """
    # 1. Fetch articles that need translation
    articles = await ArticleRepository.find_articles(
        filters={
            "summary_en": {"$ne": None},
            "summary_ko": None,
        },
        limit=limit,
    )

    if not articles:
        logger.info("No articles needing translation found")
        return PipelineTranslationResult()

    logger.info("Starting translation pipeline for %d article(s)", len(articles))

    # 2. Generate translations in batch
    results = await translate_batch(articles, concurrency=concurrency)

    # Build a lookup from URL to article for later re-indexing
    article_by_url: dict[str, ArticleDocument] = {a.url: a for a in articles}

    succeeded = 0
    failed = 0
    skipped = 0

    # 3 & 4. Persist and index
    for url, translation in results:
        if translation is None:
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
                update_fields={"summary_ko": translation},
            )
        except Exception:
            logger.exception("Failed to update translation in MongoDB: %s", url)
            failed += 1
            continue

        # 4. Re-index into Elasticsearch with the new translation
        updated_article = article.model_copy(
            update={"summary_ko": translation},
        )
        try:
            await index_article(updated_article)
        except Exception:
            logger.exception("Failed to index translated article in ES: %s", url)
            # The MongoDB write succeeded, so still count as succeeded
            succeeded += 1
            continue

        succeeded += 1

    result = PipelineTranslationResult(
        total=len(articles),
        succeeded=succeeded,
        failed=failed,
        skipped=skipped,
    )
    logger.info(
        "Translation pipeline complete — total=%d succeeded=%d failed=%d skipped=%d",
        result.total,
        result.succeeded,
        result.failed,
        result.skipped,
    )
    return result


# ---------------------------------------------------------------------------
# Full pipeline (summary + translation)
# ---------------------------------------------------------------------------


async def run_full_pipeline(
    limit: int = 50,
    concurrency: int = 3,
) -> PipelineFullResult:
    """Run the summary pipeline followed by the translation pipeline.

    Executes both pipelines sequentially so that articles summarized in the
    first step are immediately available for translation in the second step.
    """
    logger.info("Starting full pipeline (summary + translation)")

    summary_result = await run_summary_pipeline(limit=limit, concurrency=concurrency)
    translation_result = await run_translation_pipeline(limit=limit, concurrency=concurrency)

    return PipelineFullResult(
        summary=summary_result,
        translation=translation_result,
    )
