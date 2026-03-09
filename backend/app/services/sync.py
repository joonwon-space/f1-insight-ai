"""MongoDB → Elasticsearch sync pipeline.

Provides real-time synchronization via MongoDB Change Streams and a full
re-sync function for initial setup or disaster recovery.
"""

import asyncio
import logging
from datetime import datetime

from pymongo.errors import PyMongoError

from app.core.database import get_database
from app.models.article import ArticleDocument
from app.services.es_indexer import bulk_index_articles, index_article
from app.services.repository import ARTICLES_COLLECTION
from app.services.sync_models import SyncMode, SyncStatus

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Module-level state
# ---------------------------------------------------------------------------

_sync_task: asyncio.Task | None = None  # type: ignore[type-arg]
_status = SyncStatus()

FULL_SYNC_BATCH_SIZE = 100
_MAX_BACKOFF_SECONDS = 60


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def get_sync_status() -> SyncStatus:
    """Return a snapshot of the current sync state."""
    return _status.model_copy()


async def start_sync() -> None:
    """Start the change-stream watcher as a background asyncio task.

    If already running, this is a no-op.
    """
    global _sync_task
    if _sync_task is not None and not _sync_task.done():
        logger.info("Sync watcher already running — skipping start")
        return

    _sync_task = asyncio.create_task(_watch_change_stream())
    logger.info("Change-stream sync watcher started")


async def stop_sync() -> None:
    """Gracefully stop the change-stream watcher."""
    global _sync_task, _status
    if _sync_task is None or _sync_task.done():
        logger.info("Sync watcher is not running — nothing to stop")
        return

    _sync_task.cancel()
    try:
        await _sync_task
    except asyncio.CancelledError:
        pass
    _sync_task = None
    _status = _status.model_copy(update={"is_running": False, "mode": SyncMode.IDLE})
    logger.info("Change-stream sync watcher stopped")


def _watcher_is_active() -> bool:
    """Check whether the change-stream watcher task is still running."""
    return _sync_task is not None and not _sync_task.done()


def _current_mode() -> SyncMode:
    """Return REALTIME if the watcher is active, otherwise IDLE."""
    return SyncMode.REALTIME if _watcher_is_active() else SyncMode.IDLE


async def run_full_sync() -> int:
    """Read all articles from MongoDB and bulk-index them into Elasticsearch.

    Uses cursor-based pagination to avoid loading all documents at once.
    Returns the total number of successfully synced documents.
    """
    global _status
    _status = _status.model_copy(update={"is_running": True, "mode": SyncMode.FULL})
    logger.info("Starting full MongoDB → Elasticsearch sync")

    db = get_database()
    collection = db[ARTICLES_COLLECTION]
    total_synced = 0
    skip = 0

    try:
        while True:
            cursor = (
                collection.find({}).sort("scraped_at", -1).skip(skip).limit(FULL_SYNC_BATCH_SIZE)
            )
            batch: list[ArticleDocument] = []
            async for doc in cursor:
                doc.pop("_id", None)
                try:
                    batch.append(ArticleDocument(**doc))
                except Exception:
                    logger.warning("Skipping invalid document at offset %d", skip + len(batch))

            if not batch:
                break

            indexed = await bulk_index_articles(batch)
            total_synced += indexed
            skip += FULL_SYNC_BATCH_SIZE
            logger.info(
                "Full sync progress: indexed %d (batch %d), total %d so far",
                indexed,
                len(batch),
                total_synced,
            )

        _status = _status.model_copy(
            update={
                "total_synced": _status.total_synced + total_synced,
                "last_sync_at": datetime.utcnow(),
                "mode": _current_mode(),
                "is_running": _watcher_is_active(),
            }
        )
        logger.info("Full sync completed: %d documents indexed", total_synced)

    except Exception as exc:
        _status = _status.model_copy(
            update={
                "error_count": _status.error_count + 1,
                "last_error": str(exc),
                "mode": _current_mode(),
                "is_running": _watcher_is_active(),
            }
        )
        logger.exception("Full sync failed")

    return total_synced


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _doc_to_article(doc: dict) -> ArticleDocument | None:
    """Convert a raw MongoDB document dict to an ArticleDocument.

    Returns None if the document cannot be parsed.
    """
    doc.pop("_id", None)
    try:
        return ArticleDocument(**doc)
    except Exception:
        logger.warning("Failed to parse document: %s", doc.get("url", "<unknown>"))
        return None


async def _watch_change_stream() -> None:
    """Watch the articles collection for insert/update operations.

    Reconnects with exponential backoff on errors.
    Falls back gracefully when the MongoDB deployment does not support
    change streams (e.g. standalone mode without a replica set).
    """
    global _status
    _status = _status.model_copy(update={"is_running": True, "mode": SyncMode.REALTIME})

    backoff = 1
    pipeline = [{"$match": {"operationType": {"$in": ["insert", "update", "replace"]}}}]

    while True:
        try:
            db = get_database()
            collection = db[ARTICLES_COLLECTION]
            logger.info("Opening change stream on '%s' collection", ARTICLES_COLLECTION)

            async with collection.watch(pipeline, full_document="updateLookup") as stream:
                backoff = 1  # reset on successful connection
                async for change in stream:
                    await _handle_change_event(change)

        except asyncio.CancelledError:
            logger.info("Change-stream watcher cancelled")
            raise

        except PyMongoError as exc:
            error_msg = str(exc)
            # Detect standalone / no replica set — cannot use change streams
            if "not supported" in error_msg.lower() or "replica set" in error_msg.lower():
                logger.warning(
                    "Change streams not supported on this MongoDB deployment "
                    "(requires replica set). Real-time sync disabled. "
                    "Use POST /sync/full for manual synchronization."
                )
                _status = _status.model_copy(
                    update={
                        "is_running": False,
                        "mode": SyncMode.IDLE,
                        "last_error": "Change streams not supported (standalone MongoDB)",
                    }
                )
                return  # exit the watcher — no point retrying

            _status = _status.model_copy(
                update={
                    "error_count": _status.error_count + 1,
                    "last_error": error_msg,
                }
            )
            logger.warning("Change stream error, reconnecting in %ds: %s", backoff, error_msg)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, _MAX_BACKOFF_SECONDS)

        except Exception as exc:
            _status = _status.model_copy(
                update={
                    "error_count": _status.error_count + 1,
                    "last_error": str(exc),
                }
            )
            logger.exception("Unexpected error in change-stream watcher, retrying in %ds", backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, _MAX_BACKOFF_SECONDS)


async def _handle_change_event(change: dict) -> None:
    """Process a single change-stream event."""
    global _status
    operation = change.get("operationType")
    full_doc = change.get("fullDocument")

    if full_doc is None:
        logger.debug("Change event '%s' has no fullDocument — skipping", operation)
        return

    article = _doc_to_article(full_doc)
    if article is None:
        return

    try:
        await index_article(article)
        _status = _status.model_copy(
            update={
                "total_synced": _status.total_synced + 1,
                "last_sync_at": datetime.utcnow(),
            }
        )
        logger.debug(
            "Synced %s event for article '%s'",
            operation,
            article.title[:60],
        )
    except Exception as exc:
        _status = _status.model_copy(
            update={
                "error_count": _status.error_count + 1,
                "last_error": f"Index failed for {article.url}: {exc}",
            }
        )
        logger.warning(
            "Failed to index article '%s' after %s event: %s",
            article.title[:60],
            operation,
            exc,
        )
