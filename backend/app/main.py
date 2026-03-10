import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import images, news, schedule, search, teams
from app.api.router import router as api_router
from app.core.config import settings
from app.core.database import close_mongodb, connect_mongodb
from app.core.elasticsearch import close_elasticsearch, connect_elasticsearch
from app.core.logging import setup_logging
from app.scheduler.service import start_scheduler, stop_scheduler
from app.services.db_indexes import ensure_indexes
from app.services.es_indexes import ensure_es_indexes
from app.services.repository import MasterDataRepository
from app.services.sync import start_sync, stop_sync

setup_logging(json_logs=settings.json_logs)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Manage application startup and shutdown."""
    # Startup
    logger.info("Starting F1 Insight AI backend...")
    await connect_mongodb()
    await connect_elasticsearch()
    logger.info("All connections established")
    await ensure_indexes()
    await ensure_es_indexes()
    await MasterDataRepository.ensure_master_data()
    logger.info("Database indexes and master data initialized")
    await start_sync()
    await start_scheduler()

    yield

    # Shutdown
    logger.info("Shutting down F1 Insight AI backend...")
    await stop_scheduler()
    await stop_sync()
    await close_elasticsearch()
    await close_mongodb()
    logger.info("All connections closed")


app = FastAPI(
    title="F1 Insight AI",
    description="F1 news collection, LLM summarization & translation API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
app.include_router(news.router)
app.include_router(search.router)
app.include_router(schedule.router)
app.include_router(teams.router)
app.include_router(images.router)
