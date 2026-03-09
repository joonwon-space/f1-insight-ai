"""Article summarization using LLM — single-article and batch processing."""

from __future__ import annotations

import asyncio
import logging

from app.llm.prompts import build_summary_prompt
from app.llm.service import get_llm_service
from app.models.article import ArticleDocument

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Quality validation
# ---------------------------------------------------------------------------

_MIN_SUMMARY_LENGTH = 50
_MAX_SUMMARY_LENGTH = 500
_SIMILARITY_THRESHOLD = 0.85


def validate_summary(summary: str, article: ArticleDocument) -> bool:
    """Check whether a generated summary meets quality requirements.

    Criteria:
      - Between 50 and 500 characters.
      - Not a near-duplicate of the article title.

    Returns True when the summary passes all checks.
    """
    text = summary.strip()
    if len(text) < _MIN_SUMMARY_LENGTH:
        logger.debug("Summary too short (%d chars): %s...", len(text), text[:40])
        return False

    if len(text) > _MAX_SUMMARY_LENGTH:
        logger.debug("Summary too long (%d chars)", len(text))
        return False

    # Reject if the summary is essentially the title repeated
    title_lower = article.title.strip().lower()
    summary_lower = text.lower()
    if title_lower in summary_lower and len(summary_lower) < len(title_lower) * 1.3:
        logger.debug("Summary is near-duplicate of title")
        return False

    return True


# ---------------------------------------------------------------------------
# Single article
# ---------------------------------------------------------------------------


async def summarize_article(article: ArticleDocument) -> str | None:
    """Generate an English summary for a single article.

    Returns the summary text, or None if the article already has one or if
    generation / validation fails.
    """
    if article.summary_en:
        logger.debug("Skipping already-summarized article: %s", article.url)
        return article.summary_en

    if not article.content or not article.content.strip():
        logger.warning("Article has no content, skipping: %s", article.url)
        return None

    prompt = build_summary_prompt(article.title, article.content)

    try:
        service = get_llm_service()
        response = await service.generate(
            prompt=prompt,
            temperature=0.3,
            max_tokens=256,
        )
    except Exception:
        logger.exception("LLM generation failed for article: %s", article.url)
        return None

    summary = response.content.strip()

    if not validate_summary(summary, article):
        logger.warning("Summary failed validation for article: %s", article.url)
        return None

    return summary


# ---------------------------------------------------------------------------
# Batch processing
# ---------------------------------------------------------------------------


async def summarize_batch(
    articles: list[ArticleDocument],
    concurrency: int = 3,
) -> list[tuple[str, str | None]]:
    """Summarize multiple articles with controlled concurrency.

    Returns a list of (url, summary) tuples. The summary is None when
    generation or validation fails for an individual article.
    """
    semaphore = asyncio.Semaphore(concurrency)

    async def _process(article: ArticleDocument) -> tuple[str, str | None]:
        async with semaphore:
            summary = await summarize_article(article)
            return (article.url, summary)

    tasks = [asyncio.create_task(_process(a)) for a in articles]
    return list(await asyncio.gather(*tasks))
