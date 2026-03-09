import logging

from elasticsearch import AsyncElasticsearch

from app.core.config import settings

logger = logging.getLogger(__name__)

_client: AsyncElasticsearch | None = None


async def connect_elasticsearch() -> None:
    """Connect to Elasticsearch."""
    global _client
    logger.info("Connecting to Elasticsearch at %s", settings.elasticsearch_url)
    _client = AsyncElasticsearch(hosts=[settings.elasticsearch_url])
    info = await _client.info()
    logger.info(
        "Connected to Elasticsearch cluster '%s' (version %s)",
        info["cluster_name"],
        info["version"]["number"],
    )


async def close_elasticsearch() -> None:
    """Close the Elasticsearch connection."""
    global _client
    if _client is not None:
        await _client.close()
        _client = None
        logger.info("Closed Elasticsearch connection")


def get_elasticsearch() -> AsyncElasticsearch:
    """Return the Elasticsearch client instance.

    Raises:
        RuntimeError: If the Elasticsearch connection has not been initialized.
    """
    if _client is None:
        raise RuntimeError(
            "Elasticsearch connection not initialized. Call connect_elasticsearch() first."
        )
    return _client


async def ping_elasticsearch() -> bool:
    """Check if Elasticsearch is reachable."""
    if _client is None:
        return False
    try:
        return await _client.ping()
    except Exception:
        return False
