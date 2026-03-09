"""Prompt templates for LLM-based article summarization."""

from __future__ import annotations

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
