"""Dynamic scheduler service for F1 scraping.

Uses APScheduler to run scraping jobs at different frequencies depending on
whether a race weekend is in progress. Checks session info every 30 minutes
and switches between NORMAL (twice daily) and RACE_WEEKEND (every 10 min) modes.
"""

import logging
from datetime import datetime, timedelta, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.scheduler.models import SchedulerMode, SchedulerStatus
from app.scraper.service import ScraperService
from app.services.schedule import get_current_session_info

logger = logging.getLogger(__name__)

# Job IDs
_SCRAPE_JOB_ID = "scrape_articles"
_MODE_CHECK_JOB_ID = "check_scheduler_mode"

# Module-level state
_scheduler: AsyncIOScheduler | None = None
_current_mode: SchedulerMode = SchedulerMode.NORMAL
_last_run_time: datetime | None = None


async def _run_scrape_job() -> None:
    """Execute a single scraping run and log results."""
    global _last_run_time
    logger.info("Scrape job started (mode=%s)", _current_mode)

    scraper = ScraperService()
    try:
        articles = await scraper.scrape_all()
        _last_run_time = datetime.now(tz=timezone.utc)
        logger.info("Scrape job completed: %d new articles collected", len(articles))
    except Exception:
        logger.error("Scrape job failed", exc_info=True)
    finally:
        await scraper.close()


def _apply_mode(mode: SchedulerMode) -> None:
    """Add or replace the scrape job with the appropriate trigger for the given mode.

    NORMAL mode: cron trigger at 08:00 and 20:00 UTC.
    RACE_WEEKEND mode: interval trigger every 10 minutes.
    """
    global _current_mode
    if _scheduler is None:
        return

    # Remove existing scrape job if present
    existing = _scheduler.get_job(_SCRAPE_JOB_ID)
    if existing is not None:
        _scheduler.remove_job(_SCRAPE_JOB_ID)

    if mode == SchedulerMode.RACE_WEEKEND:
        _scheduler.add_job(
            _run_scrape_job,
            trigger="interval",
            minutes=10,
            id=_SCRAPE_JOB_ID,
            name="Scrape articles (race weekend)",
            replace_existing=True,
        )
    else:
        _scheduler.add_job(
            _run_scrape_job,
            trigger="cron",
            hour="8,20",
            id=_SCRAPE_JOB_ID,
            name="Scrape articles (normal)",
            replace_existing=True,
        )

    _current_mode = mode
    logger.info("Scheduler mode set to %s", mode.value)


async def _check_and_update_mode() -> None:
    """Evaluate the current F1 session state and switch mode if needed.

    Switches to RACE_WEEKEND mode when:
    - A session is currently in progress, OR
    - The next session starts within 2 hours.

    Otherwise stays in / reverts to NORMAL mode.
    """
    try:
        info = await get_current_session_info()
    except Exception:
        logger.error("Failed to fetch session info for mode check", exc_info=True)
        return

    should_be_race_mode = False

    # Session in progress
    if info.current_session is not None:
        should_be_race_mode = True

    # Next session within 2 hours
    if info.next_session is not None:
        now = datetime.now(tz=timezone.utc)
        time_until = info.next_session.start_time - now
        if time_until <= timedelta(hours=2):
            should_be_race_mode = True

    desired = SchedulerMode.RACE_WEEKEND if should_be_race_mode else SchedulerMode.NORMAL

    if desired != _current_mode:
        logger.info("Mode transition: %s -> %s", _current_mode.value, desired.value)
        _apply_mode(desired)


async def start_scheduler() -> None:
    """Initialize and start the APScheduler."""
    global _scheduler

    _scheduler = AsyncIOScheduler(timezone="UTC")

    # Periodic mode-check job (every 30 min)
    _scheduler.add_job(
        _check_and_update_mode,
        trigger="interval",
        minutes=30,
        id=_MODE_CHECK_JOB_ID,
        name="Check scheduler mode",
        replace_existing=True,
    )

    # Set initial scraping mode
    _apply_mode(SchedulerMode.NORMAL)

    _scheduler.start()
    logger.info("Scheduler started")

    # Run an initial mode check to pick up any in-progress race weekend
    await _check_and_update_mode()


async def stop_scheduler() -> None:
    """Shut down the scheduler gracefully."""
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped")
        _scheduler = None


def get_scheduler_status() -> SchedulerStatus:
    """Return the current scheduler status."""
    if _scheduler is None:
        return SchedulerStatus()

    next_run: datetime | None = None
    scrape_job = _scheduler.get_job(_SCRAPE_JOB_ID)
    if scrape_job is not None and scrape_job.next_run_time is not None:
        next_run = scrape_job.next_run_time

    return SchedulerStatus(
        mode=_current_mode,
        is_running=_scheduler.running,
        next_run_time=next_run,
        last_run_time=_last_run_time,
        job_count=len(_scheduler.get_jobs()),
    )
