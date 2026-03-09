"""Prompt templates for LLM-based article summarization and translation."""

from __future__ import annotations

from app.llm.glossary import get_glossary_reference

SUMMARY_EN_SYSTEM = """You are a Formula 1 news editor. Your job is to produce concise, engaging \
English summaries of F1 articles.

Rules:
- Write exactly 2-4 sentences.
- Follow the AIDA framework: open with an attention-grabbing statement, build interest with key \
facts, create desire to learn more, and end with an actionable takeaway or forward-looking note.
- Cover the essential facts: who (driver/team), what happened, when, where, and why it matters.
- Preserve all driver names, team names, and technical terms exactly as they appear.
- Do NOT add opinions or speculation beyond what the article states.
- Output ONLY the summary paragraph, no headings or bullet points."""

_MAX_CONTENT_CHARS = 3000


def build_summary_prompt(title: str, content: str) -> str:
    """Format a summarization prompt from an article's title and body.

    The content is truncated to ~3000 characters to fit within typical model
    context windows while retaining the most important information (articles
    lead with the key facts).
    """
    truncated = content[:_MAX_CONTENT_CHARS]
    if len(content) > _MAX_CONTENT_CHARS:
        truncated = truncated.rsplit(" ", 1)[0] + " ..."

    return f"{SUMMARY_EN_SYSTEM}\n\n---\nTitle: {title}\n\nArticle:\n{truncated}\n---\n\nSummary:"


# ---------------------------------------------------------------------------
# Korean translation prompts
# ---------------------------------------------------------------------------

TRANSLATE_KR_SYSTEM = f"""You are a professional Korean translator specializing in Formula 1 \
motorsport content. Translate the given English F1 summary into natural, fluent Korean.

Rules:
- Translate naturally and idiomatically, not word-for-word.
- Keep all driver names and personal names in English (e.g., Max Verstappen, Lewis Hamilton).
- Use standard Korean F1 terminology for technical terms, team names, and session types.
- Maintain the same tone, structure, and factual content as the original.
- Do NOT add any information not present in the original.
- Output ONLY the translated text, no headings, bullet points, or explanations.

F1 Terminology Reference (English → Korean):
{get_glossary_reference()}"""


def build_translation_prompt(summary_en: str) -> str:
    """Format a translation prompt from an English summary.

    Returns a complete prompt string with the system instructions and the
    source text to translate.
    """
    return (
        f"{TRANSLATE_KR_SYSTEM}\n\n---\nEnglish summary:\n{summary_en}\n---\n\nKorean translation:"
    )
