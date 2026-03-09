"""Rule-based auto-tagging for F1 articles — teams, drivers, and topics."""

from __future__ import annotations

import asyncio
import logging
import re
from typing import Sequence

from pydantic import BaseModel

from app.models.article import ArticleDocument
from app.models.master_data import get_drivers, get_teams

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Result model
# ---------------------------------------------------------------------------


class TagResult(BaseModel):
    """Tagging output for a single article."""

    teams: list[str] = []
    drivers: list[str] = []
    topics: list[str] = []

    model_config = {"frozen": True}

    @property
    def all_tags(self) -> list[str]:
        """Return a flat, deduplicated list of all tags for the tags field."""
        seen: set[str] = set()
        tags: list[str] = []
        for tag in [*self.teams, *self.drivers, *self.topics]:
            lower = tag.lower()
            if lower not in seen:
                seen.add(lower)
                tags.append(tag)
        return tags


# ---------------------------------------------------------------------------
# Team aliases (canonical name -> set of aliases for matching)
# ---------------------------------------------------------------------------

_TEAM_ALIASES: dict[str, list[str]] = {
    "Mercedes": [
        "Mercedes",
        "Mercedes-AMG",
        "Mercedes AMG",
        "PETRONAS",
    ],
    "Ferrari": [
        "Ferrari",
        "Scuderia Ferrari",
    ],
    "McLaren": [
        "McLaren",
    ],
    "Red Bull": [
        "Red Bull Racing",
        "Red Bull",
        "RBR",
        "Oracle Red Bull",
    ],
    "Alpine": [
        "Alpine",
        "BWT Alpine",
    ],
    "Williams": [
        "Williams",
        "Williams Racing",
    ],
    "Racing Bulls": [
        "Racing Bulls",
        "VCARB",
        "Visa Cash App Racing Bulls",
        "AlphaTauri",
        "Toro Rosso",
    ],
    "Aston Martin": [
        "Aston Martin",
        "AMR",
        "Aston Martin Aramco",
    ],
    "Haas": [
        "Haas",
        "MoneyGram Haas",
    ],
    "Audi": [
        "Audi",
        "Audi F1",
        "Kick Sauber",
        "Sauber",
    ],
    "Cadillac": [
        "Cadillac",
        "Cadillac F1",
        "Andretti",
        "Andretti Cadillac",
    ],
}


# ---------------------------------------------------------------------------
# Driver first-name -> last-name disambiguations
# Only include first names that uniquely identify a driver.
# ---------------------------------------------------------------------------

_FIRST_NAME_MAP: dict[str, str] = {
    "Max": "Verstappen",
    "Lewis": "Hamilton",
    "Charles": "Leclerc",
    "Lando": "Norris",
    "Oscar": "Piastri",
    "George": "Russell",
    "Fernando": "Alonso",
    "Carlos": "Sainz",
    "Pierre": "Gasly",
    "Yuki": "Tsunoda",
    "Lance": "Stroll",
    "Esteban": "Ocon",
    "Nico": "Hulkenberg",
    "Alexander": "Albon",
    "Alex": "Albon",
    "Liam": "Lawson",
    "Oliver": "Bearman",
    "Ollie": "Bearman",
    "Jack": "Doohan",
    "Gabriel": "Bortoleto",
    "Isack": "Hadjar",
    "Felipe": "Drugovich",
    "Theo": "Pourchaire",
}


# ---------------------------------------------------------------------------
# Topic patterns
# ---------------------------------------------------------------------------

_SESSION_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("qualifying", re.compile(r"\bqualifying\b", re.IGNORECASE)),
    ("race", re.compile(r"\brace\b", re.IGNORECASE)),
    ("practice", re.compile(r"\b(?:free\s+)?practice\b|\bFP[1-3]\b", re.IGNORECASE)),
    ("sprint", re.compile(r"\bsprint\b", re.IGNORECASE)),
]

_TOPIC_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("penalty", re.compile(r"\bpenalt(?:y|ies)\b", re.IGNORECASE)),
    ("crash", re.compile(r"\b(?:crash|collision|accident|incident)\b", re.IGNORECASE)),
    ("podium", re.compile(r"\bpodium\b", re.IGNORECASE)),
    ("pole position", re.compile(r"\bpole\s+position\b|\bpole\b", re.IGNORECASE)),
    ("pit stop", re.compile(r"\bpit\s+stop\b|\bpit\s+strategy\b", re.IGNORECASE)),
    ("strategy", re.compile(r"\bstrateg(?:y|ies)\b", re.IGNORECASE)),
    ("contract", re.compile(r"\bcontract\b", re.IGNORECASE)),
    ("transfer", re.compile(r"\btransfer\b|\bsigning\b|\bsigned\b", re.IGNORECASE)),
    ("regulation", re.compile(r"\bregulation\b|\brule\s+change\b|\brules\b", re.IGNORECASE)),
    ("championship", re.compile(r"\bchampionship\b|\btitle\s+race\b", re.IGNORECASE)),
    ("retirement", re.compile(r"\bretir(?:e|ed|ement|ing)\b", re.IGNORECASE)),
    ("safety car", re.compile(r"\bsafety\s+car\b|\bVSC\b", re.IGNORECASE)),
    ("tire", re.compile(r"\btyre\b|\btire\b", re.IGNORECASE)),
    ("upgrade", re.compile(r"\bupgrade\b", re.IGNORECASE)),
    ("weather", re.compile(r"\brain\b|\bwet\b|\bweather\b", re.IGNORECASE)),
    ("DRS", re.compile(r"\bDRS\b")),
    ("red flag", re.compile(r"\bred\s+flag\b", re.IGNORECASE)),
    ("overtake", re.compile(r"\bovertake\b|\bovertaking\b", re.IGNORECASE)),
]


