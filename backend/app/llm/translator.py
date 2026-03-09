"""Article translation (English → Korean) using LLM with glossary post-processing."""

from __future__ import annotations

import asyncio
import logging
import re

from app.llm.glossary import apply_glossary
from app.llm.prompts import build_translation_prompt
from app.llm.service import get_llm_service
from app.models.article import ArticleDocument

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

_MIN_TRANSLATION_LENGTH = 30
_MAX_TRANSLATION_LENGTH = 800
_HANGUL_PATTERN = re.compile(r"[\uac00-\ud7af]")


def validate_translation(translation: str) -> bool:
    """Check whether a generated translation meets quality requirements.

    Criteria:
      - Between 30 and 800 characters.
      - Contains at least some Hangul characters (i.e., is actually Korean).
      - Hangul characters make up a meaningful portion of the text.

    Returns True when the translation passes all checks.
    """
    text = translation.strip()
    if len(text) < _MIN_TRANSLATION_LENGTH:
        logger.debug("Translation too short (%d chars): %s...", len(text), text[:40])
        return False

    if len(text) > _MAX_TRANSLATION_LENGTH:
        logger.debug("Translation too long (%d chars)", len(text))
        return False

    hangul_chars = _HANGUL_PATTERN.findall(text)
    if not hangul_chars:
        logger.debug("Translation contains no Hangul characters")
        return False

    # At least 15% of non-space characters should be Hangul
    non_space = len(text.replace(" ", ""))
    if non_space > 0 and len(hangul_chars) / non_space < 0.15:
        logger.debug(
            "Translation has too few Hangul characters (%d/%d)",
            len(hangul_chars),
            non_space,
        )
        return False

    return True


# ---------------------------------------------------------------------------
# Single article
# ---------------------------------------------------------------------------


async def translate_article(article: ArticleDocument) -> str | None:
    """Translate the English summary of a single article to Korean.

    Returns the Korean translation, or None if:
      - The article has no English summary.
      - The article already has a Korean translation.
      - LLM generation or validation fails.
    """
    if not article.summary_en:
        logger.debug("No English summary, skipping translation: %s", article.url)
        return None

    if article.summary_ko:
        logger.debug("Skipping already-translated article: %s", article.url)
        return article.summary_ko

    prompt = build_translation_prompt(article.summary_en)

    try:
        service = get_llm_service()
        response = await service.generate(
            prompt=prompt,
            temperature=0.3,
            max_tokens=512,
        )
    except Exception:
        logger.exception("LLM translation failed for article: %s", article.url)
        return None

    translation = response.content.strip()

    # Apply glossary post-processing for terminology consistency
    translation = apply_glossary(translation)

    if not validate_translation(translation):
        logger.warning("Translation failed validation for article: %s", article.url)
        return None

    return translation


# ---------------------------------------------------------------------------
# Batch processing
# ---------------------------------------------------------------------------


async def translate_batch(
    articles: list[ArticleDocument],
    concurrency: int = 3,
) -> list[tuple[str, str | None]]:
    """Translate multiple articles with controlled concurrency.

    Returns a list of (url, translation) tuples. The translation is None when
    generation or validation fails for an individual article.
    """
    semaphore = asyncio.Semaphore(concurrency)

    async def _process(article: ArticleDocument) -> tuple[str, str | None]:
        async with semaphore:
            translation = await translate_article(article)
            return (article.url, translation)

    tasks = [asyncio.create_task(_process(a)) for a in articles]
    return list(await asyncio.gather(*tasks))
