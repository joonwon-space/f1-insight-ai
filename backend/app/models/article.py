"""Pydantic models for F1 news articles."""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field, HttpUrl


class NewsSource(StrEnum):
    """Supported F1 news sources."""

    FORMULA1 = "formula1.com"
    THE_RACE = "the-race.com"
    AUTOSPORT = "autosport.com"


class ArticleLink(BaseModel):
    """A link to an article discovered on a listing page."""

    url: str
    title: str
    source: NewsSource

    model_config = {"frozen": True}


class RawArticle(BaseModel):
    """A scraped article before LLM processing."""

    url: str
    title: str
    content: str = Field(description="Extracted article body text")
    source: NewsSource
    published_at: datetime | None = None
    author: str | None = None
    image_url: str | None = None
    tags: list[str] = Field(default_factory=list)
    scraped_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {"frozen": True}


class ArticleDocument(BaseModel):
    """Article as stored in MongoDB."""

    url: str
    title: str
    content: str
    source: NewsSource
    published_at: datetime | None = None
    author: str | None = None
    image_url: HttpUrl | None = None
    tags: list[str] = Field(default_factory=list)
    scraped_at: datetime = Field(default_factory=datetime.utcnow)
    summary_en: str | None = None
    summary_ko: str | None = None
    is_summarized: bool = False

    model_config = {"frozen": True}
