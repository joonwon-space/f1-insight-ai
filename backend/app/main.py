import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import router as api_router
from app.core.database import close_mongodb, connect_mongodb
from app.core.elasticsearch import close_elasticsearch, connect_elasticsearch
from app.scheduler.service import start_scheduler, stop_scheduler
from app.services.db_indexes import ensure_indexes
from app.services.repository import MasterDataRepository

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
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
    await MasterDataRepository.ensure_master_data()
    logger.info("Database indexes and master data initialized")
    await start_scheduler()

    yield

    # Shutdown
    logger.info("Shutting down F1 Insight AI backend...")
    await stop_scheduler()
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
