import logging

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.config import settings

logger = logging.getLogger(__name__)

_client: AsyncIOMotorClient | None = None
_database: AsyncIOMotorDatabase | None = None


async def connect_mongodb() -> None:
    """Connect to MongoDB using Motor async driver."""
    global _client, _database
    logger.info("Connecting to MongoDB at %s", settings.mongodb_uri)
    _client = AsyncIOMotorClient(settings.mongodb_uri)
    _database = _client[settings.mongodb_db]
    # Verify connection
    await _client.admin.command("ping")
    logger.info("Connected to MongoDB database '%s'", settings.mongodb_db)


async def close_mongodb() -> None:
    """Close the MongoDB connection."""
    global _client, _database
    if _client is not None:
        _client.close()
        _client = None
        _database = None
        logger.info("Closed MongoDB connection")


def get_database() -> AsyncIOMotorDatabase:
    """Return the MongoDB database instance.

    Raises:
        RuntimeError: If the database connection has not been initialized.
    """
    if _database is None:
        raise RuntimeError("MongoDB connection not initialized. Call connect_mongodb() first.")
    return _database


async def ping_mongodb() -> bool:
    """Check if MongoDB is reachable."""
    if _client is None:
        return False
    try:
        await _client.admin.command("ping")
        return True
    except Exception:
        return False
