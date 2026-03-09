"""MongoDB index definitions — called once on application startup."""

import logging

from pymongo import ASCENDING, DESCENDING, IndexModel

from app.core.database import get_database

logger = logging.getLogger(__name__)


async def ensure_indexes() -> None:
    """Create MongoDB indexes for all collections.

    Safe to call multiple times — MongoDB will skip indexes that already exist.
    """
    db = get_database()

    # --- Articles ---
    articles = db["articles"]
    article_indexes = [
        IndexModel([("url", ASCENDING)], unique=True, name="ux_article_url"),
        IndexModel([("source", ASCENDING)], name="ix_article_source"),
        IndexModel([("published_at", DESCENDING)], name="ix_article_published_at"),
        IndexModel([("tags", ASCENDING)], name="ix_article_tags"),
        IndexModel([("scraped_at", DESCENDING)], name="ix_article_scraped_at"),
    ]
    await articles.create_indexes(article_indexes)
    logger.info("Ensured indexes for 'articles' collection")

    # --- Transcripts ---
    transcripts = db["transcripts"]
    transcript_indexes = [
        IndexModel([("gp_name", ASCENDING)], name="ix_transcript_gp_name"),
        IndexModel([("date", DESCENDING)], name="ix_transcript_date"),
        IndexModel([("source_url", ASCENDING)], unique=True, name="ux_transcript_source_url"),
    ]
    await transcripts.create_indexes(transcript_indexes)
    logger.info("Ensured indexes for 'transcripts' collection")

    # --- Teams ---
    teams = db["teams"]
    team_indexes = [
        IndexModel([("team_id", ASCENDING)], unique=True, name="ux_team_id"),
    ]
    await teams.create_indexes(team_indexes)
    logger.info("Ensured indexes for 'teams' collection")

    # --- Drivers ---
    drivers = db["drivers"]
    driver_indexes = [
        IndexModel([("driver_id", ASCENDING)], unique=True, name="ux_driver_id"),
        IndexModel([("team_id", ASCENDING)], name="ix_driver_team_id"),
        IndexModel([("last_name", ASCENDING)], name="ix_driver_last_name"),
    ]
    await drivers.create_indexes(driver_indexes)
    logger.info("Ensured indexes for 'drivers' collection")
