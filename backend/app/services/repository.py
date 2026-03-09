"""MongoDB repository layer for articles, transcripts, and master data."""

import logging
from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.database import get_database
from app.models.article import ArticleDocument
from app.models.master_data import get_drivers, get_teams
from app.models.team import Driver, Team
from app.models.transcript import Transcript

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Collection names
# ---------------------------------------------------------------------------

ARTICLES_COLLECTION = "articles"
TRANSCRIPTS_COLLECTION = "transcripts"
TEAMS_COLLECTION = "teams"
DRIVERS_COLLECTION = "drivers"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _db() -> AsyncIOMotorDatabase:
    return get_database()


def _serialize_model(model: Any) -> dict[str, Any]:
    """Serialize a Pydantic model to a MongoDB-friendly dict."""
    data = model.model_dump(mode="json")
    return data


# ---------------------------------------------------------------------------
# ArticleRepository
# ---------------------------------------------------------------------------


class ArticleRepository:
    """CRUD operations for the articles collection."""

    @staticmethod
    async def insert_article(article: ArticleDocument) -> str:
        """Insert an article and return the inserted _id as string."""
        doc = _serialize_model(article)
        result = await _db()[ARTICLES_COLLECTION].insert_one(doc)
        return str(result.inserted_id)

    @staticmethod
    async def find_by_url(url: str) -> ArticleDocument | None:
        """Find an article by its URL. Returns None if not found."""
        doc = await _db()[ARTICLES_COLLECTION].find_one({"url": url})
        if doc is None:
            return None
        doc.pop("_id", None)
        return ArticleDocument(**doc)

    @staticmethod
    async def find_articles(
        filters: dict[str, Any] | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> list[ArticleDocument]:
        """Find articles matching optional filters with pagination."""
        query = filters or {}
        cursor = (
            _db()[ARTICLES_COLLECTION].find(query).sort("scraped_at", -1).skip(skip).limit(limit)
        )
        results: list[ArticleDocument] = []
        async for doc in cursor:
            doc.pop("_id", None)
            results.append(ArticleDocument(**doc))
        return results

    @staticmethod
    async def count_articles(filters: dict[str, Any] | None = None) -> int:
        """Count articles matching optional filters."""
        query = filters or {}
        return await _db()[ARTICLES_COLLECTION].count_documents(query)

    @staticmethod
    async def get_known_urls() -> set[str]:
        """Return all known article URLs for deduplication."""
        cursor = _db()[ARTICLES_COLLECTION].find({}, {"url": 1, "_id": 0})
        urls: set[str] = set()
        async for doc in cursor:
            urls.add(doc["url"])
        return urls


# ---------------------------------------------------------------------------
# TranscriptRepository
# ---------------------------------------------------------------------------


class TranscriptRepository:
    """CRUD operations for the transcripts collection."""

    @staticmethod
    async def insert_transcript(transcript: Transcript) -> str:
        """Insert a transcript and return the inserted _id as string."""
        doc = _serialize_model(transcript)
        result = await _db()[TRANSCRIPTS_COLLECTION].insert_one(doc)
        return str(result.inserted_id)

    @staticmethod
    async def find_transcripts(
        filters: dict[str, Any] | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Transcript]:
        """Find transcripts matching optional filters with pagination."""
        query = filters or {}
        cursor = _db()[TRANSCRIPTS_COLLECTION].find(query).sort("date", -1).skip(skip).limit(limit)
        results: list[Transcript] = []
        async for doc in cursor:
            doc.pop("_id", None)
            results.append(Transcript(**doc))
        return results


# ---------------------------------------------------------------------------
# MasterDataRepository
# ---------------------------------------------------------------------------


class MasterDataRepository:
    """Manage teams and drivers master data collections."""

    @staticmethod
    async def ensure_master_data() -> None:
        """Seed teams and drivers collections if they are empty."""
        db = _db()

        teams_count = await db[TEAMS_COLLECTION].count_documents({})
        if teams_count == 0:
            teams = [_serialize_model(t) for t in get_teams()]
            await db[TEAMS_COLLECTION].insert_many(teams)
            logger.info("Seeded %d teams into MongoDB", len(teams))

        drivers_count = await db[DRIVERS_COLLECTION].count_documents({})
        if drivers_count == 0:
            drivers = [_serialize_model(d) for d in get_drivers()]
            await db[DRIVERS_COLLECTION].insert_many(drivers)
            logger.info("Seeded %d drivers into MongoDB", len(drivers))

    @staticmethod
    async def get_teams() -> list[Team]:
        """Return all teams from MongoDB."""
        cursor = _db()[TEAMS_COLLECTION].find({})
        results: list[Team] = []
        async for doc in cursor:
            doc.pop("_id", None)
            results.append(Team(**doc))
        return results

    @staticmethod
    async def get_drivers() -> list[Driver]:
        """Return all drivers from MongoDB."""
        cursor = _db()[DRIVERS_COLLECTION].find({})
        results: list[Driver] = []
        async for doc in cursor:
            doc.pop("_id", None)
            results.append(Driver(**doc))
        return results

    @staticmethod
    async def get_driver_by_name(last_name: str) -> Driver | None:
        """Find a driver by last name (case-insensitive)."""
        doc = await _db()[DRIVERS_COLLECTION].find_one(
            {"last_name": {"$regex": f"^{last_name}$", "$options": "i"}}
        )
        if doc is None:
            return None
        doc.pop("_id", None)
        return Driver(**doc)
