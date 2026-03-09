"""Pipelines — orchestrate batch summarization, translation, persistence, and indexing."""

from __future__ import annotations

import logging

from pydantic import BaseModel

from app.llm.summarizer import summarize_batch
from app.llm.tagger import tag_batch
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


class PipelineTaggingResult(BaseModel):
    """Statistics returned after a tagging pipeline run."""

    total: int = 0
    succeeded: int = 0
    failed: int = 0

    model_config = {"frozen": True}


class PipelineFullResult(BaseModel):
    """Combined statistics from running summary, translation, and tagging pipelines."""

    summary: PipelineSummaryResult
    translation: PipelineTranslationResult
    tagging: PipelineTaggingResult | None = None

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
# Tagging pipeline
# ---------------------------------------------------------------------------


async def run_tagging_pipeline(
    limit: int = 100,
    concurrency: int = 5,
) -> PipelineTaggingResult:
    """Fetch untagged articles, apply rule-based tagging, and persist results.

    Steps:
      1. Query MongoDB for articles where ``is_tagged`` is not True.
      2. Run batch tagging via rule-based pattern matching.
      3. Save tags, teams, and drivers back to MongoDB.
      4. Re-index updated articles into Elasticsearch.
      5. Return aggregate statistics.
    """
    # 1. Fetch untagged articles
    articles = await ArticleRepository.find_untagged_articles(limit=limit)

    if not articles:
        logger.info("No untagged articles found")
        return PipelineTaggingResult()

    logger.info("Starting tagging pipeline for %d article(s)", len(articles))

    # 2. Run batch tagging
    results = await tag_batch(articles, concurrency=concurrency)

    # Build a lookup from URL to article for later re-indexing
    article_by_url: dict[str, ArticleDocument] = {a.url: a for a in articles}

    succeeded = 0
    failed = 0

    # 3 & 4. Persist and index
    for url, tag_result in results:
        article = article_by_url.get(url)
        if article is None:
            failed += 1
            continue

        update_fields = {
            "tags": tag_result.all_tags,
            "teams": tag_result.teams,
            "drivers": tag_result.drivers,
            "is_tagged": True,
        }

        # 3. Update MongoDB
        try:
            await ArticleRepository.update_article(url=url, update_fields=update_fields)
        except Exception:
            logger.exception("Failed to update tags in MongoDB: %s", url)
            failed += 1
            continue

        # 4. Re-index into Elasticsearch with the new tags
        updated_article = article.model_copy(update=update_fields)
        try:
            await index_article(updated_article)
        except Exception:
            logger.exception("Failed to index tagged article in ES: %s", url)
            # MongoDB write succeeded, still count as succeeded
            succeeded += 1
            continue

        succeeded += 1

    result = PipelineTaggingResult(
        total=len(articles),
        succeeded=succeeded,
        failed=failed,
    )
    logger.info(
        "Tagging pipeline complete — total=%d succeeded=%d failed=%d",
        result.total,
        result.succeeded,
        result.failed,
    )
    return result


# ---------------------------------------------------------------------------
# Full pipeline (summary + translation + tagging)
# ---------------------------------------------------------------------------


async def run_full_pipeline(
    limit: int = 50,
    concurrency: int = 3,
) -> PipelineFullResult:
    """Run the summary, translation, and tagging pipelines sequentially.

    Executes all pipelines in order so that articles processed in earlier
    steps are available for subsequent steps.
    """
    logger.info("Starting full pipeline (summary + translation + tagging)")

    summary_result = await run_summary_pipeline(limit=limit, concurrency=concurrency)
    translation_result = await run_translation_pipeline(limit=limit, concurrency=concurrency)
    tagging_result = await run_tagging_pipeline(limit=limit, concurrency=concurrency)

    return PipelineFullResult(
        summary=summary_result,
        translation=translation_result,
        tagging=tagging_result,
    )
