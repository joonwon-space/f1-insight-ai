import asyncio

from fastapi import APIRouter

from app.core.database import ping_mongodb
from app.core.elasticsearch import ping_elasticsearch
from app.llm.pipeline import (
    PipelineFullResult,
    PipelineSummaryResult,
    PipelineTaggingResult,
    PipelineTranslationResult,
    run_full_pipeline,
    run_summary_pipeline,
    run_tagging_pipeline,
    run_translation_pipeline,
)
from app.llm.service import get_llm_service
from app.scheduler.models import SchedulerStatus
from app.scheduler.service import get_scheduler_status
from app.services.repository import ArticleRepository
from app.services.sync import get_sync_status, run_full_sync
from app.services.sync_models import SyncStatus

router = APIRouter()


@router.get("/health")
async def health_check() -> dict:
    """Health check endpoint reporting status of all service dependencies."""
    mongodb_ok = await ping_mongodb()
    elasticsearch_ok = await ping_elasticsearch()

    all_healthy = mongodb_ok and elasticsearch_ok
    status = "healthy" if all_healthy else "degraded"

    return {
        "status": status,
        "dependencies": {
            "mongodb": "connected" if mongodb_ok else "disconnected",
            "elasticsearch": "connected" if elasticsearch_ok else "disconnected",
        },
    }


@router.get("/scheduler/status")
async def scheduler_status() -> SchedulerStatus:
    """Return the current scheduler status including mode, next run time, and job count."""
    return get_scheduler_status()


@router.get("/sync/status")
async def sync_status() -> SyncStatus:
    """Return the current MongoDB → Elasticsearch sync status."""
    return get_sync_status()


@router.post("/sync/full")
async def trigger_full_sync() -> dict:
    """Trigger a full re-sync from MongoDB to Elasticsearch.

    The sync runs in the background. Use GET /sync/status to monitor progress.
    """
    asyncio.create_task(run_full_sync())
    return {"message": "Full sync started in background"}


@router.get("/llm/status")
async def llm_status() -> dict:
    """Return available LLM providers and the active model."""
    service = get_llm_service()
    return await service.health_check()


@router.post("/llm/summarize")
async def trigger_summarize(limit: int = 50) -> PipelineSummaryResult:
    """Trigger the English summary pipeline manually.

    Fetches up to ``limit`` unsummarized articles, generates summaries via LLM,
    saves them to MongoDB, and re-indexes into Elasticsearch.
    """
    return await run_summary_pipeline(limit=limit)


@router.post("/llm/translate")
async def trigger_translate(limit: int = 50) -> PipelineTranslationResult:
    """Trigger the Korean translation pipeline manually.

    Fetches up to ``limit`` articles that have English summaries but no Korean
    translation, translates them via LLM, saves to MongoDB, and re-indexes
    into Elasticsearch.
    """
    return await run_translation_pipeline(limit=limit)


@router.post("/llm/tag")
async def trigger_tagging(limit: int = 100) -> PipelineTaggingResult:
    """Trigger the auto-tagging pipeline manually.

    Fetches up to ``limit`` untagged articles, applies rule-based tagging
    (teams, drivers, topics), saves tags to MongoDB, and re-indexes into
    Elasticsearch.
    """
    return await run_tagging_pipeline(limit=limit)


@router.post("/llm/pipeline")
async def trigger_full_pipeline(limit: int = 50) -> PipelineFullResult:
    """Trigger the full pipeline (summary + translation + tagging) manually.

    Runs the English summary pipeline first, then the Korean translation
    pipeline, then the auto-tagging pipeline sequentially.
    """
    return await run_full_pipeline(limit=limit)


@router.get("/tags")
async def get_all_tags() -> dict[str, list[str]]:
    """Return all unique tags, teams, and drivers from the articles collection."""
    return await ArticleRepository.get_distinct_tags()
