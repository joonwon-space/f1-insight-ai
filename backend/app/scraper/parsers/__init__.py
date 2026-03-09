"""Parser registry for F1 news sources."""

from app.models.article import NewsSource
from app.scraper.parsers.autosport import AutosportParser
from app.scraper.parsers.base import BaseParser
from app.scraper.parsers.formula1 import Formula1Parser
from app.scraper.parsers.the_race import TheRaceParser

PARSER_REGISTRY: dict[NewsSource, BaseParser] = {
    NewsSource.FORMULA1: Formula1Parser(),
    NewsSource.THE_RACE: TheRaceParser(),
    NewsSource.AUTOSPORT: AutosportParser(),
}


def get_parser(source: NewsSource) -> BaseParser:
    """Get the parser for a given news source.

    Args:
        source: The news source to get a parser for.

    Returns:
        The parser instance for the source.

    Raises:
        KeyError: If no parser is registered for the source.
    """
    if source not in PARSER_REGISTRY:
        raise KeyError(f"No parser registered for source: {source}")
    return PARSER_REGISTRY[source]


__all__ = [
    "PARSER_REGISTRY",
    "AutosportParser",
    "BaseParser",
    "Formula1Parser",
    "TheRaceParser",
    "get_parser",
]