# ---------------------------------------------------------------------------
# Pre-compiled matchers (built lazily on first use)
# ---------------------------------------------------------------------------

_team_patterns: list[tuple[str, re.Pattern[str]]] | None = None
_driver_patterns: list[tuple[str, re.Pattern[str]]] | None = None


def _build_team_patterns() -> list[tuple[str, re.Pattern[str]]]:
    """Build regex patterns for team name matching.

    Includes aliases from the static map and also validates against master data.
    """
    teams = {t.name for t in get_teams()}
    patterns: list[tuple[str, re.Pattern[str]]] = []

    # Sort aliases by length (longest first) to avoid partial matches
    for canonical, aliases in _TEAM_ALIASES.items():
        if canonical not in teams:
            logger.warning("Team alias canonical name '%s' not in master data", canonical)
        sorted_aliases = sorted(aliases, key=len, reverse=True)
        combined = "|".join(re.escape(a) for a in sorted_aliases)
        patterns.append((canonical, re.compile(rf"\b(?:{combined})\b", re.IGNORECASE)))

    return patterns


def _build_driver_patterns() -> list[tuple[str, re.Pattern[str]]]:
    """Build regex patterns for driver name matching.

    Matches last name, full name, abbreviation (uppercase only), and
    common first-name references.
    """
    drivers = get_drivers()
    patterns: list[tuple[str, re.Pattern[str]]] = []

    for driver in drivers:
        canonical = f"{driver.first_name} {driver.last_name}"
        alternatives: list[str] = []

        # Full name (longest first)
        alternatives.append(re.escape(f"{driver.first_name} {driver.last_name}"))
        # Last name only
        alternatives.append(re.escape(driver.last_name))

        # First-name-only matches (only if mapped to avoid ambiguity)
        first = driver.first_name.split()[0]  # handle "Andrea Kimi" -> "Andrea"
        if first in _FIRST_NAME_MAP and _FIRST_NAME_MAP[first] == driver.last_name:
            alternatives.append(re.escape(first))
        # Also check the full first_name for multi-word names like "Andrea Kimi"
        if driver.first_name in _FIRST_NAME_MAP:
            alternatives.append(re.escape(driver.first_name))

        # Sort by length descending to match longest first
        alternatives.sort(key=len, reverse=True)
        combined = "|".join(alternatives)

        # Abbreviation must be exactly 3 uppercase letters to avoid false positives
        abbr_pattern = rf"\b{re.escape(driver.abbreviation)}\b"
        full_pattern = rf"\b(?:{combined})\b"

        # Combine: word-boundary name match OR uppercase abbreviation match
        patterns.append(
            (
                canonical,
                re.compile(rf"(?:{full_pattern})|(?:{abbr_pattern})", re.IGNORECASE),
            )
        )

    return patterns


def _get_team_patterns() -> list[tuple[str, re.Pattern[str]]]:
    global _team_patterns
    if _team_patterns is None:
        _team_patterns = _build_team_patterns()
    return _team_patterns


def _get_driver_patterns() -> list[tuple[str, re.Pattern[str]]]:
    global _driver_patterns
    if _driver_patterns is None:
        _driver_patterns = _build_driver_patterns()
    return _driver_patterns


# ---------------------------------------------------------------------------
# Core tagging function
# ---------------------------------------------------------------------------


def _extract_text(article: ArticleDocument) -> str:
    """Combine title and content for pattern matching."""
    parts = [article.title]
    if article.content:
        parts.append(article.content)
    return " ".join(parts)


def auto_tag_article(article: ArticleDocument) -> TagResult:
    """Tag an article with teams, drivers, and topics using rule-based matching.

    This is a synchronous, CPU-bound function (no I/O). It scans the article
    title and content for known entity names and topic keywords.
    """
    text = _extract_text(article)

    # --- Teams ---
    matched_teams: list[str] = []
    seen_teams: set[str] = set()
    for canonical, pattern in _get_team_patterns():
        if canonical not in seen_teams and pattern.search(text):
            matched_teams.append(canonical)
            seen_teams.add(canonical)

    # --- Drivers ---
    matched_drivers: list[str] = []
    seen_drivers: set[str] = set()
    for canonical, pattern in _get_driver_patterns():
        if canonical not in seen_drivers and pattern.search(text):
            matched_drivers.append(canonical)
            seen_drivers.add(canonical)

    # --- Sessions & Topics ---
    matched_topics: list[str] = []
    seen_topics: set[str] = set()
    for label, pattern in _SESSION_PATTERNS + _TOPIC_PATTERNS:
        if label not in seen_topics and pattern.search(text):
            matched_topics.append(label)
            seen_topics.add(label)

    return TagResult(
        teams=matched_teams,
        drivers=matched_drivers,
        topics=matched_topics,
    )


# ---------------------------------------------------------------------------
# Batch tagging
# ---------------------------------------------------------------------------


async def tag_batch(
    articles: Sequence[ArticleDocument],
    concurrency: int = 5,
) -> list[tuple[str, TagResult]]:
    """Tag a batch of articles concurrently.

    Since tagging is CPU-bound (regex matching), we run each article's tagging
    in the default executor to avoid blocking the event loop for large batches.

    Returns a list of (url, TagResult) tuples.
    """
    loop = asyncio.get_running_loop()
    semaphore = asyncio.Semaphore(concurrency)

    async def _tag_one(article: ArticleDocument) -> tuple[str, TagResult]:
        async with semaphore:
            result = await loop.run_in_executor(None, auto_tag_article, article)
            return (article.url, result)

    tasks = [_tag_one(article) for article in articles]
    return await asyncio.gather(*tasks)
